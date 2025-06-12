import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn
from backend.config import settings
from mcp_server.protocol import MCPProtocol, MCPMessage
from mcp_server.search_service import SearchService
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Server - Streamable HTTP", version="0.1.0")
protocol = MCPProtocol()
search_service = SearchService()

# Session管理（可选）
sessions: Dict[str, Dict[str, Any]] = {}

# 定义工具列表
TOOLS = [
    {
        "name": "search_prompts",
        "description": "搜索prompt模板，支持按标题、标签和内容搜索",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "search_in": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "搜索范围：title, tags, content",
                    "default": ["title", "tags", "content"],
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_prompt_names",
        "description": "获取所有可用的prompt名称列表",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_prompt_by_title",
        "description": "根据标题获取具体的prompt内容",
        "inputSchema": {
            "type": "object",
            "properties": {"title": {"type": "string", "description": "prompt标题"}},
            "required": ["title"],
        },
    },
    {
        "name": "list_prompts_by_tag",
        "description": "列出指定标签的所有prompts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "按标签过滤，留空返回所有prompts",
                }
            },
            "required": [],
        },
    },
]


# MCP方法处理器
async def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理初始化请求"""
    client_info = params.get("clientInfo", {})
    logger.info(f"Initializing for client: {client_info.get('name', 'unknown')}")

    return {
        "protocolVersion": "2024-11-05",
        "serverInfo": {"name": "prompt-management-mcp", "version": "1.0.0"},
        "capabilities": {
            "tools": {},  # 声明支持工具
            # 不声明不支持的功能
        },
    }


async def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理工具列表请求"""
    return {"tools": TOOLS}


async def handle_tools_call(params: Dict[str, Any]) -> Any:
    """处理工具调用请求"""
    tool_name = params.get("name")
    tool_args = params.get("arguments", {})

    logger.info(f"Tool call: {tool_name} with args: {json.dumps(tool_args)}")

    try:
        if tool_name == "search_prompts":
            results = await search_service.search_prompts(tool_args)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"results": results}, ensure_ascii=False, indent=2
                        ),
                    }
                ]
            }

        elif tool_name == "get_prompt_names":
            names = await search_service.get_prompt_names(tool_args)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"names": names}, ensure_ascii=False, indent=2
                        ),
                    }
                ]
            }

        elif tool_name == "get_prompt_by_title":
            prompt = await search_service.get_prompt(tool_args)
            if prompt:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"prompt": prompt}, ensure_ascii=False, indent=2
                            ),
                        }
                    ]
                }
            else:
                return {
                    "content": [{"type": "text", "text": "Prompt not found"}],
                    "isError": True,
                }

        elif tool_name == "list_prompts_by_tag":
            prompts = await search_service.list_prompts(tool_args)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"prompts": prompts}, ensure_ascii=False, indent=2
                        ),
                    }
                ]
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True,
        }


# 注册处理器
protocol.register_handler("initialize", handle_initialize)
protocol.register_handler("tools/list", handle_tools_list)
protocol.register_handler("tools/call", handle_tools_call)


