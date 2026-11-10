"""
CSE472 Deep Learning for NLP - Similarity Engine
Implements Unit I & Unit II vector distance and similarity functions:
- Cosine Similarity
- Euclidean (L2) Distance
- Manhattan (L1) Distance
- Jaccard Similarity (Set-based)
- Normalized Inner Product
"""

import numpy as np
from typing import Set, Any, Union, List


class SimilarityEngine:
    """
    Mathematical similarity and distance metric calculator for vector space models.
    """

    @staticmethod
    def cosine_similarity(vec_a: Union[np.ndarray, List[float]], vec_b: Union[np.ndarray, List[float]]) -> float:
        """
        Computes Cosine Similarity:
        cos(a, b) = (a · b) / (||a||_2 * ||b||_2)
        """
        a = np.asarray(vec_a, dtype=float)
        b = np.asarray(vec_b, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def euclidean_distance(vec_a: Union[np.ndarray, List[float]], vec_b: Union[np.ndarray, List[float]]) -> float:
        """
        Computes Euclidean (L2) Distance:
        d(a, b) = ||a - b||_2 = sqrt(sum((a_i - b_i)^2))
        """
        a = np.asarray(vec_a, dtype=float)
        b = np.asarray(vec_b, dtype=float)
        return float(np.linalg.norm(a - b))

    @staticmethod
    def manhattan_distance(vec_a: Union[np.ndarray, List[float]], vec_b: Union[np.ndarray, List[float]]) -> float:
        """
        Computes Manhattan (L1) Distance:
        d(a, b) = sum(|a_i - b_i|)
        """
        a = np.asarray(vec_a, dtype=float)
        b = np.asarray(vec_b, dtype=float)
        return float(np.sum(np.abs(a - b)))

    @staticmethod
    def jaccard_similarity(set_a: Set[Any], set_b: Set[Any]) -> float:
        """
        Computes Jaccard Similarity Coefficient:
        J(A, B) = |A ∩ B| / |A ∪ B|
        """
        if not set_a and not set_b:
            return 1.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        if union == 0:
            return 0.0
        return float(intersection / union)

    @staticmethod
    def compute_all_metrics(vec_a: np.ndarray, vec_b: np.ndarray, tokens_a: List[str] = None, tokens_b: List[str] = None) -> dict:
        """
        Returns a comparative dictionary of multiple similarity & distance metrics.
        """
        cos_sim = SimilarityEngine.cosine_similarity(vec_a, vec_b)
        euc_dist = SimilarityEngine.euclidean_distance(vec_a, vec_b)
        man_dist = SimilarityEngine.manhattan_distance(vec_a, vec_b)
        
        jaccard = None
        if tokens_a is not None and tokens_b is not None:
            jaccard = SimilarityEngine.jaccard_similarity(set(tokens_a), set(tokens_b))

        return {
            "cosine_similarity": round(cos_sim, 4),
            "cosine_similarity_pct": round(cos_sim * 100, 2),
            "euclidean_distance": round(euc_dist, 4),
            "manhattan_distance": round(man_dist, 4),
            "jaccard_similarity": round(jaccard, 4) if jaccard is not None else None,
            "jaccard_similarity_pct": round(jaccard * 100, 2) if jaccard is not None else None
        }

