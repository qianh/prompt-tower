import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MCPMessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


@dataclass
class MCPMessage:
    """MCP消息格式"""

    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {"jsonrpc": self.jsonrpc}

        # 只包含非None的字段
        if self.id is not None:
            data["id"] = self.id
        if self.method is not None:
            data["method"] = self.method
        if self.params is not None:
            data["params"] = self.params
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error

        return data

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())


class MCPProtocol:
    """MCP协议处理器"""

    def __init__(self):
        self.handlers = {}
        # 注册内置方法
        self.register_handler("initialize", self._handle_initialize)
        self.register_handler("initialized", self._handle_initialized)
        self.register_handler("shutdown", self._handle_shutdown)

    def register_handler(self, method: str, handler):
        """注册方法处理器"""
        self.handlers[method] = handler
        logger.info(f"Registered handler for method: {method}")

    async def handle_message(self, message: Dict[str, Any]) -> Optional[MCPMessage]:
        """处理MCP消息"""
        # 验证JSON-RPC格式
        if message.get("jsonrpc") != "2.0":
            return MCPMessage(
                id=message.get("id"),
                error={
                    "code": -32600,
                    "message": "Invalid Request: missing or invalid jsonrpc field",
                },
            )

        method = message.get("method")
        if not method:
            return MCPMessage(
                id=message.get("id"),
                error={
                    "code": -32600,
                    "message": "Invalid Request: missing method field",
                },
            )

        if method not in self.handlers:
            logger.warning(f"Method not found: {method}")
            return MCPMessage(
                id=message.get("id"),
                error={"code": -32601, "message": f"Method not found: {method}"},
            )

        try:
            params = message.get("params", {})
            result = await self.handlers[method](params)

            # 如果是通知（没有id），不返回响应
            if message.get("id") is None:
                return None

            return MCPMessage(id=message.get("id"), result=result)
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}")
            return MCPMessage(
                id=message.get("id"),
                error={"code": -32603, "message": f"Internal error: {str(e)}"},
            )

    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {"name": "Prompt Management MCP Server", "version": "0.1.0"},
            "capabilities": {"search": True, "list": True},
        }

    async def _handle_initialized(self, params: Dict[str, Any]) -> None:
        """处理初始化完成通知"""
        logger.info("MCP client initialized")
        return None

    async def _handle_shutdown(self, params: Dict[str, Any]) -> None:
        """处理关闭请求"""
        logger.info("MCP shutdown requested")
        return None