@app.post("/mcp")
async def handle_mcp_post(
    request: Request,
    accept: Optional[str] = Header(None),
    mcp_session_id: Optional[str] = Header(None),
    origin: Optional[str] = Header(None),
):
    """
    处理MCP POST请求 - Streamable HTTP协议的核心
    按照规范：https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http
    """

    # 安全检查：验证Origin头
    if origin and not _is_allowed_origin(origin):
        return JSONResponse(status_code=403, content={"error": "Forbidden origin"})

    # 检查Accept头
    if accept and not any(
        ct in accept for ct in ["application/json", "text/event-stream", "*/*"]
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Accept header must include application/json or text/event-stream"
            },
        )

    try:
        # 读取请求体
        body = await request.json()
        logger.info(
            f"MCP POST request: {json.dumps(body) if isinstance(body, dict) else f'Batch of {len(body)} messages'}"
        )

        # 判断是否为批量请求
        is_batch = isinstance(body, list)
        messages = body if is_batch else [body]

        # 检查是否包含请求（有id的消息）
        has_requests = any(msg.get("id") is not None for msg in messages)

        # 如果只包含响应或通知（没有id），返回202
        if not has_requests:
            logger.info("No requests in body, returning 202 Accepted")
            return Response(status_code=202)

        # 处理所有消息
        responses = []
        session_id = mcp_session_id

        for message in messages:
            if message.get("id") is not None:  # 只处理请求
                response = await protocol.handle_message(message)
                if response:
                    # 特殊处理初始化请求
                    if message.get("method") == "initialize" and not session_id:
                        session_id = str(uuid.uuid4())
                        sessions[session_id] = {
                            "created_at": asyncio.get_event_loop().time(),
                            "client_info": message.get("params", {}).get(
                                "clientInfo", {}
                            ),
                        }
                        logger.info(f"Created new session: {session_id}")

                    responses.append(response.to_dict())

        # 根据Accept头决定响应格式
        use_sse = accept and "text/event-stream" in accept

        if use_sse and responses:
            # 返回SSE流
            async def generate_sse():
                for response in responses:
                    event_data = json.dumps(response)
                    yield {
                        "event": "message",
                        "data": event_data,
                        "id": str(uuid.uuid4()),
                    }

            headers = {}
            if session_id:
                headers["Mcp-Session-Id"] = session_id

            return EventSourceResponse(generate_sse(), headers=headers)
        else:
            # 返回JSON
            headers = {}
            if session_id:
                headers["Mcp-Session-Id"] = session_id

            # 单个请求返回单个响应，批量请求返回数组
            content = (
                responses[0] if not is_batch and len(responses) == 1 else responses
            )

            return JSONResponse(content=content, headers=headers)

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None,
            },
        )
    except Exception as e:
        logger.error(f"Error in MCP POST: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": None,
            },
        )


@app.get("/mcp")
async def handle_mcp_get(
    request: Request,
    accept: Optional[str] = Header(None),
    mcp_session_id: Optional[str] = Header(None),
    last_event_id: Optional[str] = Header(None),
):
    """
    处理MCP GET请求 - 用于服务器主动推送消息（可选功能）
    """

    # 必须包含text/event-stream
    if not accept or "text/event-stream" not in accept:
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed - GET requires Accept: text/event-stream"
            },
        )

    # 验证session（如果提供）
    if mcp_session_id and mcp_session_id not in sessions:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    async def event_stream():
        """生成SSE事件流"""
        try:
            event_id = 0

            # 处理断线重连
            if last_event_id:
                try:
                    event_id = int(last_event_id) + 1
                except ValueError:
                    event_id = 0

            while True:
                # 每30秒发送心跳
                yield {
                    "event": "ping",
                    "data": json.dumps(
                        {"type": "ping", "timestamp": asyncio.get_event_loop().time()}
                    ),
                    "id": str(event_id),
                }
                event_id += 1

                await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("SSE connection closed")
            raise

    return EventSourceResponse(event_stream())


@app.delete("/mcp")
async def handle_mcp_delete(mcp_session_id: Optional[str] = Header(None)):
    """
    处理session终止请求（可选功能）
    """
    if not mcp_session_id:
        return JSONResponse(
            status_code=400, content={"error": "Mcp-Session-Id header required"}
        )

    if mcp_session_id in sessions:
        del sessions[mcp_session_id]
        logger.info(f"Deleted session: {mcp_session_id}")
        return Response(status_code=204)
    else:
        return JSONResponse(status_code=404, content={"error": "Session not found"})


def _is_allowed_origin(origin: str) -> bool:
    """检查是否允许的来源（安全措施）"""
    allowed_origins = [
        "http://localhost",
        "http://127.0.0.1",
        "https://localhost",
        "https://127.0.0.1",
        "app://",  # Electron应用
    ]
    return any(origin.startswith(ao) for ao in allowed_origins)


@app.get("/")
async def root():
    """根路径信息"""
    return {
        "implementation": "prompt-management-mcp-server",
        "version": "1.0.0",
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
        "protocol_version": "2024-11-05",
        "tools_count": len(TOOLS),
        "capabilities": ["tools"],
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "transport": "streamable-http",
        "sessions": len(sessions),
    }


# CORS中间件
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting MCP Server with Streamable HTTP Transport")
    logger.info(f"Server: http://127.0.0.1:{settings.MCP_SERVER_PORT}")
    logger.info(f"MCP Endpoint: http://127.0.0.1:{settings.MCP_SERVER_PORT}/mcp")
    logger.info(f"Protocol: Streamable HTTP (2024-11-05)")
    logger.info(f"Tools: {len(TOOLS)}")
    logger.info("=" * 60)

    # 只绑定到localhost以提高安全性
    uvicorn.run(app, host="127.0.0.1", port=settings.MCP_SERVER_PORT, log_level="info")
