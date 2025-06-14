from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth, llm, prompts, tags  # Added tags
from backend.config import settings

app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
)

from backend.services.tag_service import sync_tags_from_prompts  # Corrected import for startup event


# Startup event to sync tags
@app.on_event("startup")
async def startup_sync_tags():
    try:
        print("Application startup: Attempting to sync tags from prompts...")
        updated_tags = await sync_tags_from_prompts()
        print(f"Tag sync complete. Total global tags: {len(updated_tags)}")
    except Exception as e:
        print(f"Error during startup tag sync: {e}")


# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要修改
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(prompts.router, prefix=settings.API_PREFIX)
app.include_router(llm.router, prefix=settings.API_PREFIX)
app.include_router(auth.router)  # Auth routes typically don't have the /api/v1 prefix
app.include_router(tags.router, prefix=settings.API_PREFIX)  # Added tags router


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
