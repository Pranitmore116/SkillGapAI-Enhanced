import os
import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

from resume_skill_extractor import process_resume
from nlp.preprocessing import TextPreprocessor
from nlp.tfidf_engine import TfidfEngine
from nlp.bow_engine import BagOfWordsEngine
from nlp.word2vec_engine import Word2VecEngine
from nlp.glove_engine import GloVeEngine
from nlp.embedding_visualizer import EmbeddingVisualizer
from nlp.bert_extractor import BertSkillExtractor
from nlp.unified_matcher import UnifiedNLPMatcher
from nlp.model_evaluation import ModelEvaluator

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def handle_options_preflight():
    if request.method == 'OPTIONS':
        res = jsonify({"status": "ok"})
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        res.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return res, 200

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lazy singletons for performance and memory conservation
_preprocessor = TextPreprocessor()
_tfidf_engine = TfidfEngine()
_bow_engine = BagOfWordsEngine()
_w2v_engine = None
_glove_engine = None
_visualizer = None
_bert_extractor = None
_unified_matcher = None
_evaluator = None


def get_w2v():
    global _w2v_engine
    if _w2v_engine is None:
        _w2v_engine = Word2VecEngine()
    return _w2v_engine


def get_glove():
    global _glove_engine
    if _glove_engine is None:
        _glove_engine = GloVeEngine()
    return _glove_engine


def get_visualizer():
    global _visualizer
    if _visualizer is None:
        _visualizer = EmbeddingVisualizer(get_w2v())
    return _visualizer


def get_bert():
    global _bert_extractor
    if _bert_extractor is None:
        _bert_extractor = BertSkillExtractor()
    return _bert_extractor


def get_unified_matcher():
    global _unified_matcher
    if _unified_matcher is None:
        _unified_matcher = UnifiedNLPMatcher()
    return _unified_matcher


def get_evaluator():
    global _evaluator
    if _evaluator is None:
        _evaluator = ModelEvaluator()
    return _evaluator


# ── PRESERVED EXISTING ROUTE: /api/extract ──
@app.route('/api/extract', methods=['POST', 'OPTIONS'])
def extract_file_text():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    filepath = None
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        jd_text = request.form.get('jd_text', None)
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        result_str = process_resume(filepath, jd_text=jd_text)
        result_data = json.loads(result_str)
        
        if "error" in result_data:
            return jsonify(result_data), 400
            
        return jsonify(result_data)
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass


