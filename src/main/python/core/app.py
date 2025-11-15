"""
Main FastAPI application for Citizen Urban Planning Participation System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 使用絕對導入以支持測試環境
try:
    # 當作為模組導入時使用相對導入
    from ..api import auth, opinions, notifications, moderation, media, categories
except ImportError:
    # 當作為獨立腳本或測試時使用絕對導入
    from ..api import auth, opinions, notifications, moderation, media, categories

# Create FastAPI app
app = FastAPI(
    title="Citizen Urban Planning Participation System",
    description="API for citizen participation in urban planning",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(opinions.router)
app.include_router(categories.router)
app.include_router(notifications.router)
app.include_router(moderation.router)
app.include_router(media.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Citizen Urban Planning Participation System API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
