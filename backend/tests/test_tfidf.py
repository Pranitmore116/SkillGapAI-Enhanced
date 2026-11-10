"""
Unit Tests for Module 2: TF-IDF and Cosine Similarity (CSE472 Unit I)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.bow_engine import BagOfWordsEngine
from nlp.tfidf_engine import TfidfEngine


def test_bow_engine_similarity():
    bow = BagOfWordsEngine()
    doc_a = "Python, machine learning, data science, pandas, numpy"
    doc_b = "Machine learning engineer with strong Python and pandas skills"
    
    result = bow.vectorize_pair(doc_a, doc_b)
    
    assert "similarity" in result
    assert result["similarity"] > 0.0
    assert result["overlap_count"] > 0
    assert "shared_vocabulary_size" in result


def test_tfidf_cosine_mathematics():
    tfidf = TfidfEngine()
    resume = "Experienced software developer in Python, React, Docker, and PostgreSQL."
    jd = "Seeking software engineer proficient in Python, Docker, Kubernetes, and PostgreSQL."
    
    result = tfidf.compute_similarity(resume, jd)
    
    # Cosine similarity must strictly be bounded in [0.0, 100.0]%
    assert 0.0 <= result["cosine_similarity_pct"] <= 100.0
    assert result["raw_cosine"] > 0.0
    assert result["dot_product"] > 0.0
    assert result["norm_resume"] > 0.0
    assert result["norm_jd"] > 0.0
    
    # Matched and missing term verification
    matched_names = [t["term"] for t in result["matched_terms"]]
    assert "python" in matched_names
    assert "docker" in matched_names
    assert "postgresql" in matched_names
    
    missing_names = [t["term"] for t in result["missing_terms"]]
    assert "kubernetes" in missing_names


def test_tfidf_empty_input():
    tfidf = TfidfEngine()
    result = tfidf.compute_similarity("", "Python developer")
    assert result["cosine_similarity_pct"] == 0.0

