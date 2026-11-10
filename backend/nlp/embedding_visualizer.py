"""
CSE472 Deep Learning for NLP - Module 3C: Embedding Visualizer
Implements Unit II syllabus concepts:
- Principal Component Analysis (PCA) for Dimensionality Reduction
- 2D Vector Space Projection of Dense Embeddings
- Cluster Identification by Technical Category
- Interactive Scatter Plot Coordinate Generation
"""

import json
import os
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.decomposition import PCA


CATEGORY_COLORS = {
    "Languages": "#3b82f6",       # Blue
    "Frontend": "#06b6d4",        # Cyan
    "Backend": "#8b5cf6",         # Purple
    "Databases": "#f59e0b",       # Amber
    "Cloud & DevOps": "#10b981",  # Emerald
    "Data & AI": "#ec4899",       # Pink
    "Tools": "#64748b",           # Slate
    "Soft Skills": "#a855f7"      # Violet
}


class EmbeddingVisualizer:
    """
    Reduces high-dimensional embeddings (Word2Vec / GloVe) to 2D PCA projections
    for academic visualization of technical semantic clusters.
    """

    def __init__(self, word2vec_engine=None):
        self.w2v = word2vec_engine
        self.ontology_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skill_ontology.json')

    def _load_ontology(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.ontology_path):
            try:
                with open(self.ontology_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('skills', [])
            except Exception:
                pass
        return []

    def generate_2d_projection(
        self,
        resume_skills: Optional[List[str]] = None,
        jd_skills: Optional[List[str]] = None,
        architecture: str = "cbow"
    ) -> Dict[str, Any]:
        """
        Projects domain technical skills into 2D space using PCA.
        Flags which skills are present in the Resume and JD.
        """
        try:
            from .word2vec_engine import Word2VecEngine
        except (ImportError, ValueError):
            from nlp.word2vec_engine import Word2VecEngine
        if self.w2v is None:
            self.w2v = Word2VecEngine()

        ontology_skills = self._load_ontology()
        resume_set = {s.lower() for s in (resume_skills or [])}
        jd_set = {s.lower() for s in (jd_skills or [])}

        words = []
        metadata = []
        vectors = []

        for item in ontology_skills:
            name = item.get("name", "")
            cat = item.get("category", "General")
            lookup_key = name.lower()
            
            vec = self.w2v.get_word_vector(lookup_key, architecture=architecture)
            if vec is None and item.get("aliases"):
                for alias in item["aliases"]:
                    vec = self.w2v.get_word_vector(alias.lower(), architecture=architecture)
                    if vec is not None:
                        break

            if vec is not None:
                words.append(name)
                vectors.append(vec)
                is_in_resume = lookup_key in resume_set
                is_in_jd = lookup_key in jd_set
                
                status = "neutral"
                if is_in_resume and is_in_jd:
                    status = "matched"
                elif is_in_jd and not is_in_resume:
                    status = "missing"
                elif is_in_resume:
                    status = "bonus"

                metadata.append({
                    "name": name,
                    "category": cat,
                    "color": CATEGORY_COLORS.get(cat, "#94a3b8"),
                    "status": status,
                    "is_in_resume": is_in_resume,
                    "is_in_jd": is_in_jd,
                    "related": item.get("related", [])
                })

        if len(vectors) < 3:
            return {"points": [], "explained_variance": [0, 0]}

        # Perform PCA
        X = np.array(vectors)
        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X)

        explained_var = [round(float(v) * 100, 2) for v in pca.explained_variance_ratio_]

        # Normalize coordinates between -100 and +100 for responsive canvas rendering
        max_abs = np.max(np.abs(X_2d)) if np.max(np.abs(X_2d)) > 0 else 1.0
        X_norm = (X_2d / max_abs) * 100.0

        points = []
        for i, meta in enumerate(metadata):
            points.append({
                "name": meta["name"],
                "skill": meta["name"],
                "x": round(float(X_norm[i, 0]), 2),
                "y": round(float(X_norm[i, 1]), 2),
                "category": meta["category"],
                "color": meta["color"],
                "status": meta["status"],
                "is_in_resume": meta["is_in_resume"],
                "is_in_jd": meta["is_in_jd"],
                "related": meta["related"]
            })

        return {
            "total_points": len(points),
            "explained_variance": explained_var,
            "explained_variance_pc1": explained_var[0] if len(explained_var) > 0 else 0,
            "explained_variance_pc2": explained_var[1] if len(explained_var) > 1 else 0,
            "categories": list(CATEGORY_COLORS.keys()),
            "category_colors": CATEGORY_COLORS,
            "points": points,
            "skills": points
        }
