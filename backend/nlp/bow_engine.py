"""
CSE472 Deep Learning for NLP - Module 2A: Bag-of-Words (BoW) Engine
Implements Unit I syllabus concepts:
- CountVectorizer representation
- Unigram and Bigram feature spaces
- Term frequency matrix computation
- Vector inner product and Bag-of-Words similarity
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import CountVectorizer


class BagOfWordsEngine:
    """
    Computes Bag-of-Words (BoW) vector representations and similarity metrics.
    Aligned with CSE472 Unit I.
    """

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), max_features: int = 500):
        self.ngram_range = ngram_range
        self.max_features = max_features
        # Regex token pattern preserving technical terms containing +, #, ., and dashes
        self.token_pattern = r'(?u)\b[a-zA-Z0-9+#_.-]+\b'
        self.vectorizer = CountVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            token_pattern=self.token_pattern,
            lowercase=True
        )

    def vectorize_pair(self, doc_a: str, doc_b: str) -> Dict[str, Any]:
        """
        Fits vocabulary on both documents and extracts dense BoW vectors.
        """
        if not doc_a.strip() or not doc_b.strip():
            return {
                "similarity": 0.0,
                "shared_vocabulary_size": 0,
                "top_features": [],
                "doc_a_term_count": 0,
                "doc_b_term_count": 0,
                "overlap_count": 0
            }

        corpus = [doc_a, doc_b]
        bow_matrix = self.vectorizer.fit_transform(corpus).toarray()
        feature_names = self.vectorizer.get_feature_names_out()

        vec_a = bow_matrix[0]
        vec_b = bow_matrix[1]

        # Calculate Cosine Similarity on BoW vectors
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            bow_cosine = 0.0
        else:
            bow_cosine = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

        # Identify shared terms (non-zero in both)
        shared_mask = (vec_a > 0) & (vec_b > 0)
        shared_indices = np.where(shared_mask)[0]
        
        shared_terms = []
        for idx in shared_indices:
            term = feature_names[idx]
            count_a = int(vec_a[idx])
            count_b = int(vec_b[idx])
            shared_terms.append({
                "term": term,
                "count_resume": count_a,
                "count_jd": count_b,
                "product": count_a * count_b
            })

        # Sort shared terms by combined frequency product
        shared_terms.sort(key=lambda x: x["product"], reverse=True)

        return {
            "similarity": round(bow_cosine * 100, 2),
            "raw_cosine": float(bow_cosine),
            "shared_vocabulary_size": len(feature_names),
            "doc_a_term_count": int(np.sum(vec_a)),
            "doc_b_term_count": int(np.sum(vec_b)),
            "overlap_count": len(shared_indices),
            "top_shared_terms": shared_terms[:15],
            "sample_vocabulary": list(feature_names[:25])
        }

