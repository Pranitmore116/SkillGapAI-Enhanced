"""
CSE472 Deep Learning for NLP - Module 2B: TF-IDF and Cosine Similarity Matching Engine
Implements Unit I syllabus concepts:
- Term Frequency - Inverse Document Frequency (TF-IDF)
- TfidfVectorizer with Unigram and Bigram features
- Mathematical Cosine Similarity: cos(A,B) = (A · B) / (||A|| × ||B||)
- Top Keyword Extraction & Relative Weight Analysis
- Weighted Skill Scoring vs. General Lexical Document Similarity
"""

import json
import os
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfEngine:
    """
    Mathematical TF-IDF vectorization and Cosine Similarity engine.
    Aligned with CSE472 Unit I.
    """

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), max_features: int = 1000):
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.token_pattern = r'(?u)\b[a-zA-Z0-9+#_.-]+\b'
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            token_pattern=self.token_pattern,
            sublinear_tf=True,
            norm='l2',
            lowercase=True
        )
        self.known_skills = self._load_ontology_skills()

    def _load_ontology_skills(self) -> set:
        """
        Loads technical skill canonical names and aliases for skill weighting.
        """
        skills_set = set()
        ontology_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skill_ontology.json')
        if os.path.exists(ontology_path):
            try:
                with open(ontology_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('skills', []):
                        skills_set.add(item.get('name', '').lower())
                        for alias in item.get('aliases', []):
                            skills_set.add(alias.lower())
            except Exception:
                pass
        return skills_set

    def compute_similarity(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Computes mathematical TF-IDF representation, cosine similarity,
        and term-level importance ranking for Resume vs. Job Description.
        """
        if not resume_text.strip() or not jd_text.strip():
            return {
                "cosine_similarity_pct": 0.0,
                "raw_cosine": 0.0,
                "dot_product": 0.0,
                "norm_resume": 0.0,
                "norm_jd": 0.0,
                "matched_terms": [],
                "missing_terms": [],
                "resume_top_terms": [],
                "jd_top_terms": [],
                "skill_weighted_score": 0.0,
                "formula": "cos(A, B) = (A · B) / (||A|| × ||B||)"
            }

        corpus = [resume_text, jd_text]
        tfidf_matrix = self.vectorizer.fit_transform(corpus).toarray()
        feature_names = self.vectorizer.get_feature_names_out()

        vec_resume = tfidf_matrix[0]
        vec_jd = tfidf_matrix[1]

        # 1. Mathematical Cosine Similarity
        # Dot product
        dot_product = float(np.dot(vec_resume, vec_jd))
        # L2 Norms
        norm_resume = float(np.linalg.norm(vec_resume))
        norm_jd = float(np.linalg.norm(vec_jd))

        if norm_resume == 0.0 or norm_jd == 0.0:
            cosine_sim = 0.0
        else:
            cosine_sim = float(dot_product / (norm_resume * norm_jd))

        # 2. Term Importance Ranking
        # Terms prominent in Resume
        resume_ranked_indices = np.argsort(vec_resume)[::-1]
        resume_top_terms = []
        for idx in resume_ranked_indices:
            score = float(vec_resume[idx])
            if score <= 0.0:
                break
            term = feature_names[idx]
            resume_top_terms.append({
                "term": term,
                "tfidf": round(score, 4),
                "is_technical_skill": term.lower() in self.known_skills
            })

        # Terms prominent in JD
        jd_ranked_indices = np.argsort(vec_jd)[::-1]
        jd_top_terms = []
        for idx in jd_ranked_indices:
            score = float(vec_jd[idx])
            if score <= 0.0:
                break
            term = feature_names[idx]
            jd_top_terms.append({
                "term": term,
                "tfidf": round(score, 4),
                "is_technical_skill": term.lower() in self.known_skills
            })

        # 3. Matched Terms (present in both documents)
        matched_terms = []
        # Missing Terms (prominent in JD but 0 or negligible in Resume)
        missing_terms = []

        for idx, term in enumerate(feature_names):
            score_r = float(vec_resume[idx])
            score_jd = float(vec_jd[idx])

            if score_jd > 0.0:
                if score_r > 0.0:
                    joint_weight = score_r * score_jd
                    is_skill = term.lower() in self.known_skills
                    matched_terms.append({
                        "term": term,
                        "resume_tfidf": round(score_r, 4),
                        "jd_tfidf": round(score_jd, 4),
                        "joint_importance": round(joint_weight, 4),
                        "is_technical_skill": is_skill
                    })
                else:
                    # In JD but missing in Resume
                    missing_terms.append({
                        "term": term,
                        "jd_tfidf": round(score_jd, 4),
                        "is_technical_skill": term.lower() in self.known_skills
                    })

        # Sort matched terms by joint importance
        matched_terms.sort(key=lambda x: x["joint_importance"], reverse=True)
        # Sort missing terms by JD TF-IDF priority
        missing_terms.sort(key=lambda x: x["jd_tfidf"], reverse=True)

        # 4. Domain-Weighted Skill Score
        # Calculates weighted similarity putting 2.5x emphasis on verified technical skills
        skill_numerator = 0.0
        skill_denominator = 0.0
        for item in jd_top_terms:
            weight = 2.5 if item["is_technical_skill"] else 1.0
            term = item["term"]
            jd_tfidf = item["tfidf"]
            # Find in matched
            matching_entry = next((m for m in matched_terms if m["term"] == term), None)
            if matching_entry:
                resume_ratio = min(1.0, matching_entry["resume_tfidf"] / jd_tfidf)
                skill_numerator += weight * jd_tfidf * resume_ratio
            skill_denominator += weight * jd_tfidf

        skill_weighted_pct = round((skill_numerator / skill_denominator) * 100, 2) if skill_denominator > 0 else 0.0

        return {
            "cosine_similarity_pct": round(cosine_sim * 100, 2),
            "raw_cosine": round(cosine_sim, 4),
            "dot_product": round(dot_product, 4),
            "norm_resume": round(norm_resume, 4),
            "norm_jd": round(norm_jd, 4),
            "skill_weighted_score_pct": skill_weighted_pct,
            "matched_terms_count": len(matched_terms),
            "missing_terms_count": len(missing_terms),
            "matched_terms": matched_terms[:25],
            "missing_terms": missing_terms[:25],
            "resume_top_terms": resume_top_terms[:15],
            "jd_top_terms": jd_top_terms[:15],
            "formula": "cos(Resume, JD) = (Resume · JD) / (||Resume|| × ||JD||)",
            "tfidf_formula": "TF-IDF(t, d) = TF(t, d) × IDF(t)"
        }
