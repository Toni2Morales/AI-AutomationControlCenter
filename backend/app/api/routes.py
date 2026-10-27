from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {
        "name": "AI Automation Control Center",
        "status": "ok",
        "message": "La API está funcionando.",
    }

@router.get("/health")
def health():
    return {"status": "ok"}
