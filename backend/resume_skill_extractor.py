import os
import re
import json
from typing import List, Dict, Any, Optional

# For text extraction
import PyPDF2
import docx

# Import modular academic NLP pipeline components
from nlp.preprocessing import TextPreprocessor
from nlp.bert_extractor import BertSkillExtractor
from nlp.word2vec_engine import Word2VecEngine
from nlp.tfidf_engine import TfidfEngine
from nlp.skill_validator import SkillValidator

# Optional: Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Expanded default skill list for keyword and semantic matching
DEFAULT_SKILLS = [
    "python", "java", "sql", "aws", "amazon web services", "docker", "react", "ml", "machine learning",
    "javascript", "html", "css", "data science", "kubernetes", "azure", "git", "agile", "ruby",
    "php", "express", "mongodb", "postgresql", "mysql", "typescript", "next.js", "django", "flask",
    "fastapi", "spring boot", "laravel", "rails", "asp.net", "rest api", "microservices", "nosql",
    "terraform", "ansible", "jenkins", "ci/cd", "linux", "nlp", "deep learning", "tensorflow", "pytorch",
    "tableau", "power bi", "android", "ios", "flutter", "react native", "figma", "scrum", "agile", 
    "leadership", "communication", "problem solving", "bash", "shell", "c++", "c#", "go", "golang",
    "rust", "kotlin", "swift", "scala", "r", "matlab", "sqlite", "firebase", "redis", "elasticsearch"
]

# Initialize cached instances
_preprocessor = TextPreprocessor()
_bert_extractor = None
_w2v_engine = None


def get_bert_extractor():
    global _bert_extractor
    if _bert_extractor is None:
        _bert_extractor = BertSkillExtractor()
    return _bert_extractor


def get_w2v_engine():
    global _w2v_engine
    if _w2v_engine is None:
        _w2v_engine = Word2VecEngine()
    return _w2v_engine


def validate_file(file_path: str) -> str:
    """
    Validates the uploaded file based on its extension.
    Accepts only PDF, DOCX, and TXT files.
    Reject all other formats with a proper error message.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    valid_extensions = {'.pdf', '.docx', '.txt'}
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext not in valid_extensions:
        raise ValueError(f"Invalid file format: '{ext}'. Only PDF, DOCX, and TXT files are accepted.")
    
    return ext


def extract_text(file_path: str) -> str:
    """
    Extracts text from the provided file using TextPreprocessor.
    """
    validate_file(file_path)
    return TextPreprocessor.extract_from_file(file_path)


def clean_text(text: str) -> str:
    """
    Cleans the extracted text while preserving technical term tokens (C++, C#, .NET, etc.).
    """
    return _preprocessor.clean_text(text)


def extract_skills_keyword(text: str, skills_list: Optional[list] = None) -> list:
    """
    Extracts validated skills using predefined keyword list and technical taxonomy.
    """
    valid_extracted = SkillValidator.extract_valid_skills_from_text(text)
    extracted_skills = set(s["name"] for s in valid_extracted)

    if skills_list:
        text_lower = f" {text.lower()} "
        for skill in skills_list:
            v = SkillValidator.validate_and_canonicalize(skill)
            if v:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    extracted_skills.add(v["name"])
            
    return sorted(list(extracted_skills))


def extract_skills_spacy(text: str, skills_list: Optional[list] = None) -> list:
    """
    Dense semantic extraction using Word2Vec embeddings and domain ontology,
    guarded by technical skill validation to prevent hallucinated non-skills.
    """
    w2v = get_w2v_engine()
    kw_skills = extract_skills_keyword(text, skills_list)
    
    # Use Word2Vec to find closely related semantic terms
    semantic_skills = set()
    for kw in kw_skills:
        neighbors = w2v.find_nearest_neighbors(kw.lower(), top_n=3)
        for n in neighbors:
            if n["similarity"] >= 0.60:
                validated = SkillValidator.validate_and_canonicalize(n["word"])
                if validated:
                    semantic_skills.add(validated["name"])
                
    return sorted(list(semantic_skills))


def extract_skills_bert(text: str, skills_list: Optional[list] = None, threshold: float = 0.50) -> list:
    """
    Contextual Named Entity Recognition (NER) using BERT with BIO token classification.
    Validates candidates to guarantee only genuine technical skills are returned.
    """
    bert = get_bert_extractor()
    entities = bert.extract_skills_contextual(text)
    return sorted(list(set(e["entity"] for e in entities if e.get("confidence", 0) >= threshold)))


def optimize_resume(original_text: str, missing_skills: list) -> str:
    """
    Generates resume optimization recommendations for missing skills.
    """
    optimized = original_text
    if missing_skills:
        addition = "\n\n[AI SUGGESTED OPTIMIZATIONS]\n"
        addition += "Consider adding the following keywords to your 'Skills' or 'Experience' section to pass ATS filters:\n"
        for skill in missing_skills:
            addition += f"- {skill.title() if isinstance(skill, str) else str(skill)}\n"
        optimized += addition
    return optimized


def process_resume(file_path: str, skills_list: Optional[list] = None, jd_text: Optional[str] = None) -> str:
    """
    Orchestrator function:
    1. Validation & Extraction
    2. Academic Preprocessing & Cleaning
    3. Multi-Model Extraction (Keyword, Word2Vec, BERT)
    4. Optimization (if JD text is provided)
    Returns: JSON string with extracted data.
    """
    try:
        raw_text = extract_text(file_path)
        cleaned_text = clean_text(raw_text)
        
        # Execute extractions using validated pipeline
        kw_skills = extract_skills_keyword(cleaned_text, skills_list)
        sp_skills = extract_skills_spacy(cleaned_text, skills_list)
        bt_skills = extract_skills_bert(raw_text, skills_list)
        
        # Optimization & Match Scoring (if JD text is provided)
        optimized_text = raw_text
        matched_skills = []
        missing_skills = []
        bonus_skills = []
        match_score = 0
        jd_skills = []

        if jd_text:
            jd_cleaned = clean_text(jd_text)
            jd_skills_raw = extract_skills_keyword(jd_cleaned, skills_list)
            
            # Combine all validated resume skills
            resume_skills_combined = sorted(list(set(kw_skills + sp_skills + bt_skills)))
            
            # Calculate gap strictly using SkillValidator
            gap_data = SkillValidator.calculate_skill_gap(resume_skills_combined, jd_skills_raw)
            matched_skills = gap_data["matched_skills"]
            missing_skills = gap_data["missing_skills"]
            bonus_skills = gap_data["bonus_skills"]
            jd_skills = gap_data["jd_valid_skills"]
            
            match_score = round(len(matched_skills) / max(len(jd_skills), 1) * 100, 1)
            optimized_text = optimize_resume(raw_text, missing_skills)
            
        result = {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "optimized_text": optimized_text,
            "keyword_skills": kw_skills,
            "spacy_skills": sp_skills,
            "bert_skills": bt_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "bonus_skills": bonus_skills,
            "extra_skills": bonus_skills,
            "match_score": match_score,
            "jd_skills": jd_skills
        }
        
        return json.dumps(result, indent=4)
        
    except Exception as e:
        error_result = {
            "error": str(e)
        }
        return json.dumps(error_result, indent=4)


if __name__ == "__main__":
    test_file = "dummy_resume.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("I am a software engineer with 5 years of experience in Python, specialized in Machine Learning, React, and AWS.")
    
    print(f"Testing process_resume with {test_file}...")
    output = process_resume(test_file)
    print(output)
    
    if os.path.exists(test_file):
        os.remove(test_file)
