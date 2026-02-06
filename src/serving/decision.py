def mock_text_model(text: str) -> float:
    # Fake heuristic for now
    toxic_keywords = ["hate", "kill", "abuse"]
    return 0.9 if any(word in text.lower() for word in toxic_keywords) else 0.1


def mock_image_model(image_url: str) -> float:
    # Pretend image model
    return 0.2


def make_decision(text_score: float, image_score: float | None):
    scores=[]
    if text_score is not None:
        scores.append(text_score)
    if image_score is not None:
        scores.append(image_score)
    if not scores:
        return "REVIEW"
    if any(score > 0.8 for score in scores):
        return "REJECT"
    return "ALLOW"
