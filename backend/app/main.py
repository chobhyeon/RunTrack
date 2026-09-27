"""
RunTrack Backend - FastAPI 주 애플리케이션
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import shoes, running, weather, users
from app.config import settings

# FastAPI 앱 초기화
app = FastAPI(
    title="RunTrack API",
    description="AI 기반 맞춤형 러닝 조언 앱",
    version="0.1.0"
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Do not echo submitted passwords, including malformed request bodies.
    errors = [
        {key: value for key, value in error.items() if key not in {"input", "ctx"}}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": errors}))

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(shoes.router, prefix="/api/shoes", tags=["Shoes"])
app.include_router(running.router, prefix="/api/running", tags=["Running"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])

@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "message": "RunTrack API is running",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """서버 상태 확인"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
