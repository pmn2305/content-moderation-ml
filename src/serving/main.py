import httpx
import asyncio
import redis
import hashlib
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi import HTTPException, Request, Form
from fastapi import UploadFile, File
from src.serving.schemas import ModerateRequest, ModerateResponse
from src.serving.decision import make_decision
from src.serving.metrics import metrics

app = FastAPI(title="Content Moderation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite dev server
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

INFERENCE_BASE_URL = "http://localhost:8001"

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("moderation-api")


# ---------------- REDIS SAFE WRAPPERS ----------------

def safe_redis_incr(key: str):
    try:
        return redis_client.incr(key)
    except Exception:
        logger.warning("REDIS_UNAVAILABLE | incr")
        return None

def safe_redis_expire(key: str, seconds: int):
    try:
        redis_client.expire(key, seconds)
    except Exception:
        logger.warning("REDIS_UNAVAILABLE | expire")

def safe_redis_get(key: str):
    try:
        return redis_client.get(key)
    except Exception:
        logger.warning("REDIS_UNAVAILABLE | get")
        return None

def safe_redis_setex(key: str, seconds: int, value: str):
    try:
        redis_client.setex(key, seconds, value)
    except Exception:
        logger.warning("REDIS_UNAVAILABLE | setex")


# ----------------------------------------------------

def hash_str(value: str | None) -> str:
    if not value:
        return "none"
    return hashlib.sha256(value.encode()).hexdigest()

def rate_limit_key(ip: str) -> str:
    return f"rate:{ip}"

async def infer_text(text: str) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            f"{INFERENCE_BASE_URL}/infer/text",
            json={"text": text}
        )
        resp.raise_for_status()
        return resp.json()

async def infer_image(image_bytes: bytes | None, filename: str | None = None):
    if not image_bytes:
        return None

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            f"{INFERENCE_BASE_URL}/infer/image",
            files={
                "file": (filename or "image.jpg", image_bytes, "image/jpeg")
            }
        )
        resp.raise_for_status()
        return resp.json()

async def safe_infer(coro, model_name: str):
    try:
        return await coro
    except Exception as e:
        logger.error(
            f"INFERENCE_FAILED | model={model_name} | error={str(e)}"
        )
        return None

@app.post("/moderate", response_model=ModerateResponse)
async def moderate(
    text: str = Form(...),
    image: UploadFile = File(None),
    request: Request = None
):
    payload = ModerateRequest(text=text)
    start_time = time.time()
    metrics.inc("requests_total")

    image_bytes = None
    image_name = "uploaded.jpg"
    if image:
        image_bytes = await image.read()
        image_name = image.filename

    ip = request.client.host
    key = rate_limit_key(ip)

    count = safe_redis_incr(key)
    if count is not None:
        if count == 1:
            safe_redis_expire(key, 60)
        if count > 60:
            logger.warning(f"RATE_LIMIT_EXCEEDED | IP={ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    image_hash = hashlib.sha256(image_bytes).hexdigest() if image_bytes else "none"

    cache_key = (
        f"moderation:"
        f"{hash_str(payload.text)}:"
        f"{image_hash}"
    )

    cached = safe_redis_get(cache_key)

    if cached:
        metrics.inc("cache_hits")
        total_time = round(time.time() - start_time, 3)
        metrics.observe("request_latency_seconds", total_time)
        metrics.inc("request_success_total")
        logger.info(
            f"CACHE_HIT | ip={ip} | key={cache_key[:20]}s"
        )
        return ModerateResponse.model_validate_json(cached)

    metrics.inc("cache_misses")
    logger.info(
        f"CACHE_MISS | ip={ip} | key={cache_key[:20]}..."
    )

    text_result, image_result = await asyncio.gather(
        safe_infer(infer_text(payload.text), "text"),
        safe_infer(infer_image(image_bytes, image_name), "image")
    )

    text_score = text_result["score"] if text_result else None
    image_score = image_result["score"] if image_result else None

    infer_time = round(time.time() - start_time, 3)
    metrics.observe("inference_latency_seconds", infer_time)
    logger.info(
        f"INFERENCE_COMPLETED | IP={ip} | latency={infer_time}s"
    )

    decision = make_decision(text_score, image_score)

    response = ModerateResponse(
        decision=decision,
        scores={
            "text": text_score or 0.0,
            "image": image_score or 0.0,
        },
        model_versions={
            "text": text_result["model_version"] if text_result else "unavailable",
            "image": image_result["model_version"] if image_result else "unavailable",
        },
    )

    safe_redis_setex(cache_key, 300, response.model_dump_json())

    total_time = round(time.time() - start_time, 3)

    if text_result is None or image_result is None:
        metrics.inc("degraded_responses_total")
        logger.warning(
            f"DEGRADED_RESPONSE | ip={ip} | "
            f"text_ok={text_result is not None} | "
            f"image_ok={image_result is not None}"
        )

    metrics.observe("request_latency_seconds", total_time)
    metrics.inc("request_success_total")
    logger.info(
        f"REQUEST_COMPLETE | ip={ip} | decision={decision} | total_time={total_time}s"
    )

    return response

@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()