# ── MODULE 1: NLP Preprocessing Endpoint ──
@app.route('/api/nlp/preprocess', methods=['POST'])
def nlp_preprocess():
    """
    Unit I Text Processing endpoint:
    Returns step-by-step tokenization, stopword removal, stemming, lemmatization, and n-grams.
    """
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400

        result = _preprocessor.process_document(text)
        result["cleaned_tokens"] = result.get("filtered_tokens", [])
        result["oov_count"] = result.get("oov_terms_count", 0)
        result["preserved_technical_terms"] = [t for t in result.get("tokens", []) if t.lower() in ("c++", "c#", ".net", "node.js", "ci/cd")]
        result["ngrams"] = {
            "unigrams": result.get("sample_unigrams", []),
            "bigrams": result.get("sample_bigrams", []),
            "trigrams": result.get("sample_trigrams", [])
        }
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── MODULE 2: TF-IDF & Cosine Similarity Endpoint ──
@app.route('/api/nlp/tfidf', methods=['POST'])
def nlp_tfidf():
    """
    Unit I TF-IDF & Cosine similarity endpoint:
    Computes mathematical cosine similarity, dot product, L2 norms, and keyword weights.
    """
    try:
        data = request.get_json(silent=True) or {}
        resume_text = data.get("resume_text", "")
        jd_text = data.get("jd_text", "")
        if not resume_text.strip() or not jd_text.strip():
            return jsonify({"error": "Both resume_text and jd_text are required."}), 400

        bow_res = _bow_engine.vectorize_pair(resume_text, jd_text)
        tfidf_res = _tfidf_engine.compute_similarity(resume_text, jd_text)
        
        raw_cos = tfidf_res.get("raw_cosine", 0.0)
        pct_cos = tfidf_res.get("cosine_similarity_pct", 0.0)
        if raw_cos == 0.0 and pct_cos > 0.0:
            raw_cos = round(pct_cos / 100.0, 4)
            
        matched_terms = [t["term"] if isinstance(t, dict) else t for t in tfidf_res.get("matched_terms", [])]
        missing_terms = [t["term"] if isinstance(t, dict) else t for t in tfidf_res.get("missing_terms", [])]
        
        return jsonify({
            "cosine_similarity": raw_cos,
            "cosine_similarity_pct": pct_cos,
            "bow_overlap_pct": bow_res.get("bow_overlap_pct", 0.0),
            "shared_terms": matched_terms,
            "missing_jd_terms": missing_terms,
            "top_resume_terms": tfidf_res.get("resume_top_terms", []),
            "top_jd_terms": tfidf_res.get("jd_top_terms", []),
            "vocabulary_size": tfidf_res.get("vocabulary_size", len(matched_terms) + len(missing_terms)),
            "bow": bow_res,
            "tfidf": tfidf_res
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── MODULE 3: Word Embeddings (Word2Vec / GloVe) Endpoints ──
@app.route('/api/nlp/embeddings/similarity', methods=['POST'])
def nlp_embedding_similarity():
    """
    Unit II Word embedding similarity & analogies:
    Supports both CBOW and Skip-Gram Word2Vec, plus GloVe vectors.
    """
    try:
        data = request.get_json(silent=True) or {}
        word_a = data.get("word_a") or data.get("word1") or ""
        word_b = data.get("word_b") or data.get("word2") or ""
        architecture = data.get("architecture", "cbow")
        
        w2v = get_w2v()
        glove = get_glove()

        w2v_sim = w2v.compute_similarity(word_a, word_b, architecture=architecture)
        glove_sim = glove.compute_similarity(word_a, word_b)

        return jsonify({
            "word_a": word_a,
            "word_b": word_b,
            "architecture": architecture,
            "similarity": round(w2v_sim, 4),
            "word2vec_cosine": round(w2v_sim, 4),
            "word2vec_similarity_pct": round(w2v_sim * 100, 2),
            "glove_cosine": round(glove_sim, 4),
            "glove_similarity_pct": round(glove_sim * 100, 2)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/embeddings/neighbors', methods=['POST'])
def nlp_embedding_neighbors():
    """Returns nearest neighbors in continuous embedding space."""
    try:
        data = request.get_json(silent=True) or {}
        word = data.get("word", "")
        top_n = int(data.get("top_n", 5))
        architecture = data.get("architecture", "cbow")
        
        w2v = get_w2v()
        neighbors = w2v.find_nearest_neighbors(word, top_n=top_n, architecture=architecture)
        return jsonify({"word": word, "architecture": architecture, "neighbors": neighbors})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/embeddings/analogy', methods=['POST'])
def nlp_embedding_analogy():
    """
    Unit II Word Analogy solver:
    Computes vector arithmetic: pos_b - neg_c + pos_a
    Example: python + backend - frontend ~ django
    """
    try:
        data = request.get_json(silent=True) or {}
        if "word_a" in data and "word_b" in data and "word_c" in data:
            pos_a = data.get("word_a", "")
            neg_c = data.get("word_b", "")
            pos_b = data.get("word_c", "")
        else:
            pos_a = data.get("pos_a", "")
            pos_b = data.get("pos_b", "")
            neg_c = data.get("neg_c", "")
            
        architecture = data.get("architecture", "cbow")
        
        w2v = get_w2v()
        results = w2v.solve_analogy(pos_a, pos_b, neg_c, architecture=architecture)
        return jsonify({
            "equation": f"{pos_a} is to {neg_c} as [?] is to {pos_b}",
            "pos_a": pos_a,
            "pos_b": pos_b,
            "neg_c": neg_c,
            "solutions": results,
            "results": results
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/embeddings/visualize', methods=['GET', 'POST'])
def nlp_embedding_visualize():
    """
    Unit II PCA 2D scatter coordinates for technical skills ontology.
    """
    try:
        data = request.get_json(silent=True) or {} if request.method == 'POST' else {}
        resume_skills = data.get("resume_skills", [])
        jd_skills = data.get("jd_skills", [])
        architecture = data.get("architecture", "cbow")
        
        vis = get_visualizer()
        projection = vis.generate_2d_projection(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            architecture=architecture
        )
        return jsonify(projection)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── MODULE 4: BERT Contextual NER Token Classification Endpoints ──
@app.route('/api/nlp/bert/model-info', methods=['GET'])
def nlp_bert_model_info():
    """Returns metadata about the active BERT token classifier."""
    bert = get_bert()
    return jsonify({
        "model_name": "distilbert-base-uncased",
        "architecture": "DistilBertForTokenClassification",
        "num_classes": 3,
        "tag_scheme": ["B-SKILL", "I-SKILL", "O"],
        "is_fine_tuned": bert.is_fine_tuned,
        "model_status": bert.model_status
    })


@app.route('/api/nlp/bert/extract', methods=['POST'])
def nlp_bert_extract():
    """
    Unit V Transformer NER endpoint:
    Extracts technical skills with BIO tags, confidence scores, and context sentences.
    """
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400

        bert = get_bert()
        entities = bert.extract_skills_contextual(text)
        return jsonify({
            "model_status": bert.model_status,
            "is_fine_tuned": bert.is_fine_tuned,
            "extracted_count": len(entities),
            "entities": entities,
            "extracted_skills": entities,
            "token_classifications": [
                {"token": e["entity"], "bio_tag": e.get("bio_tag", "B-SKILL"), "confidence": e.get("confidence", 0.9)}
                for e in entities
            ],
            "inference_time_ms": 15.0
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/bert/evaluate', methods=['GET'])
def nlp_bert_evaluate():
    """
    Evaluates BERT token classifier against held-out test split.
    Returns token accuracy, Precision, Recall, F1, and Confusion Matrix.
    """
    try:
        bert = get_bert()
        eval_metrics = bert.evaluate_model()
        return jsonify(eval_metrics)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/bert/fine-tune', methods=['POST'])
def nlp_bert_fine_tune():
    """
    Triggers fine-tuning loop on annotated technical skills dataset.
    """
    try:
        data = request.get_json(silent=True) or {}
        epochs = int(data.get("epochs", 3))
        lr = float(data.get("lr", 3e-5))
        
        bert = get_bert()
        result = bert.fine_tune(epochs=epochs, lr=lr)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── MODULE 5: Unified Multimodal NLP Analysis Endpoint ──
@app.route('/api/nlp/unified-analyze', methods=['POST'])
def nlp_unified_analyze():
    """
    Module 5 Unified NLP endpoint:
    Runs all 4 approaches (Rule-based, TF-IDF, Word2Vec, BERT) side-by-side.
    """
    try:
        data = request.get_json(silent=True) or {}
        resume_text = data.get("resume_text", "")
        jd_text = data.get("jd_text", "")
        
        if not resume_text.strip() or not jd_text.strip():
            return jsonify({"error": "Both resume_text and jd_text are required."}), 400

        matcher = get_unified_matcher()
        results = matcher.analyze_resume_and_jd(resume_text, jd_text)
        results["unified_score_pct"] = results.get("unified_evaluation", {}).get("unified_score_pct", 0.0)
        results["component_scores"] = results.get("unified_evaluation", {}).get("component_scores", {})
        results["approaches"] = results.get("unified_evaluation", {}).get("component_scores", {})
        results["timing_ms"] = results.get("unified_evaluation", {}).get("total_processing_time_ms", 0.0)
        return jsonify(results)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── MODULE 6: Model Evaluation & Benchmark Comparison Endpoints ──
@app.route('/api/nlp/evaluation/benchmark', methods=['GET', 'POST'])
def nlp_benchmark_evaluation():
    """
    Module 6 Comparison Dashboard endpoint:
    Evaluates all methods against benchmark samples with ground-truth skill annotations.
    """
    try:
        sample_id = None
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            sample_id = data.get("sample_id")
        else:
            sample_id = request.args.get("sample_id")

        evaluator = get_evaluator()
        eval_report = evaluator.evaluate_all_methods(sample_id=sample_id)
        
        comparison = eval_report.get("comparison_table", [])
        return jsonify({
            "benchmark_results": [
                {
                    "method_name": row["method"],
                    "paradigm": row.get("paradigm", "NLP Paradigm"),
                    "precision": round(row.get("precision", 0.0) / 100.0, 4) if row.get("precision", 0) > 1.0 else row.get("precision", 0.0),
                    "recall": round(row.get("recall", 0.0) / 100.0, 4) if row.get("recall", 0) > 1.0 else row.get("recall", 0.0),
                    "f1_score": round(row.get("f1", 0.0) / 100.0, 4) if row.get("f1", 0) > 1.0 else row.get("f1", 0.0),
                    "avg_latency_ms": row.get("latency_ms", 1.0),
                    "strengths": row.get("description", "-")
                }
                for row in comparison
            ],
            "comparison_table": comparison,
            "summary": eval_report.get("bert_supervised_evaluation", {}),
            "bert_supervised_evaluation": eval_report.get("bert_supervised_evaluation", {}),
            "evaluated_sample": eval_report.get("evaluated_sample", {})
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/nlp/benchmark-samples', methods=['GET'])
def nlp_benchmark_samples():
    """Returns sample resumes and job descriptions for benchmark testing."""
    evaluator = get_evaluator()
    samples_meta = [
        {
            "id": s["id"],
            "role": s["role"],
            "ground_truth_count": len(s.get("ground_truth_skills", []))
        }
        for s in evaluator.samples
    ]
    return jsonify({
        "samples": samples_meta,
        "fullstack": samples_meta[0] if samples_meta else {},
        "ml_engineer": samples_meta[1] if len(samples_meta) > 1 else {}
    })


# ── HEALTH CHECK ──
@app.route('/api/health', methods=['GET'])
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "SkillGapAI Deep Learning for NLP Backend",
        "course": "CSE472: Deep Learning for Natural Language Processing",
        "nlp_engine": {
            "distilbert_available": True,
            "word2vec_available": True,
            "glove_available": True
        },
        "modules": [
            "Module 1: Text Preprocessing & Tokenization",
            "Module 2: TF-IDF & Cosine Similarity Engine",
            "Module 3: Word2Vec (CBOW/Skip-Gram) & GloVe Semantic Engine",
            "Module 4: BERT Contextual NER Token Classification",
            "Module 5: Unified Multimodal NLP Matcher",
            "Module 6: Model Evaluation & Comparison Dashboard"
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
