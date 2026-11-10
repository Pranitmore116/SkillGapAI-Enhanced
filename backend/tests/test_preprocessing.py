"""
Unit Tests for Module 1: Preprocessing Pipeline (CSE472 Unit I)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.preprocessing import TextPreprocessor


def test_technical_term_protection():
    preprocessor = TextPreprocessor()
    sample_text = "Looking for an engineer experienced in C++, C#, .NET, Node.js, and CI/CD."
    
    cleaned = preprocessor.clean_text(sample_text)
    
    # Assert technical terms are preserved and not destroyed by punctuation cleaning
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert ".net" in cleaned
    assert "node.js" in cleaned
    assert "ci/cd" in cleaned


def test_tokenization_and_spans():
    preprocessor = TextPreprocessor()
    sample_text = "Python developer with Docker and AWS experience."
    
    span_data = preprocessor.tokenize_with_spans(sample_text)
    tokens = [d["token"] for d in span_data]
    
    assert "python" in tokens
    assert "docker" in tokens
    assert "aws" in tokens
    assert len(span_data) > 0
    # Verify span character ranges
    for item in span_data:
        assert item["start"] <= item["end"]


def test_stopword_removal_whitelist():
    preprocessor = TextPreprocessor()
    tokens = ["the", "developer", "uses", "r", "and", "c", "for", "ai", "projects"]
    
    filtered, removed = preprocessor.remove_stopwords(tokens)
    
    # Assert standard stopwords removed
    assert "the" in removed
    assert "and" in removed
    assert "for" in removed
    
    # Assert single-letter/acronym skills on whitelist are NOT removed
    assert "r" in filtered
    assert "c" in filtered
    assert "ai" in filtered


def test_morphological_operations():
    preprocessor = TextPreprocessor()
    tokens = ["models", "predictive", "clustering", "developers", "python"]
    
    lemmatized = preprocessor.lemmatize_tokens(tokens)
    assert "model" in lemmatized or "models" in lemmatized
    
    stemmed = preprocessor.stem_tokens(tokens)
    assert len(stemmed) == len(tokens)


def test_ngrams():
    tokens = ["deep", "learning", "natural", "language", "processing"]
    
    unigrams = TextPreprocessor.generate_ngrams(tokens, 1)
    bigrams = TextPreprocessor.generate_ngrams(tokens, 2)
    trigrams = TextPreprocessor.generate_ngrams(tokens, 3)
    
    assert len(unigrams) == 5
    assert len(bigrams) == 4
    assert len(trigrams) == 3
    assert "deep learning" in bigrams
    assert "natural language processing" in trigrams


def test_end_to_end_document_processing():
    preprocessor = TextPreprocessor()
    text = "Engineered cloud microservices using Python, Docker, and Kubernetes on AWS."
    
    doc = preprocessor.process_document(text)
    
    assert "cleaned_text" in doc
    assert "tokens" in doc
    assert "lemmatized_tokens" in doc
    assert "top_terms" in doc
    assert doc["unigram_count"] > 0
    assert doc["bigram_count"] > 0

