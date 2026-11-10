"""
CSE472 Deep Learning for NLP - Module 3A: Word2Vec Semantic Engine
Implements Unit II syllabus concepts:
- Dense Vector Word Embeddings
- Continuous Bag-of-Words (CBOW) Architecture (sg=0)
- Skip-Gram with Negative Sampling Architecture (sg=1)
- Word Vector Extraction and Cosine Semantic Similarity
- Word Analogy Vector Arithmetic (v_B - v_A + v_C)
- Semantic Skill Matching with Ontological Guardrails
"""

import os
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    Word2Vec = None
    GENSIM_AVAILABLE = False


DEFAULT_DOMAIN_CORPUS = [
    ["python", "django", "flask", "fastapi", "backend", "web", "development", "rest", "api"],
    ["javascript", "typescript", "react", "next.js", "frontend", "ui", "redux", "html5", "css3"],
    ["java", "spring", "boot", "microservices", "hibernate", "backend", "enterprise"],
    ["c++", "c#", ".net", "systems", "algorithms", "performance", "low-level"],
    ["machine", "learning", "deep", "learning", "scikit-learn", "tensorflow", "pytorch", "models", "nlp"],
    ["data", "analysis", "pandas", "numpy", "matplotlib", "seaborn", "statistics", "data-driven"],
    ["sql", "postgresql", "mysql", "database", "relational", "indexing", "queries", "sqlite"],
    ["mongodb", "nosql", "redis", "database", "document", "cache", "key-value"],
    ["docker", "kubernetes", "containers", "devops", "ci/cd", "deployment", "microservices"],
    ["aws", "azure", "google", "cloud", "cloud", "infrastructure", "terraform", "serverless"],
    ["git", "github", "gitlab", "version", "control", "agile", "scrum", "collaboration"],
    ["natural", "language", "processing", "nlp", "bert", "transformers", "text", "tokenization", "embeddings"],
    ["experience", "developing", "predictive", "models", "and", "data-driven", "applications"],
    ["experience", "in", "machine", "learning", "and", "predictive", "analytics"]
]


