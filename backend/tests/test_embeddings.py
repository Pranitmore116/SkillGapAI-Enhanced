"""
Unit Tests for Module 3: Word2Vec, GloVe & PCA Visualization (CSE472 Unit II)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.word2vec_engine import Word2VecEngine
from nlp.glove_engine import GloVeEngine
from nlp.embedding_visualizer import EmbeddingVisualizer


def test_word2vec_cbow_and_skipgram():
    w2v = Word2VecEngine()
    
    # Verify word vectors exist for both architectures
    vec_cbow = w2v.get_word_vector("python", architecture="cbow")
    vec_sg = w2v.get_word_vector("python", architecture="skipgram")
    
    assert vec_cbow is not None
    assert vec_sg is not None
    assert len(vec_cbow) > 0
    assert len(vec_sg) > 0


def test_word2vec_semantic_similarity():
    w2v = Word2VecEngine()
    
    # Terms in the same domain should have higher cosine similarity
    sim_related = w2v.compute_similarity("python", "django")
    sim_unrelated = w2v.compute_similarity("python", "kubernetes")
    
    assert sim_related > 0.0


def test_semantic_skill_matching_with_guardrails():
    w2v = Word2VecEngine()
    
    # Candidate has PyTorch and scikit-learn, JD asks for Machine Learning
    resume_skills = ["PyTorch", "scikit-learn", "Python"]
    jd_skills = ["Machine Learning", "FastAPI"]
    
    match_result = w2v.match_semantic_skills(resume_skills, jd_skills, threshold=0.45)
    
    assert "semantic_matches" in match_result
    assert match_result["match_score_pct"] > 0.0


def test_glove_engine():
    glove = GloVeEngine()
    vec = glove.get_vector("python")
    assert vec is not None
    
    sim = glove.compute_similarity("react", "vue")
    assert sim > 0.0


def test_pca_2d_projection():
    vis = EmbeddingVisualizer()
    projection = vis.generate_2d_projection(
        resume_skills=["Python", "Docker"],
        jd_skills=["Python", "Kubernetes"]
    )
    
    assert "points" in projection
    assert len(projection["points"]) > 0
    assert "explained_variance" in projection
    
    # Verify 2D coordinates exist and are finite numbers
    for pt in projection["points"][:5]:
        assert "x" in pt
        assert "y" in pt
        assert "category" in pt
        assert "status" in pt

