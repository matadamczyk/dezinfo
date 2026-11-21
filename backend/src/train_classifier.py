import json
from pathlib import Path
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class TweetDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer, max_length: int = 128):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def load_dataset_splits(data_path: Path) -> tuple[list[str], list[int], list[str], list[int]]:
    with open(data_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    train_texts = [item["text"] for item in data if item.get("split") == "train"]
    train_labels = [1 if item.get("is_toxic") else 0 for item in data if item.get("split") == "train"]
    test_texts = [item["text"] for item in data if item.get("split") == "test"]
    test_labels = [1 if item.get("is_toxic") else 0 for item in data if item.get("split") == "test"]
    return train_texts, train_labels, test_texts, test_labels


def train_toxicity_classifier(
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    model_name: str = "allegro/herbert-base-cased",
) -> dict:
    device = get_device()
    root_dir = Path(__file__).resolve().parent.parent.parent
    data_path = root_dir / "data" / "poleval_tweets.json"
    models_dir = root_dir / "backend" / "models"
    classifier_dir = models_dir / "toxicity_classifier"
    metrics_path = models_dir / "classifier_metrics.json"

    train_texts, train_labels, test_texts, test_labels = load_dataset_splits(data_path)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    train_dataset = TweetDataset(train_texts, train_labels, tokenizer)
    test_dataset = TweetDataset(test_texts, test_labels, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    negative_count = train_labels.count(0)
    positive_count = train_labels.count(1)
    class_weights = torch.tensor(
        [1.0, negative_count / positive_count],
        dtype=torch.float,
        device=device,
    )
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)

    train_losses = []
    val_losses = []
    val_f1_scores = []
    history = []

    best_val_f1 = -1.0
    best_model_state = None

    for epoch in range(1, epochs + 1):
        model.train()
        running_train_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = loss_fn(outputs.logits, labels)
            loss.backward()
            optimizer.step()
            running_train_loss += loss.item()

        epoch_train_loss = running_train_loss / len(train_loader)
        train_losses.append(round(epoch_train_loss, 4))

        model.eval()
        running_val_loss = 0.0
        epoch_preds = []
        epoch_targets = []
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                loss = loss_fn(outputs.logits, labels)
                running_val_loss += loss.item()
                preds = torch.argmax(outputs.logits, dim=1).cpu().tolist()
                epoch_preds.extend(preds)
                epoch_targets.extend(labels.cpu().tolist())

        epoch_val_loss = running_val_loss / len(test_loader)
        epoch_val_f1 = f1_score(epoch_targets, epoch_preds, pos_label=1)
        val_losses.append(round(epoch_val_loss, 4))
        val_f1_scores.append(round(epoch_val_f1, 4))

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "val_loss": round(epoch_val_loss, 4),
            "val_f1": round(epoch_val_f1, 4),
        }
        history.append(epoch_record)

        if epoch_val_f1 > best_val_f1:
            best_val_f1 = epoch_val_f1
            best_model_state = {k: v.cpu() for k, v in model.state_dict().items()}

    if best_model_state is not None:
        model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})

    model.eval()
    final_preds = []
    final_targets = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1).cpu().tolist()
            final_preds.extend(preds)
            final_targets.extend(labels.cpu().tolist())

    report = classification_report(
        final_targets,
        final_preds,
        target_names=["non-toxic", "toxic"],
        output_dict=True,
    )
    matrix = confusion_matrix(final_targets, final_preds).tolist()
    final_f1 = f1_score(final_targets, final_preds, pos_label=1)
    final_precision = precision_score(final_targets, final_preds, pos_label=1)
    final_recall = recall_score(final_targets, final_preds, pos_label=1)
    final_accuracy = accuracy_score(final_targets, final_preds)

    models_dir.mkdir(parents=True, exist_ok=True)
    classifier_dir.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(classifier_dir)
    tokenizer.save_pretrained(classifier_dir)

    metrics_payload = {
        "model_name": model_name,
        "device": str(device),
        "epochs": list(range(1, epochs + 1)),
        "train_loss": train_losses,
        "val_loss": val_losses,
        "val_f1": val_f1_scores,
        "history": history,
        "final_metrics": {
            "f1_score": round(final_f1, 4),
            "precision": round(final_precision, 4),
            "recall": round(final_recall, 4),
            "accuracy": round(final_accuracy, 4),
        },
        "classification_report": report,
        "confusion_matrix": matrix,
    }

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, ensure_ascii=False, indent=2)

    return metrics_payload


if __name__ == "__main__":
    train_toxicity_classifier()