class Word2VecEngine:
    """
    Academic Word2Vec embedding engine for CSE472 Unit II.
    Supports CBOW and Skip-Gram with Negative Sampling.
    """

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        self.cbow_path = os.path.join(self.model_dir, 'word2vec_cbow.model')
        self.sg_path = os.path.join(self.model_dir, 'word2vec_skipgram.model')
        
        self.cbow_model = None
        self.sg_model = None
        self.active_architecture = "cbow"
        self.ontology = self._load_ontology()
        
        # Load or initialize models
        if GENSIM_AVAILABLE:
            self._initialize_models()

    def _load_ontology(self) -> Dict[str, Any]:
        """Loads technical skills ontology for category constraint checks."""
        ontology_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skill_ontology.json')
        if os.path.exists(ontology_path):
            try:
                with open(ontology_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"skills": []}

    def _build_training_sentences(self) -> List[List[str]]:
        """
        Synthesizes technical domain corpus from ontology and benchmark descriptions.
        """
        sentences = list(DEFAULT_DOMAIN_CORPUS)
        
        # Add sentences from ontology skill relationships
        for skill in self.ontology.get("skills", []):
            name = skill.get("name", "").lower()
            category = skill.get("category", "").lower()
            related = [r.lower() for r in skill.get("related", [])]
            aliases = [a.lower() for a in skill.get("aliases", [])]
            
            # Sentence binding skill to its category and aliases
            sentences.append([name, category] + aliases)
            # Sentence binding skill to related technologies
            if related:
                sentences.append([name] + related + [category])
                
        return sentences

    def train_models(self, vector_size: int = 50, window: int = 5, epochs: int = 40) -> None:
        """
        Trains both CBOW (sg=0) and Skip-Gram (sg=1) models on the domain corpus.
        """
        if not GENSIM_AVAILABLE:
            return

        sentences = self._build_training_sentences()

        # 1. Continuous Bag-of-Words (CBOW)
        # sg=0 specifies CBOW architecture
        self.cbow_model = Word2Vec(
            sentences=sentences,
            vector_size=vector_size,
            window=window,
            min_count=1,
            sg=0,
            workers=1,
            epochs=epochs,
            seed=42
        )
        self.cbow_model.save(self.cbow_path)

        # 2. Skip-Gram with Negative Sampling (SGNS)
        # sg=1 specifies Skip-Gram architecture
        self.sg_model = Word2Vec(
            sentences=sentences,
            vector_size=vector_size,
            window=window,
            min_count=1,
            sg=1,
            negative=5,
            workers=1,
            epochs=epochs,
            seed=42
        )
        self.sg_model.save(self.sg_path)

    def _initialize_models(self) -> None:
        """Loads cached models from disk or trains new domain models."""
        if os.path.exists(self.cbow_path):
            try:
                self.cbow_model = Word2Vec.load(self.cbow_path)
            except Exception:
                self.cbow_model = None

        if os.path.exists(self.sg_path):
            try:
                self.sg_model = Word2Vec.load(self.sg_path)
            except Exception:
                self.sg_model = None

        if self.cbow_model is None or self.sg_model is None:
            self.train_models()

    def get_model(self, architecture: str = "cbow"):
        """Returns the requested Word2Vec model (cbow or skipgram)."""
        if architecture.lower() in ["sg", "skipgram", "skip-gram"]:
            return self.sg_model or self.cbow_model
        return self.cbow_model or self.sg_model

    def get_word_vector(self, word: str, architecture: str = "cbow") -> Optional[np.ndarray]:
        """
        Extracts dense real-valued embedding vector for a given word.
        """
        model = self.get_model(architecture)
        if model is None:
            return None
        w = word.lower().strip()
        if w in model.wv:
            return model.wv[w]
        return None

    def compute_similarity(self, word_a: str, word_b: str, architecture: str = "cbow") -> float:
        """
        Computes cosine semantic similarity between two word vectors:
        cos(w_a, w_b) = (w_a · w_b) / (||w_a|| * ||w_b||)
        """
        model = self.get_model(architecture)
        if model is None:
            return 0.0
        w1, w2 = word_a.lower().strip(), word_b.lower().strip()
        if w1 in model.wv and w2 in model.wv:
            return float(model.wv.similarity(w1, w2))
        return 0.0

    def find_nearest_neighbors(self, word: str, top_n: int = 5, architecture: str = "cbow") -> List[Dict[str, Any]]:
        """
        Retrieves nearest neighbor tokens in dense embedding space.
        """
        model = self.get_model(architecture)
        if model is None:
            return []
        w = word.lower().strip()
        if w not in model.wv:
            return []
        neighbors = model.wv.most_similar(w, topn=top_n)
        return [{"word": term, "similarity": round(float(sim), 4)} for term, sim in neighbors]

    def solve_analogy(self, pos_a: str, pos_b: str, neg_c: str, architecture: str = "cbow") -> List[Dict[str, Any]]:
        """
        Evaluates vector analogy equation: v_result = v(pos_b) - v(neg_c) + v(pos_a)
        Example: python + backend - frontend ~ django
        """
        model = self.get_model(architecture)
        if model is None:
            return []
        try:
            results = model.wv.most_similar(positive=[pos_a.lower(), pos_b.lower()], negative=[neg_c.lower()], topn=3)
            return [{"word": term, "similarity": round(float(sim), 4)} for term, sim in results]
        except Exception:
            return []

    def match_semantic_skills(self, resume_skills: List[str], jd_skills: List[str], threshold: float = 0.50, architecture: str = "cbow") -> Dict[str, Any]:
        """
        Performs semantic skill matching between candidate skills and job requirements.
        Uses category ontology constraints to avoid spurious matches between unrelated domains.
        """
        norm_resume = {s.lower(): s for s in resume_skills}
        norm_jd = {s.lower(): s for s in jd_skills}

        exact_matches = []
        semantic_matches = []
        missing_skills = []

        # Build skill-to-category lookup
        skill_cats = {}
        skill_related = {}
        for item in self.ontology.get("skills", []):
            name_lower = item.get("name", "").lower()
            cat = item.get("category", "")
            rel = [r.lower() for r in item.get("related", [])]
            skill_cats[name_lower] = cat
            skill_related[name_lower] = rel
            for alias in item.get("aliases", []):
                skill_cats[alias.lower()] = cat
                skill_related[alias.lower()] = rel

        model = self.get_model(architecture)

        for jd_lower, jd_orig in norm_jd.items():
            # 1. Check exact match
            if jd_lower in norm_resume:
                exact_matches.append({
                    "jd_skill": jd_orig,
                    "matched_skill": norm_resume[jd_lower],
                    "match_type": "Exact",
                    "similarity": 1.0,
                    "category": skill_cats.get(jd_lower, "Technical")
                })
                continue

            # 2. Check semantic similarity against each resume skill
            best_match = None
            highest_sim = 0.0

            for res_lower, res_orig in norm_resume.items():
                # Category constraint check:
                cat_jd = skill_cats.get(jd_lower)
                cat_res = skill_cats.get(res_lower)
                
                # Check ontology related list
                is_ontologically_related = (
                    res_lower in skill_related.get(jd_lower, []) or
                    jd_lower in skill_related.get(res_lower, [])
                )
                
                # Only compare if in same category, ontologically linked, or category is unknown
                category_compatible = (cat_jd == cat_res) if (cat_jd and cat_res) else True

                if category_compatible or is_ontologically_related:
                    sim = 0.0
                    if model and jd_lower in model.wv and res_lower in model.wv:
                        sim = float(model.wv.similarity(jd_lower, res_lower))
                    elif is_ontologically_related:
                        # High confidence ontological link fallback
                        sim = 0.75

                    if sim > highest_sim and sim >= threshold:
                        highest_sim = sim
                        best_match = {
                            "jd_skill": jd_orig,
                            "matched_skill": res_orig,
                            "match_type": "Semantic (Word2Vec)",
                            "similarity": round(sim, 4),
                            "similarity_pct": round(sim * 100, 1),
                            "category": cat_jd or cat_res or "Technical",
                            "explanation": f"Semantic relation between '{res_orig}' and '{jd_orig}' (similarity: {sim:.2f})"
                        }

            if best_match:
                semantic_matches.append(best_match)
            else:
                missing_skills.append({
                    "jd_skill": jd_orig,
                    "category": skill_cats.get(jd_lower, "Technical")
                })

        total_jd = len(norm_jd)
        match_score = ((len(exact_matches) * 1.0 + len(semantic_matches) * 0.75) / total_jd * 100) if total_jd > 0 else 0.0

        return {
            "architecture": architecture,
            "match_score_pct": round(match_score, 2),
            "exact_matches_count": len(exact_matches),
            "semantic_matches_count": len(semantic_matches),
            "missing_skills_count": len(missing_skills),
            "exact_matches": exact_matches,
            "semantic_matches": semantic_matches,
            "missing_skills": missing_skills
        }

