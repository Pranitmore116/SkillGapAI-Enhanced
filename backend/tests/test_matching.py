"""
Unit Tests for Module 5 & 6: Unified NLP Matcher & Evaluation Dashboard
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.unified_matcher import UnifiedNLPMatcher
from nlp.model_evaluation import ModelEvaluator


def test_unified_matching_all_approaches():
    matcher = UnifiedNLPMatcher()
    resume = "Experienced software engineer with strong Python, React, Docker, and PostgreSQL skills."
    jd = "Seeking Full Stack Developer proficient in Python, React, Docker, and AWS."
    
    results = matcher.analyze_resume_and_jd(resume, jd)
    
    # Assert all four approaches are executed
    assert "approach_a_rule" in results
    assert "approach_b_tfidf" in results
    assert "approach_c_embeddings" in results
    assert "approach_d_bert" in results
    assert "unified_evaluation" in results
    
    # Assert latency metrics are recorded
    assert results["approach_a_rule"]["latency_ms"] >= 0.0
    assert results["approach_b_tfidf"]["latency_ms"] >= 0.0
    assert results["approach_c_embeddings"]["latency_ms"] >= 0.0
    assert results["approach_d_bert"]["latency_ms"] >= 0.0
    
    # Assert transparent unified score formulation
    unified = results["unified_evaluation"]
    assert 0.0 <= unified["unified_score_pct"] <= 100.0
    assert "formula" in unified


def test_model_evaluator_benchmark():
    evaluator = ModelEvaluator()
    report = evaluator.evaluate_all_methods()
    
    assert "comparison_table" in report
    assert len(report["comparison_table"]) == 5
    
    for row in report["comparison_table"]:
        assert "method" in row
        assert "precision" in row
        assert "recall" in row
        assert "f1" in row
        assert "latency_ms" in row
        assert "strengths" in row
        assert "limitations" in row

