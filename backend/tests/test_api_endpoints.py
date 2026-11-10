import pytest
import json
import sys
import os
import io

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "nlp_engine" in data
    assert data["nlp_engine"]["distilbert_available"] is True


def test_api_preprocess_endpoint(client):
    payload = {
        "text": "Senior Full-Stack Engineer with experience in C++, Python, and CI/CD pipelines."
    }
    response = client.post(
        "/api/nlp/preprocess",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["token_count"] > 0
    assert "c++" in [t.lower() for t in data["cleaned_tokens"]]
    assert "c++" in data["preserved_technical_terms"]
    assert "ngrams" in data


def test_api_tfidf_endpoint(client):
    payload = {
        "resume_text": "Experienced Python developer with Flask, Docker, and PostgreSQL experience.",
        "jd_text": "Looking for Python backend developer with Flask and PostgreSQL experience."
    }
    response = client.post(
        "/api/nlp/tfidf",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "cosine_similarity" in data
    assert "cosine_similarity_pct" in data
    assert data["cosine_similarity"] > 0.4
    assert len(data["shared_terms"]) > 0


def test_api_embeddings_visualize(client):
    response = client.get("/api/nlp/embeddings/visualize")
    assert response.status_code == 200
    data = response.get_json()
    assert "skills" in data
    assert len(data["skills"]) > 5
    first = data["skills"][0]
    assert "skill" in first
    assert "x" in first
    assert "y" in first
    assert "explained_variance" in data


def test_api_embeddings_similarity(client):
    payload = {
        "word1": "python",
        "word2": "java",
        "method": "word2vec"
    }
    response = client.post(
        "/api/nlp/embeddings/similarity",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "similarity" in data
    assert 0 <= data["similarity"] <= 1.0


def test_api_embeddings_analogy(client):
    payload = {
        "word_a": "javascript",
        "word_b": "web",
        "word_c": "data",
        "top_n": 3
    }
    response = client.post(
        "/api/nlp/embeddings/analogy",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data


def test_api_bert_model_info(client):
    response = client.get("/api/nlp/bert/model-info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["model_name"] == "distilbert-base-uncased"
    assert data["num_classes"] == 3


def test_api_bert_extract(client):
    payload = {
        "text": "I built a web service using Python, Flask, and PostgreSQL on AWS."
    }
    response = client.post(
        "/api/nlp/bert/extract",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "extracted_skills" in data
    assert "token_classifications" in data
    assert "inference_time_ms" in data


def test_api_unified_analyze(client):
    payload = {
        "resume_text": "Full stack engineer with Python, Flask, PostgreSQL, Docker, and AWS.",
        "jd_text": "We need a Python developer experienced with Flask, Docker, and Kubernetes."
    }
    response = client.post(
        "/api/nlp/unified-analyze",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "unified_score_pct" in data
    assert "approaches" in data
    assert "timing_ms" in data
    assert "rule_based" in data["approaches"]
    assert "tfidf_cosine" in data["approaches"]
    assert "word2vec_semantic" in data["approaches"]
    assert "bert_contextual" in data["approaches"]


def test_api_benchmark(client):
    response = client.get("/api/nlp/evaluation/benchmark")
    assert response.status_code == 200
    data = response.get_json()
    assert "benchmark_results" in data
    assert len(data["benchmark_results"]) == 5
    assert "summary" in data


def test_api_benchmark_samples(client):
    response = client.get("/api/nlp/benchmark-samples")
    assert response.status_code == 200
    data = response.get_json()
    assert "fullstack" in data
    assert "ml_engineer" in data


def test_api_extract_backward_compatibility(client):
    resume_bytes = b"Senior developer with 5 years experience in Python, React, Docker, and Git."
    data = {
        'file': (io.BytesIO(resume_bytes), 'test_resume.txt'),
        'jd_text': 'Looking for Python, React, and Kubernetes developer.'
    }
    response = client.post(
        "/api/extract",
        data=data,
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert "matched_skills" in res_data
    assert "missing_skills" in res_data
    assert "match_score" in res_data
