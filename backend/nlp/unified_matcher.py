"""
CSE472 Deep Learning for NLP - Module 5: Unified NLP Matching Engine
Integrates four independent academic paradigms:
- Approach A: Rule-Based / Dictionary Matching
- Approach B: TF-IDF + Cosine Vector Similarity (Unit I)
- Approach C: Word2Vec / GloVe Dense Semantic Matching (Unit II)
- Approach D: BERT Contextual NER Token Classification (Unit V)
Computes transparent multi-modal comparison with latency benchmarking.
"""

import time
from typing import Dict, List, Any, Optional

from nlp.preprocessing import TextPreprocessor
from nlp.bow_engine import BagOfWordsEngine
from nlp.tfidf_engine import TfidfEngine
from nlp.word2vec_engine import Word2VecEngine
from nlp.glove_engine import GloVeEngine
from nlp.bert_extractor import BertSkillExtractor
from nlp.skill_validator import SkillValidator


class UnifiedNLPMatcher:
    """
    Multimodal NLP aggregator executing all four course approaches independently.
    Provides transparent, unbundled component scores and justified unified scoring.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.bow_engine = BagOfWordsEngine()
        self.tfidf_engine = TfidfEngine()
        self.w2v_engine = Word2VecEngine()
        self.glove_engine = GloVeEngine()
        self.bert_extractor = BertSkillExtractor()

    def analyze_resume_and_jd(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Executes all four matching approaches, measures latency, and produces
        side-by-side academic comparisons.
        """
        # Module 1: Preprocessing Pipeline
        t0 = time.perf_counter()
        prep_resume = self.preprocessor.process_document(resume_text)
        prep_jd = self.preprocessor.process_document(jd_text)
        prep_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        # ── Approach A: Rule-Based Keyword Matching ──
        t0 = time.perf_counter()
        rule_results = self._run_rule_based_matching(prep_resume, prep_jd)
        rule_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        # ── Approach B: Bag-of-Words & TF-IDF Cosine Similarity (Unit I) ──
        t0 = time.perf_counter()
        bow_results = self.bow_engine.vectorize_pair(prep_resume["cleaned_text"], prep_jd["cleaned_text"])
        tfidf_results = self.tfidf_engine.compute_similarity(prep_resume["cleaned_text"], prep_jd["cleaned_text"])
        tfidf_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        # ── Approach C: Word2Vec / GloVe Semantic Matching (Unit II) ──
        t0 = time.perf_counter()
        resume_skill_names = [s["name"] for s in rule_results["resume_skills"]]
        jd_skill_names = [s["name"] for s in rule_results["jd_skills"]]
        
        w2v_results = self.w2v_engine.match_semantic_skills(
            resume_skills=resume_skill_names,
            jd_skills=jd_skill_names,
            threshold=0.50
        )
        w2v_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        # ── Approach D: BERT Contextual NER Skill Extraction (Unit V) ──
        t0 = time.perf_counter()
        bert_resume_entities = self.bert_extractor.extract_skills_contextual(resume_text)
        bert_jd_entities = self.bert_extractor.extract_skills_contextual(jd_text)
        bert_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        # Evaluate BERT entity overlap between resume and JD
        bert_results = self._calculate_bert_overlap(bert_resume_entities, bert_jd_entities)

        # ── Unified Transparent Score Formulation ──
        # Formula: Unified = 0.25 * Rule + 0.25 * TFIDF + 0.25 * Word2Vec + 0.25 * BERT
        score_rule = float(rule_results["match_pct"])
        score_tfidf = float(tfidf_results["cosine_similarity_pct"])
        score_w2v = float(w2v_results["match_score_pct"])
        score_bert = float(bert_results["match_pct"])

        weights = {"rule": 0.25, "tfidf": 0.25, "w2v": 0.25, "bert": 0.25}
        unified_score = round(
            weights["rule"] * score_rule +
            weights["tfidf"] * score_tfidf +
            weights["w2v"] * score_w2v +
            weights["bert"] * score_bert,
            2
        )

        return {
            "preprocessing": {
                "latency_ms": prep_time_ms,
                "resume": prep_resume,
                "jd": prep_jd
            },
            "approach_a_rule": {
                "name": "Rule-Based Matching",
                "unit": "Baseline / Regular Expressions",
                "latency_ms": rule_time_ms,
                "score_pct": score_rule,
                "matched_count": len(rule_results["matched"]),
                "missing_count": len(rule_results["missing"]),
                "extra_count": len(rule_results["extra"]),
                "matched_skills": rule_results["matched"],
                "missing_skills": rule_results["missing"],
                "extra_skills": rule_results["extra"]
            },
            "approach_b_tfidf": {
                "name": "TF-IDF + Cosine Similarity",
                "unit": "Unit I: Text Processing & VSM",
                "latency_ms": tfidf_time_ms,
                "cosine_similarity_pct": score_tfidf,
                "skill_weighted_score_pct": tfidf_results["skill_weighted_score_pct"],
                "bow_similarity_pct": bow_results["similarity"],
                "dot_product": tfidf_results["dot_product"],
                "norm_resume": tfidf_results["norm_resume"],
                "norm_jd": tfidf_results["norm_jd"],
                "matched_terms": tfidf_results["matched_terms"][:15],
                "missing_terms": tfidf_results["missing_terms"][:15],
                "resume_top_terms": tfidf_results["resume_top_terms"][:10],
                "jd_top_terms": tfidf_results["jd_top_terms"][:10],
                "formula": tfidf_results["formula"]
            },
            "approach_c_embeddings": {
                "name": "Word2Vec Semantic Matching",
                "unit": "Unit II: Word Embeddings",
                "latency_ms": w2v_time_ms,
                "score_pct": score_w2v,
                "exact_matches_count": w2v_results["exact_matches_count"],
                "semantic_matches_count": w2v_results["semantic_matches_count"],
                "missing_skills_count": w2v_results["missing_skills_count"],
                "exact_matches": w2v_results["exact_matches"],
                "semantic_matches": w2v_results["semantic_matches"],
                "missing_skills": w2v_results["missing_skills"]
            },
            "approach_d_bert": {
                "name": "BERT Contextual NER",
                "unit": "Unit V: Transformers & Pretrained Models",
                "latency_ms": bert_time_ms,
                "model_status": self.bert_extractor.model_status,
                "score_pct": score_bert,
                "resume_entities_count": len(bert_resume_entities),
                "jd_entities_count": len(bert_jd_entities),
                "matched_entities_count": len(bert_results["matched_entities"]),
                "missing_entities_count": len(bert_results["missing_entities"]),
                "bonus_entities_count": len(bert_results["bonus_entities"]),
                "resume_entities": bert_resume_entities,
                "jd_entities": bert_jd_entities,
                "matched_entities": bert_results["matched_entities"],
                "missing_entities": bert_results["missing_entities"],
                "bonus_entities": bert_results["bonus_entities"],
                "extra_entities": bert_results["bonus_entities"]
            },
            "unified_evaluation": {
                "unified_score_pct": unified_score,
                "formula": "0.25 * Rule + 0.25 * TFIDF + 0.25 * Word2Vec + 0.25 * BERT",
                "component_scores": {
                    "rule_based": score_rule,
                    "tfidf_cosine": score_tfidf,
                    "word2vec_semantic": score_w2v,
                    "bert_contextual": score_bert
                },
                "total_processing_time_ms": round(prep_time_ms + rule_time_ms + tfidf_time_ms + w2v_time_ms + bert_time_ms, 2)
            }
        }

    def _run_rule_based_matching(self, prep_resume: Dict[str, Any], prep_jd: Dict[str, Any]) -> Dict[str, Any]:
        """Dictionary matching against verified technical skills ontology."""
        found_resume = SkillValidator.extract_valid_skills_from_text(prep_resume["cleaned_text"])
        found_jd = SkillValidator.extract_valid_skills_from_text(prep_jd["cleaned_text"])

        gap = SkillValidator.calculate_skill_gap(
            [s["name"] for s in found_resume],
            [s["name"] for s in found_jd]
        )

        matched_names = set(gap["matched_skills"])
        missing_names = set(gap["missing_skills"])
        bonus_names = set(gap["bonus_skills"])

        matched = [s for s in found_jd if s["name"] in matched_names]
        missing = [s for s in found_jd if s["name"] in missing_names]
        extra = [s for s in found_resume if s["name"] in bonus_names]

        match_pct = round((len(matched) / len(found_jd) * 100), 2) if found_jd else 0.0

        return {
            "resume_skills": found_resume,
            "jd_skills": found_jd,
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "match_pct": match_pct
        }

    @staticmethod
    def _calculate_bert_overlap(resume_entities: List[Dict[str, Any]], jd_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates contextual entity overlap between Resume and JD extractions."""
        resume_set = {e["entity"].lower(): e for e in resume_entities}
        jd_set = {e["entity"].lower(): e for e in jd_entities}

        matched = []
        missing = []
        bonus = []

        for jd_lower, jd_item in jd_set.items():
            if jd_lower in resume_set:
                matched.append({
                    "entity": jd_item["entity"],
                    "category": jd_item.get("category", "Technical Skill"),
                    "confidence": jd_item["confidence"],
                    "resume_context": resume_set[jd_lower].get("context_sentence", ""),
                    "jd_context": jd_item.get("context_sentence", "")
                })
            else:
                missing.append(jd_item)

        for res_lower, res_item in resume_set.items():
            if res_lower not in jd_set:
                bonus.append(res_item)

        match_pct = round((len(matched) / len(jd_set) * 100), 2) if jd_set else 0.0

        return {
            "matched_entities": matched,
            "missing_entities": missing,
            "bonus_entities": bonus,
            "extra_entities": bonus,
            "match_pct": match_pct
        }

