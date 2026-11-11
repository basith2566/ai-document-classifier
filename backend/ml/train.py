"""
Train the document classifier.

Run from the backend/ folder:
    python -m ml.train
    python -m ml.train --data path/to/your_data.csv

Adding a new category: add rows to the CSV with the new label name in the
`label` column (at least ~30 examples), then run this script again. The
categories are read from the data - no code changes needed.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from ml.preprocess import clean_text
from utils.config import settings

MIN_PER_CLASS = 10


def load_dataset(path: Path):
    if not path.exists():
        sys.exit(f"Dataset not found: {path}")
    texts, labels, seen = [], [], set()
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"text", "label"} <= set(reader.fieldnames):
            sys.exit("The CSV needs two columns named 'text' and 'label'.")
        for row in reader:
            text, label = (row["text"] or "").strip(), (row["label"] or "").strip()
            # Skip blanks and exact duplicates (duplicates would leak between train and test).
            if not text or not label or text in seen:
                continue
            seen.add(text)
            texts.append(text)
            labels.append(label)
    counts = {l: labels.count(l) for l in sorted(set(labels))}
    too_small = [l for l, c in counts.items() if c < MIN_PER_CLASS]
    if len(counts) < 2 or too_small:
        sys.exit(f"Need at least 2 categories with {MIN_PER_CLASS}+ examples each. Problem: {too_small or counts}")
    return texts, labels, counts


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    ngram_range=(1, 2),
                    stop_words="english",
                    sublinear_tf=True,
                    min_df=2,
                    max_df=0.9,
                    max_features=30000,
                ),
            ),
            ("clf", LogisticRegression(C=10, max_iter=2000, class_weight="balanced")),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the document classifier")
    parser.add_argument("--data", type=Path, default=settings.dataset_path)
    parser.add_argument("--out", type=Path, default=settings.model_path)
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    texts, labels, counts = load_dataset(args.data)
    print(f"Loaded {len(texts)} documents: {counts}")

    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=args.test_size, stratify=labels, random_state=42
    )
    print(f"Train: {len(x_train)}  Test: {len(x_test)}")

    pipeline = build_pipeline()

    # 5-fold cross-validation on the training portion only.
    n_splits = min(5, min(counts.values()))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    cv_scores = cross_val_score(build_pipeline(), x_train, y_train, cv=cv, scoring="accuracy")

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    classes = list(pipeline.classes_)

    report = classification_report(y_test, predictions, labels=classes, output_dict=True, zero_division=0)
    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset_file": args.data.name,
        "n_documents": len(texts),
        "n_train": len(x_train),
        "n_test": len(x_test),
        "class_counts": counts,
        "labels": classes,
        "test_accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "test_macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "cv_accuracy_mean": round(float(np.mean(cv_scores)), 4),
        "cv_accuracy_std": round(float(np.std(cv_scores)), 4),
        "per_class": {
            c: {k: round(report[c][k], 4) for k in ("precision", "recall", "f1-score")} | {"support": int(report[c]["support"])}
            for c in classes
        },
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=classes).tolist(),
        "sklearn_version": sklearn.__version__,
        "note": "Metrics come from a held-out test split of the training dataset. "
        "If the dataset is synthetic, real-world accuracy will be lower.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "labels": classes, "metrics": metrics}, args.out)
    metrics_path = args.out.with_name("metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("\n" + classification_report(y_test, predictions, labels=classes, zero_division=0))
    print(f"Test accuracy : {metrics['test_accuracy']:.3f}")
    print(f"Macro F1      : {metrics['test_macro_f1']:.3f}")
    print(f"CV accuracy   : {metrics['cv_accuracy_mean']:.3f} +/- {metrics['cv_accuracy_std']:.3f}")
    print(f"\nSaved model   -> {args.out}\nSaved metrics -> {metrics_path}")


if __name__ == "__main__":
    main()
