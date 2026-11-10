"""
SkillGap AI - Centralized Skill Taxonomy and Validation Engine
Provides unified technical skill representation, validation, normalization,
and negative filtering across all NLP components (BERT, Rule-based, Word2Vec, TF-IDF).
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# 1. CANONICAL TECHNICAL SKILL TAXONOMY
# Comprehensive ontology spanning core software & data engineering domains.
# ─────────────────────────────────────────────────────────────────────────────

CANONICAL_SKILLS: Dict[str, Dict[str, Any]] = {
    # ── Programming Languages ──
    "Python": {"category": "Languages", "aliases": ["python", "python3", "python 3", "py"]},
    "Java": {"category": "Languages", "aliases": ["java", "core java", "j2ee", "jdk"]},
    "JavaScript": {"category": "Languages", "aliases": ["javascript", "js", "ecmascript", "es6"]},
    "TypeScript": {"category": "Languages", "aliases": ["typescript", "ts"]},
    "C++": {"category": "Languages", "aliases": ["c++", "cpp"]},
    "C#": {"category": "Languages", "aliases": ["c#", "csharp", "c sharp", ".net c#"]},
    "C": {"category": "Languages", "aliases": ["c programming", "c language"]},
    "Go": {"category": "Languages", "aliases": ["go", "golang"]},
    "Rust": {"category": "Languages", "aliases": ["rust", "rust-lang"]},
    "Ruby": {"category": "Languages", "aliases": ["ruby", "ruby-lang"]},
    "PHP": {"category": "Languages", "aliases": ["php", "php7", "php8"]},
    "Swift": {"category": "Languages", "aliases": ["swift"]},
    "Kotlin": {"category": "Languages", "aliases": ["kotlin"]},
    "Scala": {"category": "Languages", "aliases": ["scala"]},
    "R": {"category": "Languages", "aliases": ["r programming", "r language", "r-lang"]},
    "MATLAB": {"category": "Languages", "aliases": ["matlab"]},
    "Dart": {"category": "Languages", "aliases": ["dart"]},
    "Bash": {"category": "Languages", "aliases": ["bash", "shell scripting", "shell script", "sh"]},
    "SQL": {"category": "Databases", "aliases": ["sql", "structured query language", "ansi sql"]},

    # ── Frontend Frameworks & Libraries ──
    "React": {"category": "Frontend", "aliases": ["react", "react.js", "reactjs"]},
    "Angular": {"category": "Frontend", "aliases": ["angular", "angularjs", "angular 2+"]},
    "Vue.js": {"category": "Frontend", "aliases": ["vue", "vue.js", "vuejs"]},
    "Next.js": {"category": "Frontend", "aliases": ["next.js", "nextjs", "next"]},
    "Nuxt.js": {"category": "Frontend", "aliases": ["nuxt.js", "nuxt", "nuxtjs"]},
    "HTML5": {"category": "Frontend", "aliases": ["html", "html5"]},
    "CSS3": {"category": "Frontend", "aliases": ["css", "css3"]},
    "Tailwind CSS": {"category": "Frontend", "aliases": ["tailwind", "tailwind css", "tailwindcss"]},
    "Bootstrap": {"category": "Frontend", "aliases": ["bootstrap", "bootstrap 5"]},
    "Sass": {"category": "Frontend", "aliases": ["sass", "scss"]},
    "Redux": {"category": "Frontend", "aliases": ["redux", "redux toolkit"]},
    "Webpack": {"category": "Frontend", "aliases": ["webpack"]},
    "Vite": {"category": "Frontend", "aliases": ["vite", "vite.js"]},

    # ── Backend Frameworks & Runtimes ──
    "Node.js": {"category": "Backend", "aliases": ["node.js", "nodejs", "node"]},
    "Express.js": {"category": "Backend", "aliases": ["express.js", "expressjs", "express"]},
    "Django": {"category": "Backend", "aliases": ["django", "django rest framework", "drf"]},
    "Flask": {"category": "Backend", "aliases": ["flask", "flask framework"]},
    "FastAPI": {"category": "Backend", "aliases": ["fastapi", "fast api"]},
    "Spring Boot": {"category": "Backend", "aliases": ["spring boot", "spring", "spring framework", "spring mvc"]},
    "Laravel": {"category": "Backend", "aliases": ["laravel"]},
    "Ruby on Rails": {"category": "Backend", "aliases": ["rails", "ruby on rails"]},
    "ASP.NET": {"category": "Backend", "aliases": ["asp.net", "asp.net core", ".net", ".net core"]},
    "NestJS": {"category": "Backend", "aliases": ["nestjs", "nest.js"]},
    "REST API": {"category": "Backend", "aliases": ["rest api", "rest apis", "restful", "restful api", "restful apis", "rest"]},
    "GraphQL": {"category": "Backend", "aliases": ["graphql"]},
    "gRPC": {"category": "Backend", "aliases": ["grpc"]},
    "Microservices": {"category": "Backend", "aliases": ["microservices", "microservice", "microservice architecture"]},

    # ── Databases & Storage ──
    "PostgreSQL": {"category": "Databases", "aliases": ["postgresql", "postgres", "psql"]},
    "MySQL": {"category": "Databases", "aliases": ["mysql"]},
    "MongoDB": {"category": "Databases", "aliases": ["mongodb", "mongo"]},
    "Redis": {"category": "Databases", "aliases": ["redis"]},
    "SQLite": {"category": "Databases", "aliases": ["sqlite", "sqlite3"]},
    "Oracle": {"category": "Databases", "aliases": ["oracle db", "oracle database"]},
    "Cassandra": {"category": "Databases", "aliases": ["cassandra", "apache cassandra"]},
    "DynamoDB": {"category": "Databases", "aliases": ["dynamodb", "aws dynamodb"]},
    "Elasticsearch": {"category": "Databases", "aliases": ["elasticsearch", "elastic search", "elk"]},
    "Firebase": {"category": "Databases", "aliases": ["firebase", "firestore"]},
    "NoSQL": {"category": "Databases", "aliases": ["nosql", "non-relational database"]},

    # ── Cloud & DevOps ──
    "AWS": {"category": "Cloud & DevOps", "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"]},
    "Azure": {"category": "Cloud & DevOps", "aliases": ["azure", "microsoft azure"]},
    "Google Cloud": {"category": "Cloud & DevOps", "aliases": ["google cloud", "gcp", "google cloud platform"]},
    "Docker": {"category": "Cloud & DevOps", "aliases": ["docker", "containerization", "containers"]},
    "Kubernetes": {"category": "Cloud & DevOps", "aliases": ["kubernetes", "k8s"]},
    "Terraform": {"category": "Cloud & DevOps", "aliases": ["terraform"]},
    "Ansible": {"category": "Cloud & DevOps", "aliases": ["ansible"]},
    "Jenkins": {"category": "Cloud & DevOps", "aliases": ["jenkins"]},
    "CI/CD": {"category": "Cloud & DevOps", "aliases": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment"]},
    "GitHub Actions": {"category": "Cloud & DevOps", "aliases": ["github actions"]},
    "GitLab CI": {"category": "Cloud & DevOps", "aliases": ["gitlab ci", "gitlab ci/cd"]},
    "Linux": {"category": "Cloud & DevOps", "aliases": ["linux", "ubuntu", "debian", "centos", "redhat"]},
    "Nginx": {"category": "Cloud & DevOps", "aliases": ["nginx"]},

    # ── Data & Machine Learning / AI ──
    "Machine Learning": {"category": "Data & AI", "aliases": ["machine learning", "ml", "statistical learning"]},
    "Deep Learning": {"category": "Data & AI", "aliases": ["deep learning", "dl", "neural networks"]},
    "NLP": {"category": "Data & AI", "aliases": ["nlp", "natural language processing", "text processing"]},
    "Computer Vision": {"category": "Data & AI", "aliases": ["computer vision", "cv", "image processing"]},
    "PyTorch": {"category": "Data & AI", "aliases": ["pytorch", "torch"]},
    "TensorFlow": {"category": "Data & AI", "aliases": ["tensorflow", "tf", "keras"]},
    "scikit-learn": {"category": "Data & AI", "aliases": ["scikit-learn", "scikitlearn", "scikit learn", "sklearn"]},
    "Pandas": {"category": "Data & AI", "aliases": ["pandas"]},
    "NumPy": {"category": "Data & AI", "aliases": ["numpy"]},
    "Data Analysis": {"category": "Data & AI", "aliases": ["data analysis", "data analytics"]},
    "Data Science": {"category": "Data & AI", "aliases": ["data science"]},
    "Apache Spark": {"category": "Data & AI", "aliases": ["spark", "apache spark", "pyspark"]},
    "Hadoop": {"category": "Data & AI", "aliases": ["hadoop", "apache hadoop"]},
    "Tableau": {"category": "Data & AI", "aliases": ["tableau"]},
    "Power BI": {"category": "Data & AI", "aliases": ["power bi", "powerbi"]},
    "Transformers": {"category": "Data & AI", "aliases": ["transformers", "huggingface", "hugging face", "bert"]},
    "Large Language Models": {"category": "Data & AI", "aliases": ["llms", "large language models", "llm", "genai", "generative ai"]},

    # ── Mobile & Cross-Platform ──
    "React Native": {"category": "Mobile", "aliases": ["react native", "react-native"]},
    "Flutter": {"category": "Mobile", "aliases": ["flutter"]},
    "Android": {"category": "Mobile", "aliases": ["android development", "android sdk", "android"]},
    "iOS": {"category": "Mobile", "aliases": ["ios development", "ios sdk", "ios"]},

    # ── Tools & Methodologies ──
    "Git": {"category": "Tools", "aliases": ["git", "version control", "vcs"]},
    "GitHub": {"category": "Tools", "aliases": ["github"]},
    "GitLab": {"category": "Tools", "aliases": ["gitlab"]},
    "Jira": {"category": "Tools", "aliases": ["jira"]},
    "Figma": {"category": "Tools", "aliases": ["figma"]},
    "Postman": {"category": "Tools", "aliases": ["postman"]},
    "Jest": {"category": "Tools", "aliases": ["jest"]},
    "Pytest": {"category": "Tools", "aliases": ["pytest"]},
    "Selenium": {"category": "Tools", "aliases": ["selenium"]},
    "Agile": {"category": "Methodologies", "aliases": ["agile", "agile methodologies", "agile methodology"]},
    "Scrum": {"category": "Methodologies", "aliases": ["scrum", "scrum master", "sprints"]},
    "DevOps": {"category": "Methodologies", "aliases": ["devops", "devsecops"]},
    "TDD": {"category": "Methodologies", "aliases": ["tdd", "test-driven development", "test driven development"]},
    "OOP": {"category": "Methodologies", "aliases": ["oop", "object oriented programming", "object-oriented programming"]},

    # ── Soft Skills / Professional Competencies ──
    "Leadership": {"category": "Soft Skills", "aliases": ["leadership", "team lead", "technical lead"]},
    "Communication": {"category": "Soft Skills", "aliases": ["communication", "verbal communication", "written communication"]},
    "Problem Solving": {"category": "Soft Skills", "aliases": ["problem solving", "analytical skills", "critical thinking"]},
    "Teamwork": {"category": "Soft Skills", "aliases": ["teamwork", "collaboration", "cross-functional collaboration"]},
    "Project Management": {"category": "Soft Skills", "aliases": ["project management", "project planning"]}
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. BLACKLISTS & REGEX FOR INVALID CANDIDATES
# ─────────────────────────────────────────────────────────────────────────────

# Exact lowercase blacklist terms that must NEVER be treated as technical skills
EXACT_BLACKLIST: Set[str] = {
    # Personal names / usernames mentioned in user prompt or resumes
    "anit", "more", "anitmore", "anitmore116", "linkedin", "gmail", "yahoo", "outlook", "hotmail",
    # Locations
    "solapur", "pune", "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata",
    "maharashtra", "karnataka", "india", "usa", "california", "new york", "london", "remote",
    # Educational institutions, degrees, exams
    "navodaya", "madhyamik", "vidyalaya", "school", "high school", "college", "university", "institute",
    "btech", "be", "bsc", "bca", "mtech", "ms", "mca", "hsc", "ssc", "cbse", "icse", "board",
    "cgpa", "gpa", "percentage", "marks", "degree", "diploma", "bachelor", "master",
    # Dates / Months / Years / Time
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "january", "february", "march", "april", "june", "july", "august", "september", "october", "november", "december",
    "present", "current", "duration", "year", "years", "month", "months",
    # Ordinary English words / Prepositions / Stop words / Resume boilerplate
    "a", "d", "in", "one", "two", "three", "first", "second", "third",
    "and", "the", "with", "using", "for", "to", "of", "on", "at", "by", "from", "as", "is", "are", "was", "were",
    "strong", "proficient", "proficiency", "experience", "experienced", "developer", "engineer", "lead", "junior", "senior",
    "candidate", "role", "job", "responsibilities", "responsible", "working", "worked", "built", "designed", "created",
    "skills", "skill", "technical skills", "key skills", "core skills", "summary", "profile", "contact", "education",
    "projects", "project", "work", "team", "code", "system", "systems", "application", "applications", "software",
    "solution", "solutions", "hands", "hand", "knowledge", "understanding", "familiar", "familiarity",
    "required", "preferred", "plus", "desired", "qualifications", "requirements", "about", "me"
}

# Regex patterns for pure noise
PHONE_PATTERN = re.compile(r'^(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,6}$')
DIGIT_ONLY_PATTERN = re.compile(r'^\d+$')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
URL_PATTERN = re.compile(r'(https?://|www\.|linkedin\.com|github\.com)[^\s]+', re.IGNORECASE)
SYMBOL_ONLY_PATTERN = re.compile(r'^[^a-zA-Z0-9+#.]+$')


class SkillValidator:
    """
    Centralized validation and normalization engine for technical skills.
    Ensures absolute consistency across BERT NER, rule-based matching,
    and gap analysis (matched, missing, bonus).
    """

    _alias_to_canonical: Dict[str, Tuple[str, str]] = {}

    @classmethod
    def _initialize_index(cls):
        if cls._alias_to_canonical:
            return

        # Index built-in canonical skills
        for can_name, info in CANONICAL_SKILLS.items():
            cat = info["category"]
            cls._alias_to_canonical[can_name.lower()] = (can_name, cat)
            for alias in info.get("aliases", []):
                cls._alias_to_canonical[alias.lower()] = (can_name, cat)

        # Merge with external skill_ontology.json if present
        ontology_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skill_ontology.json')
        if os.path.exists(ontology_path):
            try:
                with open(ontology_path, 'r', encoding='utf-8') as f:
                    ont = json.load(f)
                    for item in ont.get("skills", []):
                        name = item.get("name")
                        cat = item.get("category", "Technical")
                        if name:
                            cls._alias_to_canonical[name.lower()] = (name, cat)
                            for a in item.get("aliases", []):
                                cls._alias_to_canonical[a.lower()] = (name, cat)
            except Exception:
                pass

    @classmethod
    def clean_token(cls, raw: str) -> str:
        """Strips leading/trailing punctuation and symbols while preserving C++, C#, .NET."""
        text = raw.strip()
        # Remove surrounding quotes, brackets, colons, bullets, asterisks
        text = re.sub(r'^[•\-\*\+\,\.\:\;\"\'\(\)\[\]\{\}\|\/\\]+', '', text)
        text = re.sub(r'[\,\.\:\;\"\'\(\)\[\]\{\}\|\/\\]+$', '', text)
        return text.strip()

    @classmethod
    def is_invalid_candidate(cls, text: str) -> bool:
        """
        Determines whether a candidate string is definitely NOT a skill
        (e.g., numbers, personal info, emails, locations, dates, noise).
        """
        cleaned = cls.clean_token(text)
        if not cleaned:
            return True

        lower = cleaned.lower()

        # Check blacklist
        if lower in EXACT_BLACKLIST:
            return True

        # Check length & character constraints
        # Single characters: only 'C' and 'R' are valid programming languages
        if len(cleaned) == 1 and lower not in {"c", "r"}:
            return True

        # Symbols only (e.g. "*", "+", "---")
        if SYMBOL_ONLY_PATTERN.match(cleaned):
            return True

        # All digits or phone number
        if DIGIT_ONLY_PATTERN.match(cleaned) or PHONE_PATTERN.match(cleaned):
            return True

        # Email or URL
        if "@" in cleaned or EMAIL_PATTERN.search(cleaned) or URL_PATTERN.search(cleaned):
            return True

        # Contains numbers mixed with words that look like usernames (e.g., anitmore116)
        if re.match(r'^[a-zA-Z]+[0-9]+$', cleaned) and lower not in {"html5", "css3", "es6", "k8s", "j2ee", "s3", "ec2"}:
            return True

        # Standard file paths or web extensions
        if lower.endswith((".com", ".org", ".net", ".edu", ".gov", ".io", ".pdf", ".txt", ".docx")):
            return True

        return False

    @classmethod
    def validate_and_canonicalize(cls, candidate: str) -> Optional[Dict[str, str]]:
        """
        Validates whether a candidate string represents a legitimate technical skill.
        If valid, returns standard dictionary: {"name": CanonicalName, "category": Category}
        If invalid, returns None.
        """
        cls._initialize_index()

        cleaned = cls.clean_token(candidate)
        if cls.is_invalid_candidate(cleaned):
            return None

        lower = cleaned.lower()

        # 1. Exact match against known aliases / canonical names
        if lower in cls._alias_to_canonical:
            can_name, cat = cls._alias_to_canonical[lower]
            return {"name": can_name, "category": cat}

        # 2. Check hyphenated vs spaced variations (e.g., "scikit learn" -> "scikit-learn")
        normalized_variant = lower.replace("-", " ")
        if normalized_variant in cls._alias_to_canonical:
            can_name, cat = cls._alias_to_canonical[normalized_variant]
            return {"name": can_name, "category": cat}

        normalized_hyphen = lower.replace(" ", "-")
        if normalized_hyphen in cls._alias_to_canonical:
            can_name, cat = cls._alias_to_canonical[normalized_hyphen]
            return {"name": can_name, "category": cat}

        # 3. Strip trailing punctuation like dot (e.g., "Python." -> "Python")
        clean_dot = lower.rstrip('.')
        if clean_dot in cls._alias_to_canonical:
            can_name, cat = cls._alias_to_canonical[clean_dot]
            return {"name": can_name, "category": cat}

        return None

    @classmethod
    def clean_evidence_sentence(cls, sentence: str, skill_name: str, max_length: int = 150) -> str:
        """
        Produces a concise, readable 1-2 sentence contextual evidence snippet.
        Guarantees that the snippet never contains an entire resume or paragraph.
        """
        if not sentence:
            return ""

        # Normalize spaces and newlines
        clean_sent = " ".join(sentence.strip().split())

        # If sentence is reasonably short, return directly
        if len(clean_sent) <= max_length:
            return clean_sent

        # If sentence is long, extract the clause/window around the skill
        lower_sent = clean_sent.lower()
        lower_skill = skill_name.lower()
        pos = lower_sent.find(lower_skill)
        if pos != -1:
            half = (max_length - len(skill_name)) // 2
            start = max(0, pos - half)
            end = min(len(clean_sent), pos + len(skill_name) + half)

            # Snap to word boundaries
            if start > 0:
                first_space = clean_sent.find(" ", start)
                if first_space != -1 and first_space < pos:
                    start = first_space + 1
            if end < len(clean_sent):
                last_space = clean_sent.rfind(" ", pos + len(skill_name), end)
                if last_space != -1:
                    end = last_space

            snippet = clean_sent[start:end].strip()
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(clean_sent) else ""
            return f"{prefix}{snippet}{suffix}"

        return clean_sent[:max_length].rsplit(" ", 1)[0] + "..."

    @classmethod
    def extract_valid_skills_from_text(cls, text: str) -> List[Dict[str, str]]:
        """
        Extracts validated skills from text using regex boundary matching
        against canonical taxonomy. Multi-word skills take precedence over single words.
        """
        cls._initialize_index()
        if not text:
            return []

        # Sort candidate aliases by length (descending) to match multi-word skills first
        # (e.g. 'scikit-learn' before 'learn', 'spring boot' before 'spring')
        sorted_aliases = sorted(cls._alias_to_canonical.keys(), key=lambda s: len(s), reverse=True)

        found_canonical: Dict[str, Dict[str, str]] = {}
        text_padded = f" {text.lower()} "

        # Replace non-word chars with spaces except + and # for C++, C#
        text_search = re.sub(r'[^a-zA-Z0-9+#.-]', ' ', text_padded)

        for alias in sorted_aliases:
            can_name, cat = cls._alias_to_canonical[alias]
            if can_name in found_canonical:
                continue

            # Strict word boundary check
            escaped_alias = re.escape(alias)
            pattern = rf'(?<![a-zA-Z0-9]){escaped_alias}(?![a-zA-Z0-9])'

            if re.search(pattern, text_search):
                found_canonical[can_name] = {"name": can_name, "category": cat}

        return list(found_canonical.values())

    @classmethod
    def calculate_skill_gap(
        cls,
        resume_skill_names: List[str],
        jd_skill_names: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates consistent, normalized skill groups:
        - Matched Skills = Resume ∩ JD
        - Missing Skills = JD − Resume
        - Bonus Skills   = Resume − JD
        """
        cls._initialize_index()

        # Canonicalize resume skills
        res_map: Dict[str, Dict[str, str]] = {}
        for s in resume_skill_names:
            v = cls.validate_and_canonicalize(s)
            if v:
                res_map[v["name"]] = v

        # Canonicalize JD skills
        jd_map: Dict[str, Dict[str, str]] = {}
        for s in jd_skill_names:
            v = cls.validate_and_canonicalize(s)
            if v:
                jd_map[v["name"]] = v

        res_keys = set(res_map.keys())
        jd_keys = set(jd_map.keys())

        matched_keys = sorted(list(res_keys.intersection(jd_keys)))
        missing_keys = sorted(list(jd_keys.difference(res_keys)))
        bonus_keys = sorted(list(res_keys.difference(jd_keys)))

        return {
            "matched_skills": [res_map[k]["name"] for k in matched_keys],
            "missing_skills": [jd_map[k]["name"] for k in missing_keys],
            "bonus_skills": [res_map[k]["name"] for k in bonus_keys],
            "matched_count": len(matched_keys),
            "missing_count": len(missing_keys),
            "bonus_count": len(bonus_keys),
            "resume_valid_skills": [res_map[k]["name"] for k in sorted(list(res_keys))],
            "jd_valid_skills": [jd_map[k]["name"] for k in sorted(list(jd_keys))]
        }

