from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
	return {"status": "ok"}


@router.get("/echo")
def echo(q: str = "hello"):
	return {"echo": q}
