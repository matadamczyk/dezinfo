import re
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_model = None
_tokenizer = None
_device = None

POSITIVE_LEXICON = {
    "super", "świetnie", "świetny", "świetna", "świetne", "wspaniale", "wspaniały", "wspaniała", "wspaniałe",
    "dobry", "dobra", "dobre", "dobrze", "polecam", "sukces", "gratulacje", "brawo", "dziękuję",
    "dzięki", "pomoc", "pomocny", "wsparcie", "pozytywny", "pozytywna", "piękny", "piękna", "piękne",
    "warto", "popieram", "prawda", "rozwój", "kocham", "uwielbiam", "nadzieja", "radość",
    "rewelacja", "rewelacyjny", "genialny", "genialna", "plus", "zyski", "wzrost", "bezpieczeństwo",
    "zgoda", "pokój", "uczciwy", "uczciwość", "doskonały", "doskonale", "optymistyczny", "szczęście",
}

NEGATIVE_LEXICON = {
    "źle", "fatalnie", "fatalny", "fatalna", "porażka", "oszustwo", "oszust", "kłamstwo", "kłamca",
    "złodziej", "złodzieje", "afera", "hańba", "wstyd", "błąd", "patologia", "upadek", "katastrofa",
    "kryzys", "strata", "dno", "chamstwo", "bzdura", "groźba", "śmieć", "zdrada", "zdrajca",
    "dramat", "tragicznie", "tragiczny", "spadek", "manipulacja", "zbrodnia", "zbrodniarz",
    "nieudolność", "bezczelność", "oszukiwać", "kłamać", "kradzież", "zamach", "skandal", "szok",
    "cwaniak", "cwaniaków", "chciwość", "kompromitacja", "haniebny",
}

NEGATION_TERMS = {"nie", "bez", "ani", "brak", "żaden", "żadna", "żadne"}


def get_inference_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_model_and_tokenizer():
    global _model, _tokenizer, _device
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer, _device

    _device = get_inference_device()
    root_dir = Path(__file__).resolve().parent.parent.parent
    classifier_dir = root_dir / "backend" / "models" / "toxicity_classifier"

    has_saved_weights = (classifier_dir / "model.safetensors").exists() or (
        classifier_dir / "pytorch_model.bin"
    ).exists()
    model_source = str(classifier_dir) if has_saved_weights else "allegro/herbert-base-cased"

    _tokenizer = AutoTokenizer.from_pretrained(model_source)
    _model = AutoModelForSequenceClassification.from_pretrained(model_source, num_labels=2)
    _model.to(_device)
    _model.eval()
    return _model, _tokenizer, _device


def classify_sentiment(text: str, toxicity_score: float, is_toxic: bool) -> str:
    if is_toxic or toxicity_score >= 0.5:
        return "negative"

    tokens = re.findall(r"\b\w+\b", text.lower())
    positive_hits = 0
    negative_hits = 0

    for idx, token in enumerate(tokens):
        is_negated = any(
            tokens[prev_idx] in NEGATION_TERMS
            for prev_idx in range(max(0, idx - 2), idx)
        )
        if token in POSITIVE_LEXICON:
            if is_negated:
                negative_hits += 1
            else:
                positive_hits += 1
        elif token in NEGATIVE_LEXICON:
            if not is_negated:
                negative_hits += 1

    if positive_hits > negative_hits and toxicity_score < 0.35:
        return "positive"
    if negative_hits > positive_hits or toxicity_score >= 0.4:
        return "negative"
    return "neutral"


def analyze_style(text: str) -> dict:
    model, tokenizer, device = get_model_and_tokenizer()

    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    toxicity_score = float(probs[0][1].item())
    is_toxic = bool(toxicity_score >= 0.5)
    sentiment = classify_sentiment(text, toxicity_score, is_toxic)

    return {
        "sentiment": sentiment,
        "toxicity_score": round(toxicity_score, 4),
        "is_toxic": is_toxic,
    }
