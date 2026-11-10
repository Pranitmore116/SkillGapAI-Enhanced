with open('SkillGapAI-Frontend/js/nlp-lab.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """    // TF-IDF sample loaders
    const loadTfidfSampleBtn = document.getElementById('btn-load-tfidf-sample');"""

repl = """    // TF-IDF sample loaders
    const loadActivePairBtn = document.getElementById('btn-load-active-pair');
    if (loadActivePairBtn) {
        if (!activeResumeText && !activeJdText) {
            loadActivePairBtn.style.opacity = '0.6';
            loadActivePairBtn.title = 'No active analysis session found. Analyze a resume on Home first!';
        }
        loadActivePairBtn.addEventListener('click', () => {
            const resInput = document.getElementById('tfidf-resume-input');
            const jdInput = document.getElementById('tfidf-jd-input');
            if (resInput) resInput.value = samples.active_resume;
            if (jdInput) jdInput.value = samples.active_jd;
        });
    }

    const loadTfidfSampleBtn = document.getElementById('btn-load-tfidf-sample');"""

if target in text:
    text = text.replace(target, repl, 1)
    with open('SkillGapAI-Frontend/js/nlp-lab.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated nlp-lab.js with active pair loader!')
else:
    print('target not found in nlp-lab.js')

