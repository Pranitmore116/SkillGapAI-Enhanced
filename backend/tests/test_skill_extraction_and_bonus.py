"""
Verification and Quality Assurance Tests for:
1. BERT Contextual Skill Extraction
2. Technical Skill Validation & Negative Filtering
3. Bonus Skills Detection and Consistency
4. Evidence Isolation (No Full-Resume Paragraphs)
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.skill_validator import SkillValidator
from nlp.bert_extractor import BertSkillExtractor
from nlp.unified_matcher import UnifiedNLPMatcher
from resume_skill_extractor import process_resume


SAMPLE_ANIT_RESUME = """
Anit More
Email: anitmore116@gmail.com | Phone: 8010725929 | Location: Solapur, India
LinkedIn: linkedin.com/in/anitmore
Education: Secondary Education at Navodaya Madhyamik Vidyalaya (Apr 2018 - Mar 2020)
Skills: Python, Java, React, Docker, Kubernetes, AWS, SQL
Experience: Designed an end-to-end machine learning pipeline using Python, Pandas and scikit-learn.
Architected resilient microservices with Spring Boot and PostgreSQL.
Automated CI/CD workflows and deployments with Docker and AWS.
"""

SAMPLE_JOB_DESCRIPTION = """
We are looking for a Senior Software Engineer with strong experience in:
- Python and React for modern web platforms
- PostgreSQL and SQL for database modeling
- Docker and AWS for cloud deployments
- Spring Boot microservices
Nice to have: Machine Learning or data analysis knowledge.
"""


def test_negative_filter_excludes_personal_info_and_noise():
    """Verify that names, emails, phone numbers, schools, locations, and noise are rejected."""
    invalid_inputs = [
        "8010725929", "91", "03", "116",
        "anit", "Anit", "Anit More", "anitmore", "anitmore116",
        "anitmore116@gmail.com", "gmail", "Gmail", "linkedin", "Linkedin", "linkedin.com/in/anitmore",
        "Solapur", "solapur", "Pune", "India",
        "Navodaya", "Madhyamik", "Vidyalaya", "Navodaya Madhyamik Vidyalaya",
        "Apr", "Aug", "Mar", "Jan", "2020", "2018",
        "A", "D", "In", "One", "And", "The", "With", "Using",
        "*", "+", "-", "•", "@",
        "Skills", "Technical Skills", "Education", "Experience"
    ]
    for term in invalid_inputs:
        result = SkillValidator.validate_and_canonicalize(term)
        assert result is None, f"Expected '{term}' to be rejected, but got: {result}"


def test_positive_technical_skills_recognition():
    """Verify that legitimate technical skills across domains are validated with canonical names."""
    valid_skills = {
        "python": "Python",
        "Python 3": "Python",
        "react.js": "React",
        "react": "React",
        "docker": "Docker",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "spring boot": "Spring Boot",
        "c++": "C++",
        "c#": "C#",
        "node.js": "Node.js",
        "aws": "AWS",
        "postgresql": "PostgreSQL",
        "machine learning": "Machine Learning",
        "ci/cd": "CI/CD"
    }
    for alias, expected_canonical in valid_skills.items():
        result = SkillValidator.validate_and_canonicalize(alias)
        assert result is not None, f"Expected '{alias}' to be recognized as valid technical skill."
        assert result["name"] == expected_canonical, f"Expected canonical '{expected_canonical}', got '{result['name']}'"
        assert "category" in result and result["category"]


def test_bert_extraction_on_user_resume():
    """
    Verify BERT extractor on the user's actual resume content:
    - No personal info, phone numbers, emails, schools, dates appear.
    - Real technical skills are extracted.
    - Contextual evidence contains only the short relevant sentence.
    """
    extractor = BertSkillExtractor()
    entities = extractor.extract_skills_contextual(SAMPLE_ANIT_RESUME)

    entity_names = [e["entity"] for e in entities]
    lower_names = [e.lower() for e in entity_names]

    # Verify NO garbage entities
    for forbidden in ["anit", "more", "anitmore", "8010725929", "solapur", "navodaya", "madhyamik", "gmail", "linkedin", "apr", "mar"]:
        assert forbidden not in lower_names, f"Forbidden entity '{forbidden}' detected in BERT output!"

    # Verify genuine skills are present
    assert "Python" in entity_names
    assert "React" in entity_names
    assert "Docker" in entity_names
    assert "AWS" in entity_names
    assert "SQL" in entity_names
    assert "scikit-learn" in entity_names
    assert "Spring Boot" in entity_names

    # Verify no duplicates
    assert len(entity_names) == len(set(entity_names)), "Duplicate entities detected in BERT extraction!"

    # Verify contextual evidence is concise (NOT the whole resume)
    for ent in entities:
        evidence = ent.get("context_sentence", "")
        assert len(evidence) > 0, f"Missing evidence for {ent['entity']}"
        assert len(evidence) <= 180, f"Evidence sentence too long for {ent['entity']}: '{evidence}'"
        assert "Anit More" not in evidence or "Skills:" in evidence, "Evidence contaminated with unrelated resume headers"


def test_bonus_skills_calculation_and_consistency():
    """
    Verify the three skill groups are calculated consistently and correctly:
    - Matched Skills = Resume ∩ JD
    - Missing Skills = JD − Resume
    - Bonus Skills   = Resume − JD
    """
    extractor = BertSkillExtractor()
    resume_entities = extractor.extract_skills_contextual(SAMPLE_ANIT_RESUME)
    jd_entities = extractor.extract_skills_contextual(SAMPLE_JOB_DESCRIPTION)

    resume_skills = [e["entity"] for e in resume_entities]
    jd_skills = [e["entity"] for e in jd_entities]

    gap = SkillValidator.calculate_skill_gap(resume_skills, jd_skills)

    matched = set(gap["matched_skills"])
    missing = set(gap["missing_skills"])
    bonus = set(gap["bonus_skills"])
    res_set = set(gap["resume_valid_skills"])
    jd_set = set(gap["jd_valid_skills"])

    # Mathematical consistency checks
    assert matched.issubset(res_set), "Matched skills must be a subset of resume skills."
    assert matched.issubset(jd_set), "Matched skills must be a subset of JD skills."
    assert matched.isdisjoint(bonus), "Matched skills and Bonus skills must be disjoint."
    assert matched.isdisjoint(missing), "Matched skills and Missing skills must be disjoint."
    assert bonus.isdisjoint(jd_set), "Bonus skills must NOT be in JD skills."
    assert missing.isdisjoint(res_set), "Missing skills must NOT be in Resume skills."
    assert matched.union(bonus) == res_set, "Matched ∪ Bonus must equal Resume skills."
    assert matched.union(missing) == jd_set, "Matched ∪ Missing must equal JD skills."

    # Verify Bonus skills count is reliable and clean
    assert gap["bonus_count"] == len(gap["bonus_skills"])
    for forbidden in ["anit", "8010725929", "solapur", "navodaya", "madhyamik", "apr", "mar", "gmail"]:
        assert forbidden not in [b.lower() for b in gap["bonus_skills"]], f"Forbidden term '{forbidden}' in bonus skills!"


def test_unified_matcher_consistency():
    """Verify that UnifiedNLPMatcher uses the same validated representation."""
    matcher = UnifiedNLPMatcher()
    results = matcher.analyze_resume_and_jd(SAMPLE_ANIT_RESUME, SAMPLE_JOB_DESCRIPTION)

    bert_sec = results["approach_d_bert"]
    assert "resume_entities" in bert_sec
    assert "matched_entities" in bert_sec
    assert "missing_entities" in bert_sec
    assert "bonus_entities" in bert_sec

    bert_resume_names = [e["entity"].lower() for e in bert_sec["resume_entities"]]
    for forbidden in ["8010725929", "anit", "solapur", "navodaya", "gmail"]:
        assert forbidden not in bert_resume_names

