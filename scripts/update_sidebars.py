import os
import re

files_to_update = [
    'SkillGapAI-Frontend/about.html',
    'SkillGapAI-Frontend/compare.html',
    'SkillGapAI-Frontend/dashboard.html',
    'SkillGapAI-Frontend/history.html',
    'SkillGapAI-Frontend/jobs.html',
    'SkillGapAI-Frontend/roadmap.html',
    'SkillGapAI-Frontend/settings.html'
]

nlp_links = '''                <a href="nlp-lab.html" class="side-link">
                    <span class="s-icon">🔬</span> <span class="s-text">NLP Lab</span>
                </a>
                <a href="methodology.html" class="side-link">
                    <span class="s-icon">🎓</span> <span class="s-text">Methodology</span>
                </a>
'''

for filepath in files_to_update:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'nlp-lab.html' in content:
        print(f"Already updated: {filepath}")
        continue
    
    # Match the history link block and insert right after it
    pattern = r'(<a href="history\.html" class="side-link[^"]*">.*?</a>\s*)'
    if re.search(pattern, content, re.DOTALL):
        updated_content = re.sub(pattern, r'\1' + nlp_links, content, count=1, flags=re.DOTALL)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Successfully updated: {filepath}")
    else:
        print(f"Pattern not found in: {filepath}")

