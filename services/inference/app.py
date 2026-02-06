from fastapi import FastAPI
from pydantic import BaseModel
from services.inference.models.text import TextModerationModel
from services.inference.models.image import ImageModerationModel
from fastapi import UploadFile, File, HTTPException
from PIL import Image
import io

app = FastAPI(title="Inference Service")

text_model = TextModerationModel()
image_model = ImageModerationModel()


class TextRequest(BaseModel):
    text: str

@app.post("/infer/text")
def infer_text(req: TextRequest):
    
    if not req.text.strip():
        return {
            "score": 0.0,
            "model_version": "toxic-bert-v1"
        }
    score = text_model.predict(req.text)
    return {
        "score": round(score,3),
        "model_version": "toxic-bert-v1"
    }

@app.post("/infer/image")
async def infer_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    score = image_model.predict(image)

    return {
        "score": round(score, 3),
        "model_version": image_model.model_version
    }


@app.get("/health")
def health():
    return {"status": "ok"}
