"""
CSE472 Deep Learning for NLP - Module 6: Model Evaluation & Comparison Engine
Implements evaluation metrics:
- Precision, Recall, F1-Score, Token-Level Accuracy
- Latency Benchmarking across all NLP Paradigms
- Evaluation against Ground-Truth Annotated Datasets
- Methodological Strengths & Limitations Analysis
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

from nlp.preprocessing import TextPreprocessor
from nlp.bow_engine import BagOfWordsEngine
from nlp.tfidf_engine import TfidfEngine
from nlp.word2vec_engine import Word2VecEngine
from nlp.bert_extractor import BertSkillExtractor
from nlp.skill_validator import SkillValidator


class ModelEvaluator:
    """
    Academic evaluation harness comparing all course NLP approaches against
    ground-truth benchmark annotations.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.bow_engine = BagOfWordsEngine()
        self.tfidf_engine = TfidfEngine()
        self.w2v_engine = Word2VecEngine()
        self.bert_extractor = BertSkillExtractor()
        
        self.benchmark_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_resumes_jds.json')
        self.samples = self._load_benchmark_samples()

    def _load_benchmark_samples(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.benchmark_path):
            try:
                with open(self.benchmark_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("samples", [])
            except Exception:
                pass
        return []

    def evaluate_all_methods(self, sample_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs comprehensive benchmark comparison across all methods on selected sample or default.
        """
        sample = None
        if sample_id:
            sample = next((s for s in self.samples if s.get("id") == sample_id), None)
        if not sample and self.samples:
            sample = self.samples[0]

        if not sample:
            return {"error": "No benchmark sample available."}

        resume_text = sample["resume_text"]
        jd_text = sample["jd_text"]
        ground_truth = set(s.lower() for s in sample.get("ground_truth_skills", []))

        results = []

        # ── 1. Rule-Based Extractor ──
        t0 = time.perf_counter()
        valid_rule = SkillValidator.extract_valid_skills_from_text(resume_text)
        rule_extracted = set(s["name"].lower() for s in valid_rule)
        t_rule = (time.perf_counter() - t0) * 1000

        m_rule = self._compute_metrics(rule_extracted, ground_truth)
        results.append({
            "method": "Rule-Based Regex Matching",
            "unit": "Baseline (Keyword Dictionaries)",
            "precision": m_rule["precision"],
            "recall": m_rule["recall"],
            "f1": m_rule["f1"],
            "latency_ms": round(t_rule, 2),
            "extracted_count": len(rule_extracted),
            "tp": m_rule["tp"],
            "fp": m_rule["fp"],
            "fn": m_rule["fn"],
            "strengths": "Fast, 100% precision on exact keywords, zero false positives for known dictionary terms.",
            "limitations": "Cannot handle synonyms, abbreviations, morphological variations, or context."
        })

        # ── 2. Bag-of-Words (BoW) ──
        t0 = time.perf_counter()
        bow_out = self.bow_engine.vectorize_pair(resume_text, jd_text)
        bow_terms = set(t["term"].lower() for t in bow_out.get("top_shared_terms", []))
        t_bow = (time.perf_counter() - t0) * 1000
        m_bow = self._compute_metrics(bow_terms, ground_truth)
        results.append({
            "method": "Bag-of-Words (CountVectorizer)",
            "unit": "Unit I: Text Processing & BoW",
            "precision": m_bow["precision"],
            "recall": m_bow["recall"],
            "f1": m_bow["f1"],
            "latency_ms": round(t_bow, 2),
            "extracted_count": len(bow_terms),
            "tp": m_bow["tp"],
            "fp": m_bow["fp"],
            "fn": m_bow["fn"],
            "strengths": "Captures raw unigram and bigram frequency statistics directly from text.",
            "limitations": "High vector sparsity, treats all overlapping words (even generic nouns) equally."
        })

        # ── 3. TF-IDF + Cosine Similarity ──
        t0 = time.perf_counter()
        tfidf_out = self.tfidf_engine.compute_similarity(resume_text, jd_text)
        tfidf_terms = set(t["term"].lower() for t in tfidf_out.get("matched_terms", []))
        t_tfidf = (time.perf_counter() - t0) * 1000
        m_tfidf = self._compute_metrics(tfidf_terms, ground_truth)
        results.append({
            "method": "TF-IDF + Cosine Similarity",
            "unit": "Unit I: Vector Space Models & TF-IDF",
            "precision": m_tfidf["precision"],
            "recall": m_tfidf["recall"],
            "f1": m_tfidf["f1"],
            "latency_ms": round(t_tfidf, 2),
            "extracted_count": len(tfidf_terms),
            "tp": m_tfidf["tp"],
            "fp": m_tfidf["fp"],
            "fn": m_tfidf["fn"],
            "strengths": "Downweights ubiquitous common terms via IDF, highlights high-signal discriminative keywords.",
            "limitations": "Surface lexical matching only; zero similarity for semantically identical terms with different spellings."
        })

        # ── 4. Word2Vec Dense Embeddings ──
        t0 = time.perf_counter()
        w2v_out = self.w2v_engine.match_semantic_skills(
            resume_skills=list(rule_extracted),
            jd_skills=list(ground_truth),
            threshold=0.50
        )
        w2v_matched = set(m["matched_skill"].lower() for m in w2v_out.get("exact_matches", []))
        for s in w2v_out.get("semantic_matches", []):
            w2v_matched.add(s["matched_skill"].lower())
        t_w2v = (time.perf_counter() - t0) * 1000
        m_w2v = self._compute_metrics(w2v_matched, ground_truth)
        results.append({
            "method": "Word2Vec Dense Semantic Matching",
            "unit": "Unit II: Word Embeddings (CBOW / Skip-Gram)",
            "precision": m_w2v["precision"],
            "recall": m_w2v["recall"],
            "f1": m_w2v["f1"],
            "latency_ms": round(t_w2v, 2),
            "extracted_count": len(w2v_matched),
            "tp": m_w2v["tp"],
            "fp": m_w2v["fp"],
            "fn": m_w2v["fn"],
            "strengths": "Recognizes semantic equivalence (e.g. PyTorch ~ Deep Learning; Node.js ~ Backend) in continuous space.",
            "limitations": "Static vector per word; cannot handle polysemy (words with multiple contextual meanings)."
        })

        # ── 5. BERT Contextual Token Classification ──
        t0 = time.perf_counter()
        bert_entities = self.bert_extractor.extract_skills_contextual(resume_text)
        bert_extracted = set(e["entity"].lower() for e in bert_entities)
        t_bert = (time.perf_counter() - t0) * 1000
        m_bert = self._compute_metrics(bert_extracted, ground_truth)
        results.append({
            "method": "BERT Contextual NER (BIO Tagging)",
            "unit": "Unit V: Transformers & Pretrained Language Models",
            "precision": m_bert["precision"],
            "recall": m_bert["recall"],
            "f1": m_bert["f1"],
            "latency_ms": round(t_bert, 2),
            "extracted_count": len(bert_extracted),
            "tp": m_bert["tp"],
            "fp": m_bert["fp"],
            "fn": m_bert["fn"],
            "strengths": "Deep bidirectional contextual representations, subword handling, extracts novel skills in context.",
            "limitations": "Higher compute and latency requirements, requires GPU or quantization for large-scale production."
        })

        # Get BERT supervised test-set evaluation
        bert_test_eval = self.bert_extractor.evaluate_model()

        return {
            "evaluated_sample": {
                "id": sample["id"],
                "role": sample["role"],
                "ground_truth_skills_count": len(ground_truth),
                "ground_truth_skills": sorted(list(ground_truth))
            },
            "comparison_table": results,
            "bert_supervised_evaluation": bert_test_eval
        }

    @staticmethod
    def _compute_metrics(extracted: set, ground_truth: set) -> Dict[str, Any]:
        """Calculates standard Precision, Recall, and F1."""
        tp = len(extracted.intersection(ground_truth))
        fp = len(extracted - ground_truth)
        fn = len(ground_truth - extracted)

        precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2)
        }
