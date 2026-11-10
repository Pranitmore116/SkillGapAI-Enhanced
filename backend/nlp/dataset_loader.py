"""
CSE472 Deep Learning for NLP - Module 4A: Skill NER Dataset Loader
Implements Unit V syllabus concepts:
- Dataset Preparation & Ingestion for Transformer Token Classification
- BIO Tagging Scheme Alignment (B-SKILL, I-SKILL, O)
- Subword (WordPiece) Tokenizer Alignment & Label Masking (-100)
- Train, Validation, and Test Dataset Splitting
"""

import os
import json
from typing import Dict, List, Any, Tuple, Optional


TAG2ID = {
    "O": 0,
    "B-SKILL": 1,
    "I-SKILL": 2
}

ID2TAG = {v: k for k, v in TAG2ID.items()}


class SkillDatasetLoader:
    """
    Loads and preprocesses BIO-annotated technical skill NER datasets.
    Complies with CSE472 Unit V token classification standards.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        default_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'annotated_skills_dataset.json')
        self.dataset_path = dataset_path or default_path
        self.data: Dict[str, Any] = {}
        self.load_dataset()

    def load_dataset(self) -> Dict[str, Any]:
        """Loads annotated JSON file from disk."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
            
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data

    def get_split(self, split_name: str = "train") -> List[Dict[str, Any]]:
        """Returns samples for 'train', 'validation', or 'test' split."""
        return self.data.get(split_name, [])

    def get_summary(self) -> Dict[str, Any]:
        """Computes academic distribution metrics across dataset splits."""
        train_samples = self.get_split("train")
        val_samples = self.get_split("validation")
        test_samples = self.get_split("test")

        def count_tags(samples):
            counts = {"O": 0, "B-SKILL": 0, "I-SKILL": 0, "total_entities": 0}
            for s in samples:
                for tag in s.get("tags", []):
                    counts[tag] = counts.get(tag, 0) + 1
                    if tag == "B-SKILL":
                        counts["total_entities"] += 1
            return counts

        return {
            "metadata": self.data.get("metadata", {}),
            "tag_scheme": list(TAG2ID.keys()),
            "tag2id": TAG2ID,
            "train_size": len(train_samples),
            "val_size": len(val_samples),
            "test_size": len(test_samples),
            "train_stats": count_tags(train_samples),
            "val_stats": count_tags(val_samples),
            "test_stats": count_tags(test_samples)
        }

    @staticmethod
    def align_labels_with_tokens(tokenizer, tokens: List[str], tags: List[str], max_length: int = 128) -> Tuple[Dict[str, Any], List[int]]:
        """
        Aligns WordPiece subword tokens with word-level BIO tags.
        Subword continuation pieces and special tokens are assigned label -100 (PyTorch ignore_index).
        """
        tokenized_inputs = tokenizer(
            tokens,
            is_split_into_words=True,
            max_length=max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        word_ids = tokenized_inputs.word_ids(batch_index=0)
        previous_word_idx = None
        label_ids = []

        for word_idx in word_ids:
            if word_idx is None:
                # Special tokens ([CLS], [SEP], [PAD]) ignored in loss
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                # First subword token of word receives original BIO tag
                tag_str = tags[word_idx] if word_idx < len(tags) else "O"
                label_ids.append(TAG2ID.get(tag_str, 0))
            else:
                # Subsequent subword continuation pieces assigned -100
                label_ids.append(-100)
            previous_word_idx = word_idx

        return tokenized_inputs, label_ids

