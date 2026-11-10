
import json
from resume_skill_extractor import process_resume

# Create a test resume that definitely has skills
test_resume = "I am an expert in Python, Java, React, and AWS. I use Docker and Kubernetes for DevOps. I also know SQL and MongoDB."

with open('test_resume_full.txt', 'w') as f:
    f.write(test_resume)

try:
    jd_text = "Looking for a Python developer with React and AWS experience."
    output = process_resume('test_resume_full.txt', jd_text=jd_text)
    data = json.loads(output)
    print("Keyword Skills:", data.get('keyword_skills'))
    print("SpaCy Skills:", data.get('spacy_skills'))
    print("BERT Skills:", data.get('bert_skills'))
except Exception as e:
    print(f"FAILED: {e}")
finally:
    import os
    if os.path.exists('test_resume_full.txt'):
        os.remove('test_resume_full.txt')
