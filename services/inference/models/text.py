from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "unitary/toxic-bert"

class TextModerationModel:
    def __init__(self):
        self.version = "toxic-bert-v1"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()

    def predict(self, text: str) -> float:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.sigmoid(logits)

        # toxic-bert → single toxicity score
        return probs[0][0].item()
