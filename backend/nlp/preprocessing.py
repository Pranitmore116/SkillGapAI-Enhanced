"""
CSE472 Deep Learning for NLP - Module 1: Text Preprocessing Pipeline
Implements Unit I syllabus concepts:
- File Extraction (PDF, DOCX, TXT)
- Technical Term Protection (C++, C#, .NET, Node.js, CI/CD, etc.)
- Normalization, Case Folding, Whitespace Normalization
- Tokenization (Regex & NLTK-compatible)
- Stopword Removal (with Technical Skill Whitelist)
- Stemming (Porter Stemmer)
- Lemmatization (WordNet Lemmatizer)
- Out-of-Vocabulary (OOV) Handling
- N-gram Generation (Unigram, Bigram, Trigram)
- Offset & Span Mapping for Explainability
"""

import os
import re
import string
from collections import Counter
from typing import Dict, List, Tuple, Any, Optional

# File text extraction libraries
import PyPDF2
import docx

# NLTK imports with robust fallback if corpora are missing
try:
    import nltk
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.corpus import stopwords

    # Ensure required NLTK resources are available without throwing uncaught exceptions
    for resource in ['punkt', 'stopwords', 'wordnet', 'omw-1.4']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            pass
except ImportError:
    nltk = None
    PorterStemmer = None
    WordNetLemmatizer = None
    stopwords = None

# Comprehensive fallback stop words for standard English
FALLBACK_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

# Technical terms that must NEVER be stripped, stemmed, or split by punctuation
TECHNICAL_TERM_MAP = {
    r"(?i)(?<=[^a-zA-Z0-9+#])c\+\+(?=[^a-zA-Z0-9+#]|$)": "__TOKEN_CPP__",
    r"(?i)(?<=[^a-zA-Z0-9+#])c#(?=[^a-zA-Z0-9+#]|$)": "__TOKEN_CSHARP__",
    r"(?i)(?<=[^a-zA-Z0-9])\.net(?=[^a-zA-Z0-9]|$)": "__TOKEN_DOTNET__",
    r"(?i)(?<=[^a-zA-Z0-9])node\.js(?=[^a-zA-Z0-9]|$)": "__TOKEN_NODEJS__",
    r"(?i)(?<=[^a-zA-Z0-9])vue\.js(?=[^a-zA-Z0-9]|$)": "__TOKEN_VUEJS__",
    r"(?i)(?<=[^a-zA-Z0-9])next\.js(?=[^a-zA-Z0-9]|$)": "__TOKEN_NEXTJS__",
    r"(?i)(?<=[^a-zA-Z0-9])ci/cd(?=[^a-zA-Z0-9]|$)": "__TOKEN_CICD__",
    r"(?i)(?<=[^a-zA-Z0-9])rest api(?=[^a-zA-Z0-9]|$)": "__TOKEN_RESTAPI__",
    r"(?i)(?<=[^a-zA-Z0-9])restful api(?=[^a-zA-Z0-9]|$)": "__TOKEN_RESTFULAPI__",
    r"(?i)(?<=[^a-zA-Z0-9])spring boot(?=[^a-zA-Z0-9]|$)": "__TOKEN_SPRINGBOOT__",
    r"(?i)(?<=[^a-zA-Z0-9])power bi(?=[^a-zA-Z0-9]|$)": "__TOKEN_POWERBI__",
    r"(?i)(?<=[^a-zA-Z0-9])deep learning(?=[^a-zA-Z0-9]|$)": "__TOKEN_DEEPLEARNING__",
    r"(?i)(?<=[^a-zA-Z0-9])machine learning(?=[^a-zA-Z0-9]|$)": "__TOKEN_MACHINELEARNING__",
    r"(?i)(?<=[^a-zA-Z0-9])scikit-learn(?=[^a-zA-Z0-9]|$)": "__TOKEN_SCIKITLEARN__",
    r"(?i)(?<=[^a-zA-Z0-9])ruby on rails(?=[^a-zA-Z0-9]|$)": "__TOKEN_RUBYONRAILS__",
    r"(?i)(?<=[^a-zA-Z0-9])google cloud(?=[^a-zA-Z0-9]|$)": "__TOKEN_GOOGLECLOUD__",
    r"(?i)(?<=[^a-zA-Z0-9])amazon web services(?=[^a-zA-Z0-9]|$)": "__TOKEN_AWS_FULL__"
}

