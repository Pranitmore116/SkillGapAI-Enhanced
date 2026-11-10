"""
Unit Tests for Module 4: BERT Contextual Skill Extractor (CSE472 Unit V)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.dataset_loader import SkillDatasetLoader, TAG2ID, ID2TAG
from nlp.bert_extractor import BertSkillExtractor


def test_dataset_loader_splits_and_bio_tags():
    loader = SkillDatasetLoader()
    summary = loader.get_summary()
    
    assert summary["train_size"] > 0
    assert summary["val_size"] > 0
    assert summary["test_size"] > 0
    assert "B-SKILL" in summary["tag_scheme"]
    assert "I-SKILL" in summary["tag_scheme"]
    assert "O" in summary["tag_scheme"]


def test_bert_extractor_inference():
    extractor = BertSkillExtractor()
    sample_text = "I developed a backend application using Python, Flask, PostgreSQL and AWS."
    
    entities = extractor.extract_skills_contextual(sample_text)
    
    assert isinstance(entities, list)
    entity_names = [e["entity"].lower() for e in entities]
    
    # Verify key skills are extracted
    assert any("python" in name for name in entity_names)
    assert any("flask" in name for name in entity_names)
    assert any("aws" in name for name in entity_names)
    
    # Check fields in extraction dictionary
    for ent in entities:
        assert "entity" in ent
        assert "confidence" in ent
        assert "context_sentence" in ent


def test_bert_evaluation_pipeline():
    extractor = BertSkillExtractor()
    eval_report = extractor.evaluate_model()
    
    assert "token_accuracy" in eval_report
    assert "confusion_matrix" in eval_report
    assert "entity_metrics" in eval_report
    assert "macro_f1" in eval_report

