from transformers import pipeline
from PIL import Image

class ImageModerationModel:
    def __init__(self):
        self.pipe = pipeline(
            "image-classification",
            model="Falconsai/nsfw_image_detection"
        )
        self.model_version = "nsfw-vit-v1"

    def predict(self, image: Image.Image) -> float:
        """
        Expects a PIL.Image.Image object (already loaded & RGB).
        Returns NSFW confidence score.
        """
        outputs = self.pipe(image)
        print("model outputs:", outputs)

        NSFW_LABELS = {"porn", "sexy", "hentai", "nsfw"}

        for out in outputs:
            if out["label"].lower() in NSFW_LABELS:
                return float(out["score"])

        return 0.0