REVERSE_TECHNICAL_MAP = {v: k.replace(r"\b", "").replace(r"\.", ".").replace(r"\+", "+") for k, v in TECHNICAL_TERM_MAP.items()}
REVERSE_TECHNICAL_MAP["__TOKEN_CPP__"] = "c++"
REVERSE_TECHNICAL_MAP["__TOKEN_CSHARP__"] = "c#"
REVERSE_TECHNICAL_MAP["__TOKEN_DOTNET__"] = ".net"
REVERSE_TECHNICAL_MAP["__TOKEN_NODEJS__"] = "node.js"
REVERSE_TECHNICAL_MAP["__TOKEN_VUEJS__"] = "vue.js"
REVERSE_TECHNICAL_MAP["__TOKEN_NEXTJS__"] = "next.js"
REVERSE_TECHNICAL_MAP["__TOKEN_CICD__"] = "ci/cd"
REVERSE_TECHNICAL_MAP["__TOKEN_RESTAPI__"] = "rest api"
REVERSE_TECHNICAL_MAP["__TOKEN_RESTFULAPI__"] = "restful api"
REVERSE_TECHNICAL_MAP["__TOKEN_SPRINGBOOT__"] = "spring boot"
REVERSE_TECHNICAL_MAP["__TOKEN_POWERBI__"] = "power bi"
REVERSE_TECHNICAL_MAP["__TOKEN_DEEPLEARNING__"] = "deep learning"
REVERSE_TECHNICAL_MAP["__TOKEN_MACHINELEARNING__"] = "machine learning"
REVERSE_TECHNICAL_MAP["__TOKEN_SCIKITLEARN__"] = "scikit-learn"
REVERSE_TECHNICAL_MAP["__TOKEN_RUBYONRAILS__"] = "ruby on rails"
REVERSE_TECHNICAL_MAP["__TOKEN_GOOGLECLOUD__"] = "google cloud"
REVERSE_TECHNICAL_MAP["__TOKEN_AWS_FULL__"] = "amazon web services"

# Whitelist of terms that might coincide with stopwords or single chars but are valid skills
SKILL_WHITELIST = {"r", "c", "go", "git", "ai", "ml", "nlp", "sql", "aws", "gcp", "k8s"}


class TextPreprocessor:
    """
    Academic NLP Preprocessing Pipeline compliant with CSE472 Unit I.
    Provides modular, transparent, and step-by-step transformations.
    """

    def __init__(self):
        # Initialize stemmer and lemmatizer
        self.stemmer = PorterStemmer() if PorterStemmer else None
        self.lemmatizer = WordNetLemmatizer() if WordNetLemmatizer else None
        
        # Load stopwords
        self.stopwords = set()
        if stopwords:
            try:
                self.stopwords = set(stopwords.words('english'))
            except Exception:
                self.stopwords = set(FALLBACK_STOPWORDS)
        else:
            self.stopwords = set(FALLBACK_STOPWORDS)
            
        # Ensure whitelist is excluded from stopwords
        self.stopwords = self.stopwords - SKILL_WHITELIST

    @staticmethod
    def extract_from_file(file_path: str) -> str:
        """
        Extracts raw textual content from PDF, DOCX, or TXT formats.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        text = ""

        if ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported: PDF, DOCX, TXT.")

        return text.strip()

    def protect_technical_terms(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Substitutes technical terms with safe placeholders to prevent tokenization corruption.
        """
        protected_text = f" {text} "
        applied_replacements = {}
        for pattern, placeholder in TECHNICAL_TERM_MAP.items():
            matches = re.findall(pattern, protected_text)
            if matches:
                applied_replacements[placeholder] = matches[0]
                protected_text = re.sub(pattern, f" {placeholder} ", protected_text)
        return protected_text.strip(), applied_replacements

    def restore_technical_terms(self, tokens: List[str]) -> List[str]:
        """
        Restores protected placeholders back to canonical lowercase skill terms.
        """
        restored = []
        for t in tokens:
            if t in REVERSE_TECHNICAL_MAP:
                restored.append(REVERSE_TECHNICAL_MAP[t])
            else:
                restored.append(t)
        return restored

    def clean_text(self, text: str) -> str:
        """
        Normalizes whitespace and removes noise while protecting technical symbols.
        """
        if not text:
            return ""
        # Protect technical terms
        protected, _ = self.protect_technical_terms(text.lower())
        # Replace non-alphanumeric noise (keep placeholders, letters, numbers)
        cleaned = re.sub(r'[^a-zA-Z0-9_\s]', ' ', protected)
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Restore technical terms
        tokens = cleaned.split()
        restored_tokens = self.restore_technical_terms(tokens)
        return " ".join(restored_tokens)

    def tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        """
        Tokenizes text while tracking start and end character offsets for visualization and NER.
        """
        token_data = []
        # Protect technical terms in lowercased string
        protected, rep_map = self.protect_technical_terms(text)
        
        # Regex to find words or protected tokens
        pattern = re.compile(r'(__TOKEN_\w+__|[a-zA-Z0-9+#.]+)')
        for match in pattern.finditer(protected):
            token_str = match.group()
            start, end = match.span()
            canonical = REVERSE_TECHNICAL_MAP.get(token_str, token_str.lower())
            token_data.append({
                "token": canonical,
                "raw": token_str,
                "start": start,
                "end": end
            })
        return token_data

    def remove_stopwords(self, tokens: List[str]) -> Tuple[List[str], List[str]]:
        """
        Filters stop words while strictly preserving skill terms and whitelisted words.
        Returns: (filtered_tokens, removed_stopwords)
        """
        filtered = []
        removed = []
        for t in tokens:
            t_lower = t.lower()
            if t_lower in self.stopwords and t_lower not in SKILL_WHITELIST and t_lower not in REVERSE_TECHNICAL_MAP.values():
                removed.append(t)
            else:
                filtered.append(t)
        return filtered, removed

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Applies Porter Stemmer to tokens, avoiding technical protected words.
        """
        if not self.stemmer:
            return tokens
        stemmed = []
        for t in tokens:
            if t in REVERSE_TECHNICAL_MAP.values() or t in SKILL_WHITELIST:
                stemmed.append(t)
            else:
                stemmed.append(self.stemmer.stem(t))
        return stemmed

    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Applies WordNet Lemmatizer to tokens, reducing words to dictionary lemma.
        """
        if not self.lemmatizer:
            return tokens
        lemmatized = []
        for t in tokens:
            if t in REVERSE_TECHNICAL_MAP.values() or t in SKILL_WHITELIST:
                lemmatized.append(t)
            else:
                try:
                    lemmatized.append(self.lemmatizer.lemmatize(t))
                except Exception:
                    lemmatized.append(t)
        return lemmatized

    @staticmethod
    def generate_ngrams(tokens: List[str], n: int) -> List[str]:
        """
        Constructs n-grams (unigram n=1, bigram n=2, trigram n=3) from token sequence.
        """
        if n < 1 or len(tokens) < n:
            return []
        return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

    def process_document(self, text: str, min_term_freq: int = 1) -> Dict[str, Any]:
        """
        Executes the end-to-end preprocessing pipeline for Unit I text processing.
        Returns detailed academic representations for visualization and downstream matching.
        """
        raw_text = text or ""
        cleaned = self.clean_text(raw_text)
        
        # Token extraction with spans
        span_data = self.tokenize_with_spans(raw_text)
        raw_tokens = [d["token"] for d in span_data if d["token"].strip()]
        
        # Stopword filtering
        filtered_tokens, removed_stops = self.remove_stopwords(raw_tokens)
        
        # Morphological transformations
        stemmed = self.stem_tokens(filtered_tokens)
        lemmatized = self.lemmatize_tokens(filtered_tokens)
        
        # Term frequencies and vocabulary analysis
        freq_dist = Counter(lemmatized)
        top_terms = [{"term": term, "count": count} for term, count in freq_dist.most_common(20)]
        
        # OOV handling: Identify rare/hapax words
        oov_terms = [term for term, count in freq_dist.items() if count <= min_term_freq]
        
        # N-grams (Unigrams, Bigrams, Trigrams)
        unigrams = self.generate_ngrams(lemmatized, 1)
        bigrams = self.generate_ngrams(lemmatized, 2)
        trigrams = self.generate_ngrams(lemmatized, 3)

        return {
            "original_text": raw_text,
            "original_length": len(raw_text),
            "cleaned_text": cleaned,
            "cleaned_length": len(cleaned),
            "token_count": len(raw_tokens),
            "filtered_token_count": len(filtered_tokens),
            "tokens": raw_tokens,
            "filtered_tokens": filtered_tokens,
            "removed_stopwords": removed_stops,
            "removed_stopwords_count": len(removed_stops),
            "stemmed_tokens": stemmed,
            "lemmatized_tokens": lemmatized,
            "top_terms": top_terms,
            "vocabulary_size": len(freq_dist),
            "oov_terms_count": len(oov_terms),
            "oov_sample": oov_terms[:15],
            "unigram_count": len(unigrams),
            "bigram_count": len(bigrams),
            "trigram_count": len(trigrams),
            "sample_bigrams": bigrams[:10],
            "sample_trigrams": trigrams[:10]
        }
