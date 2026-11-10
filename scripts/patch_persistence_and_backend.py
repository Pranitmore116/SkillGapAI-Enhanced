"""
patch_persistence_and_backend.py
Applies bulletproof cross-page session persistence, backend URL resolution with automatic fallback,
and seamless synchronization across Home, NLP Lab, Learning Paths (Roadmap), and Jobs.
"""
import os
import re

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'SkillGapAI-Frontend')

# ─────────────────────────────────────────────────────────────
# 1. PATCH app.js
# ─────────────────────────────────────────────────────────────
app_js_path = os.path.join(FRONTEND_DIR, 'js', 'app.js')
with open(app_js_path, 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace BACKEND_URL and getBackendBaseUrl if not present
if 'function getBackendBaseUrl()' not in app_js:
    app_js = app_js.replace(
        "const BACKEND_URL = 'http://127.0.0.1:5000/api/extract';",
        """function getBackendBaseUrl() {
    const host = window.location.hostname;
    if (host === 'localhost') return 'http://localhost:5000';
    if (host === '127.0.0.1') return 'http://127.0.0.1:5000';
    return 'http://127.0.0.1:5000';
}
const BACKEND_URL = getBackendBaseUrl() + '/api/extract';"""
    )

# Replace parseFile with resilient primary & fallback fetch
parse_file_old = re.search(r'async function parseFile\(file, jdText\) \{[\s\S]*?return \{ raw_text: rawText', app_js)
if parse_file_old:
    parse_file_replacement = """async function parseFile(file, jdText) {
    if (!file) throw new Error('No file provided.');
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'txt', 'docx'].includes(ext)) throw new Error(`Unsupported format: .${ext}. Use PDF or TXT.`);

    // Try backend first (with primary and fallback host)
    try {
        const formData = new FormData();
        formData.append('file', file);
        if (jdText) formData.append('jd_text', jdText);

        const primaryUrl = getBackendBaseUrl() + '/api/extract';
        const fallbackUrl = primaryUrl.includes('localhost') ? 'http://127.0.0.1:5000/api/extract' : 'http://localhost:5000/api/extract';

        let response = null;
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 8000);
            response = await fetch(primaryUrl, { method: 'POST', body: formData, signal: controller.signal });
            clearTimeout(tid);
        } catch (e1) {
            try {
                const controller2 = new AbortController();
                const tid2 = setTimeout(() => controller2.abort(), 8000);
                response = await fetch(fallbackUrl, { method: 'POST', body: formData, signal: controller2.signal });
                clearTimeout(tid2);
            } catch (e2) {
                // fall through to local fallback
            }
        }

        if (response && response.ok) {
            const data = await response.json();
            console.log('[SkillGapAI] Backend parse success');
            return data;
        }
    } catch (err) {
        console.warn('[SkillGapAI] Backend parse failed, using local fallback:', err.message);
    }

    // Local fallback
    let rawText = '';
    if (ext === 'pdf') {
        if (typeof pdfjsLib === 'undefined') throw new Error('PDF.js not loaded. Cannot parse PDF without backend running.');
        pdfjsLib.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;
        const buf = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            rawText += content.items.map(item => item.str).join(' ') + '\\n';
        }
        rawText = rawText.trim();
    } else {
        rawText = await file.text();
    }

    const cleaned = rawText.toLowerCase().replace(/[^a-zA-Z0-9\\s+#.]/g, ' ').replace(/\\s+/g, ' ').trim();
    const optimized = generateOptimizedResume(rawText, jdText || '');
    console.log('[SkillGapAI] Local fallback parsed, length:', cleaned.length);
    return { raw_text: rawText, cleaned_text: cleaned, optimized_text: optimized, keyword_skills: [], spacy_skills: [], bert_skills: [] };
}"""
    app_js = re.sub(r'async function parseFile\(file, jdText\) \{[\s\S]*?return \{ raw_text: rawText, cleaned_text: cleaned, optimized_text: optimized, keyword_skills: \[\], spacy_skills: \[\], bert_skills: \[\] \};\s*\}', lambda m: parse_file_replacement, app_js)

# Update performAnalysis to support restored resumeText & persist session
perform_analysis_match = re.search(r'async function performAnalysis\(\) \{[\s\S]*?populateDashboard\(results\);[\s\S]*?state\.analysisResult = results;[\s\S]*?try \{ saveAnalysis[\s\S]*?\} catch \(err\) \{', app_js)
if perform_analysis_match:
    updated_perform_analysis = """async function performAnalysis() {
    hideError();

    const activeTab = document.querySelector('.tab-btn.active')?.dataset?.tab || 'paste';
    const jdPasteText = ($('jd-textarea')?.value || '').trim();

    if (!state.resumeFile && !state.resumeText) { showError('Please upload your resume to begin.'); return; }
    if (activeTab === 'paste' && !jdPasteText) { showError('Please paste the job description.'); return; }
    if (activeTab === 'file' && !state.jdFile) { showError('Please upload the job description file.'); return; }

    showSection('loading-section');

    try {
        setLoaderStep(1, 'Extracting and parsing resume data...');
        const jdText = activeTab === 'paste' ? jdPasteText : null;
        let resumeData;
        if (state.resumeFile) {
            resumeData = await parseFile(state.resumeFile, jdText);
        } else if (state.resumeText) {
            resumeData = {
                raw_text: state.resumeText,
                cleaned_text: state.resumeText.toLowerCase().replace(/[^a-zA-Z0-9\\s+#.]/g, ' ').replace(/\\s+/g, ' ').trim(),
                optimized_text: generateOptimizedResume(state.resumeText, jdText || '')
            };
        }
        await new Promise(r => setTimeout(r, 700)); // Dramatic pause

        const rText = (resumeData.cleaned_text || resumeData.raw_text || resumeData.text || state.resumeText || '').trim();
        if (!rText || rText.length < 5) throw new Error('Resume content is too short or unreadable. Please check the file.');

        setLoaderStep(2, 'Mapping technical requirements from JD...');
        let jdData = jdText;
        if (activeTab === 'file' && state.jdFile) {
            const jdParsed = await parseFile(state.jdFile);
            jdData = jdParsed.cleaned_text || jdParsed.raw_text || jdParsed.text || '';
        }
        await new Promise(r => setTimeout(r, 800));

        setLoaderStep(3, 'Running NLP matching algorithms...');
        await new Promise(r => setTimeout(r, 1200)); // Heavy processing simulation

        const results = analyzeGap(resumeData, jdData);

        // Attach resume text to results so populateDashboard can display it
        results.raw_text = resumeData.raw_text || rText;
        results.optimized_text = resumeData.optimized_text || resumeData.raw_text || rText;

        setLoaderStep(4, 'Generating skill roadmap and dashboard...');
        await new Promise(r => setTimeout(r, 600));

        populateDashboard(results);
        state.analysisResult = results;
        state.resumeText = rText;
        state.jdText = jdData;
        state.resumeFileName = state.resumeFile ? state.resumeFile.name : (state.resumeFileName || 'Uploaded_Resume.pdf');
        state.resumeFileSize = state.resumeFile ? state.resumeFile.size : (state.resumeFileSize || 48000);

        // ── SAVE ANALYSIS SESSION TO STORAGE FOR NAVIGATION PERSISTENCE ──
        const activeSessionData = {
            results: results,
            resumeText: rText,
            jdText: jdData,
            resumeFileName: state.resumeFileName,
            resumeFileSize: state.resumeFileSize,
            jdFileName: state.jdFile ? state.jdFile.name : null,
            activeTab: activeTab,
            timestamp: Date.now()
        };
        try {
            sessionStorage.setItem('skillgap_active_analysis', JSON.stringify(activeSessionData));
            localStorage.setItem('skillgap_active_analysis', JSON.stringify(activeSessionData));
            console.log('[SkillGapAI] Active analysis session persisted successfully.');
        } catch (e) {
            console.warn('[SkillGapAI] Could not persist session:', e);
        }

        // Update top-nav buttons
        if ($('view-results-btn')) $('view-results-btn').style.display = 'none';
        if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'inline-flex';

        // Populate Academic NLP Deep Dive Visualizers (CSE472)
        if (window.nlpDashboard && typeof window.nlpDashboard.fetchAndPopulate === 'function') {
            window.nlpDashboard.fetchAndPopulate(rText, jdData, results.resumeSkills, results.jdSkills);
        }

        try { saveAnalysis(results, state.jdFile ? state.jdFile.name.replace(/\\.[^/.]+$/, '') : 'JD Analysis'); } catch (e) { }

    } catch (err) {"""
    app_js = app_js.replace(perform_analysis_match.group(0), updated_perform_analysis)

# Update DOMContentLoaded in app.js for automatic restoration
dom_loaded_marker = "console.log('[SkillGapAI] App initialized (non-module bundle)');"
dom_loaded_restoration = """console.log('[SkillGapAI] App initialized (non-module bundle)');

    // ── RESTORE PREVIOUS ANALYSIS SESSION ON PAGE NAVIGATION / LOAD ──
    try {
        const savedSessionStr = sessionStorage.getItem('skillgap_active_analysis') || localStorage.getItem('skillgap_active_analysis');
        if (savedSessionStr) {
            const saved = JSON.parse(savedSessionStr);
            if (saved && saved.results && saved.resumeText) {
                console.log('[SkillGapAI] Restoring active analysis session across navigation...');
                state.analysisResult = saved.results;
                state.resumeText = saved.resumeText;
                state.jdText = saved.jdText || '';
                state.resumeFileName = saved.resumeFileName || 'Resume.pdf';
                state.resumeFileSize = saved.resumeFileSize || 45000;

                // Restore JD textarea
                const jdTextarea = $('jd-textarea');
                if (jdTextarea && saved.jdText) {
                    jdTextarea.value = saved.jdText;
                    if ($('char-count')) $('char-count').textContent = saved.jdText.length;
                }

                // Restore uploaded resume file card in upload UI
                if ($('resume-drop-inner') && $('resume-success')) {
                    $('resume-drop-inner').style.display = 'none';
                    $('resume-success').style.display = 'flex';
                    if ($('resume-filename')) $('resume-filename').textContent = state.resumeFileName;
                    if ($('resume-filesize')) $('resume-filesize').textContent = formatSize(state.resumeFileSize);
                }

                // Show active session banner in upload section
                const banner = $('active-session-banner');
                if (banner) {
                    banner.style.display = 'flex';
                    const bannerText = $('active-session-banner-text');
                    if (bannerText) bannerText.textContent = `Active analysis for "${state.resumeFileName}" (${saved.results.matchPct}% match score).`;
                }

                // Show navigation buttons in header
                if ($('view-results-btn')) $('view-results-btn').style.display = 'inline-flex';
                if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'inline-flex';

                // Render dashboard with active results immediately
                populateDashboard(saved.results);

                // Restore Academic NLP Deep Dive
                const cachedNlpStr = sessionStorage.getItem('skillgap_nlp_deepdive');
                if (cachedNlpStr && window.nlpDashboard && typeof window.nlpDashboard.restoreFromCache === 'function') {
                    window.nlpDashboard.restoreFromCache(JSON.parse(cachedNlpStr));
                } else if (window.nlpDashboard && typeof window.nlpDashboard.fetchAndPopulate === 'function') {
                    window.nlpDashboard.fetchAndPopulate(saved.resumeText, saved.jdText, saved.results.resumeSkills, saved.results.jdSkills);
                }
            }
        }
    } catch (e) {
        console.warn('[SkillGapAI] Error restoring previous session:', e);
    }

    // Top-header and banner button listeners
    $('view-results-btn')?.addEventListener('click', () => {
        if (state.analysisResult) {
            showSection('results-section');
            if ($('view-results-btn')) $('view-results-btn').style.display = 'none';
            if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'inline-flex';
        }
    });

    $('banner-view-results-btn')?.addEventListener('click', () => {
        if (state.analysisResult) {
            showSection('results-section');
            if ($('view-results-btn')) $('view-results-btn').style.display = 'none';
            if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'inline-flex';
        }
    });

    document.querySelectorAll('.back-to-upload-btn, #back-to-upload-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            showSection('upload-section');
            if ($('view-results-btn')) $('view-results-btn').style.display = 'inline-flex';
            if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'none';
            const banner = $('active-session-banner');
            if (banner && state.analysisResult) banner.style.display = 'flex';
        });
    });

    $('banner-clear-btn')?.addEventListener('click', () => {
        if (confirm('Clear current analysis session and start fresh?')) {
            sessionStorage.removeItem('skillgap_active_analysis');
            localStorage.removeItem('skillgap_active_analysis');
            sessionStorage.removeItem('skillgap_nlp_deepdive');
            location.reload();
        }
    });"""

if dom_loaded_marker in app_js and 'RESTORE PREVIOUS ANALYSIS SESSION' not in app_js:
    app_js = app_js.replace(dom_loaded_marker, dom_loaded_restoration, 1)

# Update resetLogic to clear storage when user starts fresh
reset_logic_old = """    const resetLogic = () => {
        resetFile('resume'); resetFile('jd');
        if (jdTextarea) jdTextarea.value = '';
        if ($('char-count')) $('char-count').textContent = '0';
        document.querySelectorAll('.new-analysis-trigger, #new-analysis-btn').forEach(b => b.style.display = 'none');
        hideError();
        showSection('upload-section');
    };"""

reset_logic_new = """    const resetLogic = (fullClear = true) => {
        if (fullClear) {
            try {
                sessionStorage.removeItem('skillgap_active_analysis');
                localStorage.removeItem('skillgap_active_analysis');
                sessionStorage.removeItem('skillgap_nlp_deepdive');
            } catch (e) {}
            state.analysisResult = null;
            state.resumeText = null;
            state.jdText = null;
            resetFile('resume');
            resetFile('jd');
            if (jdTextarea) jdTextarea.value = '';
            if ($('char-count')) $('char-count').textContent = '0';
            const banner = $('active-session-banner');
            if (banner) banner.style.display = 'none';
            if ($('view-results-btn')) $('view-results-btn').style.display = 'none';
            if ($('back-to-upload-btn')) $('back-to-upload-btn').style.display = 'none';
        }
        document.querySelectorAll('.new-analysis-trigger, #new-analysis-btn').forEach(b => b.style.display = 'none');
        hideError();
        showSection('upload-section');
    };"""

if reset_logic_old in app_js:
    app_js = app_js.replace(reset_logic_old, reset_logic_new, 1)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(app_js)
print('Successfully patched SkillGapAI-Frontend/js/app.js')


# ─────────────────────────────────────────────────────────────
# 2. PATCH nlp-dashboard.js
# ─────────────────────────────────────────────────────────────
nlp_dash_path = os.path.join(FRONTEND_DIR, 'js', 'nlp-dashboard.js')
with open(nlp_dash_path, 'r', encoding='utf-8') as f:
    nlp_dash = f.read()

# Make API URL dynamic with fallback
dash_url_old = "const NLP_API_BASE = 'http://127.0.0.1:5000/api/nlp';"
dash_url_new = """function getNlpApiBase() {
    const host = window.location.hostname;
    if (host === 'localhost') return 'http://localhost:5000/api/nlp';
    if (host === '127.0.0.1') return 'http://127.0.0.1:5000/api/nlp';
    return 'http://127.0.0.1:5000/api/nlp';
}
const NLP_API_BASE = getNlpApiBase();

async function safeFetchJson(path, options = {}) {
    const primary = getNlpApiBase() + path;
    const fallbackBase = primary.includes('localhost') ? 'http://127.0.0.1:5000/api/nlp' : 'http://localhost:5000/api/nlp';
    const fallback = fallbackBase + path;

    try {
        const res = await fetch(primary, options);
        if (res.ok) return await res.json();
    } catch (e1) {
        try {
            const res2 = await fetch(fallback, options);
            if (res2.ok) return await res2.json();
        } catch (e2) {
            console.warn('[SkillGapAI] safeFetchJson failed for ' + path);
        }
    }
    return null;
}"""

if dash_url_old in nlp_dash:
    nlp_dash = nlp_dash.replace(dash_url_old, dash_url_new, 1)

# Upgrade fetchAndPopulate and add restoreFromCache
fetch_populate_old = re.search(r'async fetchAndPopulate\(resumeText, jdText, resumeSkills, jdSkills\) \{[\s\S]*?const nlpWrap = document\.getElementById\(\'nlp-deepdive-container\'\);[\s\S]*?if \(nlpWrap\) nlpWrap\.style\.display = \'block\';[\s\S]*?\} catch \(err\) \{[\s\S]*?\}', nlp_dash)
if fetch_populate_old:
    fetch_populate_new = """async fetchAndPopulate(resumeText, jdText, resumeSkills, jdSkills) {
        console.log('[SkillGapAI] Fetching multimodal NLP analysis from backend...');
        try {
            const [unifiedRes, pcaRes, benchmarkRes] = await Promise.all([
                safeFetchJson('/unified-analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume_text: resumeText, jd_text: jdText })
                }),
                safeFetchJson('/embeddings/visualize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        resume_skills: (resumeSkills || []).map(s => s.name || s),
                        jd_skills: (jdSkills || []).map(s => s.name || s),
                        architecture: 'cbow'
                    })
                }),
                safeFetchJson('/evaluation/benchmark')
            ]);

            if (unifiedRes) {
                this.nlpData = unifiedRes;
                this.renderPreprocessing(unifiedRes.preprocessing);
                this.renderTfidf(unifiedRes.approach_b_tfidf);
                this.renderEmbeddings(unifiedRes.approach_c_embeddings);
                this.renderBert(unifiedRes.approach_d_bert);
                this.renderUnifiedScore(unifiedRes.unified_evaluation);
            }

            if (pcaRes) {
                this.pcaData = pcaRes;
                this.renderPCAScatter('pcaCanvas', pcaRes);
            }

            if (benchmarkRes) {
                this.renderBenchmarkTable(benchmarkRes);
            }

            // Cache deep dive results in sessionStorage for instant return on navigation
            if (unifiedRes || pcaRes || benchmarkRes) {
                try {
                    sessionStorage.setItem('skillgap_nlp_deepdive', JSON.stringify({
                        unifiedRes,
                        pcaRes,
                        benchmarkRes,
                        timestamp: Date.now()
                    }));
                } catch (e) {}
            }

            const nlpWrap = document.getElementById('nlp-deepdive-container');
            if (nlpWrap) nlpWrap.style.display = 'block';

        } catch (err) {
            console.warn('[SkillGapAI] NLP deep dive fetch error:', err);
            const nlpWrap = document.getElementById('nlp-deepdive-container');
            if (nlpWrap) nlpWrap.style.display = 'block';
        }
    },

    restoreFromCache(cached) {
        if (!cached) return;
        console.log('[SkillGapAI] Restoring Academic NLP Deep Dive from cache...');
        if (cached.unifiedRes) {
            this.nlpData = cached.unifiedRes;
            this.renderPreprocessing(cached.unifiedRes.preprocessing);
            this.renderTfidf(cached.unifiedRes.approach_b_tfidf);
            this.renderEmbeddings(cached.unifiedRes.approach_c_embeddings);
            this.renderBert(cached.unifiedRes.approach_d_bert);
            this.renderUnifiedScore(cached.unifiedRes.unified_evaluation);
        }
        if (cached.pcaRes) {
            this.pcaData = cached.pcaRes;
            this.renderPCAScatter('pcaCanvas', cached.pcaRes);
        }
        if (cached.benchmarkRes) {
            this.renderBenchmarkTable(cached.benchmarkRes);
        }
        const nlpWrap = document.getElementById('nlp-deepdive-container');
        if (nlpWrap) nlpWrap.style.display = 'block';
    }"""
    nlp_dash = nlp_dash.replace(fetch_populate_old.group(0), fetch_populate_new)

# Update Analogy and Custom BERT events in nlp-dashboard.js to use safeFetchJson
nlp_dash = nlp_dash.replace(
    "const res = await fetch(`${NLP_API_BASE}/embeddings/analogy`, {",
    "const data = await safeFetchJson('/embeddings/analogy', {"
)
nlp_dash = nlp_dash.replace(
    "const res = await fetch(`${NLP_API_BASE}/bert/extract`, {",
    "const data = await safeFetchJson('/bert/extract', {"
)

with open(nlp_dash_path, 'w', encoding='utf-8') as f:
    f.write(nlp_dash)
print('Successfully patched SkillGapAI-Frontend/js/nlp-dashboard.js')


# ─────────────────────────────────────────────────────────────
# 3. PATCH nlp-lab.js
# ─────────────────────────────────────────────────────────────
nlp_lab_path = os.path.join(FRONTEND_DIR, 'js', 'nlp-lab.js')
with open(nlp_lab_path, 'r', encoding='utf-8') as f:
    nlp_lab = f.read()

# Make BACKEND_URL resilient with auto-retry
lab_backend_old = "const BACKEND_URL = (window.location.hostname === 'localhost') ? 'http://localhost:5000' : 'http://127.0.0.1:5000';"
lab_backend_new = """function getBackendUrl() {
    const host = window.location.hostname;
    if (host === 'localhost') return 'http://localhost:5000';
    if (host === '127.0.0.1') return 'http://127.0.0.1:5000';
    return 'http://127.0.0.1:5000';
}
const BACKEND_URL = getBackendUrl();

async function fetchBackend(path, options = {}) {
    const primary = getBackendUrl() + path;
    const secondaryBase = primary.includes('localhost') ? 'http://127.0.0.1:5000' : 'http://localhost:5000';
    const secondary = secondaryBase + path;

    try {
        const resp = await fetch(primary, options);
        if (resp.ok) return resp;
        throw new Error('HTTP ' + resp.status);
    } catch (e1) {
        try {
            const resp2 = await fetch(secondary, options);
            if (resp2.ok) return resp2;
            throw new Error('HTTP ' + resp2.status);
        } catch (e2) {
            throw new Error('Failed to fetch from backend on port 5000. Ensure start_skillgap_backend.bat is running.');
        }
    }
}

async function checkBackendHealth() {
    const statusEl = document.getElementById('lab-backend-status');
    try {
        const resp = await fetchBackend('/api/health');
        const data = await resp.json();
        if (statusEl) {
            statusEl.innerHTML = '<span class="pulse-dot" style="background:#10b981;"></span> <span style="color:#10b981;font-weight:700;">Backend Online (Port 5000)</span>';
        }
        return true;
    } catch (e) {
        if (statusEl) {
            statusEl.innerHTML = '<span class="pulse-dot" style="background:#ef4444;"></span> <span style="color:#ef4444;font-weight:700;">Backend Offline</span> <button id="btn-retry-backend" style="background:transparent;border:1px solid var(--danger);color:var(--danger);padding:2px 8px;border-radius:4px;cursor:pointer;font-size:0.75rem;margin-left:6px;">Retry</button>';
            document.getElementById('btn-retry-backend')?.addEventListener('click', () => {
                checkBackendHealth().then(ok => {
                    if (ok) {
                        loadEmbeddingVisualization();
                        loadBertModelInfo();
                        loadBenchmarkTable();
                    }
                });
            });
        }
        return false;
    }
}"""

if lab_backend_old in nlp_lab:
    nlp_lab = nlp_lab.replace(lab_backend_old, lab_backend_new, 1)

# Replace fetch calls with fetchBackend
nlp_lab = re.sub(r'fetch\(`\$\{BACKEND_URL\}(/api/nlp/[^`]+)`', r'fetchBackend(`\1`', nlp_lab)
nlp_lab = re.sub(r'fetch\(`\$\{BACKEND_URL\}(/api/health)`', r'fetchBackend(`\1`', nlp_lab)

# In initSampleLoaders, inject active uploaded resume and JD from session storage
sample_loader_search = "const samples = {"
sample_loader_inject = """// Check for active uploaded resume / JD from Home session
    const savedActiveStr = sessionStorage.getItem('skillgap_active_analysis') || localStorage.getItem('skillgap_active_analysis');
    let activeResumeText = null;
    let activeJdText = null;
    let activeResumeName = 'Uploaded Resume';
    if (savedActiveStr) {
        try {
            const savedActive = JSON.parse(savedActiveStr);
            activeResumeText = savedActive.resumeText;
            activeJdText = savedActive.jdText;
            activeResumeName = savedActive.resumeFileName || 'Uploaded Resume';
        } catch (e) {}
    }

    const samples = {
        active_resume: activeResumeText || `Senior Full-Stack Engineer with 5+ years of experience in Python, Flask, React, and PostgreSQL. Developed microservices deployed on AWS using Docker, Kubernetes, and automated CI/CD pipelines. Proficient in Node.js, C++, and Redis caching. Strong background in Git, REST APIs, and Agile development.`,
        active_jd: activeJdText || `We are looking for a Senior Software Engineer to build scalable cloud backends. Required skills: Python, Flask, FastAPI, PostgreSQL, Docker, AWS, and Git. Experience with Kubernetes, Redis, and modern CI/CD practices is highly desirable. Candidates should have solid object-oriented programming skills in Python or C++.`,"""

if sample_loader_search in nlp_lab and 'savedActiveStr' not in nlp_lab:
    nlp_lab = nlp_lab.replace(sample_loader_search, sample_loader_inject, 1)

# In DOMContentLoaded of nlp-lab.js, invoke checkBackendHealth
dom_nlp_lab_old = "document.addEventListener('DOMContentLoaded', () => {\n    initTabs();"
dom_nlp_lab_new = "document.addEventListener('DOMContentLoaded', () => {\n    checkBackendHealth();\n    initTabs();"
if dom_nlp_lab_old in nlp_lab:
    nlp_lab = nlp_lab.replace(dom_nlp_lab_old, dom_nlp_lab_new, 1)

with open(nlp_lab_path, 'w', encoding='utf-8') as f:
    f.write(nlp_lab)
print('Successfully patched SkillGapAI-Frontend/js/nlp-lab.js')


# ─────────────────────────────────────────────────────────────
# 4. PATCH index.html (Header buttons + Active Session Banner)
# ─────────────────────────────────────────────────────────────
index_html_path = os.path.join(FRONTEND_DIR, 'index.html')
with open(index_html_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

# Header buttons
header_old = """            <!-- Header area for New Analysis button if needed -->
            <header class="top-header" style="display: flex; justify-content: flex-end; padding: 1rem 2rem;">
                <button class="btn-ghost" id="new-analysis-btn" style="display:none;">↩ New Analysis</button>
            </header>"""

header_new = """            <!-- Header area for New Analysis and Navigation buttons -->
            <header class="top-header" style="display: flex; justify-content: flex-end; gap: 10px; padding: 1rem 2rem; align-items: center;">
                <button class="btn-ghost back-to-upload-btn" id="back-to-upload-btn" style="display:none;">✏️ Edit Resume / JD</button>
                <button class="btn-primary" id="view-results-btn" style="display:none;">📊 View Analysis Results</button>
                <button class="btn-ghost" id="new-analysis-btn" style="display:none;">🔄 New Analysis</button>
            </header>"""

if header_old in index_html:
    index_html = index_html.replace(header_old, header_new, 1)

# Active session banner right after hero
banner_html = """
                    <!-- Active Session Reminder Banner -->
                    <div id="active-session-banner" style="display:none; background:linear-gradient(135deg, rgba(16,185,129,0.12), rgba(99,102,241,0.12)); border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:14px 20px; margin-bottom:24px; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:1.5rem;">⚡</span>
                            <div>
                                <div style="font-weight:700; color:var(--t1); font-size:0.95rem;">Active Analysis Session Available</div>
                                <div style="color:var(--t2); font-size:0.8rem;" id="active-session-banner-text">Resume and job requirements are currently analyzed.</div>
                            </div>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button id="banner-view-results-btn" class="btn-primary" style="padding:6px 14px; font-size:0.85rem;">View Results Dashboard →</button>
                            <button id="banner-clear-btn" class="btn-ghost" style="padding:6px 14px; font-size:0.85rem; color:var(--danger); border-color:var(--danger);">Start Fresh</button>
                        </div>
                    </div>
"""

if '<!-- Active Session Reminder Banner -->' not in index_html:
    index_html = index_html.replace('<!-- Upload Cards -->', banner_html + '\n                    <!-- Upload Cards -->', 1)

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(index_html)
print('Successfully patched SkillGapAI-Frontend/index.html')


# ─────────────────────────────────────────────────────────────
# 5. PATCH nlp-lab.html (Status Indicator in Hero + Active Session buttons)
# ─────────────────────────────────────────────────────────────
nlp_lab_html_path = os.path.join(FRONTEND_DIR, 'nlp-lab.html')
with open(nlp_lab_html_path, 'r', encoding='utf-8') as f:
    nlp_lab_html = f.read()

# Add status pill in lab-hero
hero_btn_old = """                <div style="display: flex; gap: 10px;">
                    <a href="methodology.html" class="btn-primary" style="text-decoration:none; display:inline-flex; align-items:center; gap:8px;">
                        <span>🎓 View Academic Syllabus Guide</span>
                    </a>
                </div>"""

hero_btn_new = """                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <div id="lab-backend-status" style="display:inline-flex; align-items:center; gap:8px; background:var(--bg3); border:1px solid var(--border); padding:8px 14px; border-radius:10px; font-size:0.85rem; font-weight:600;">
                        <span class="pulse-dot"></span> Checking backend status...
                    </div>
                    <a href="methodology.html" class="btn-primary" style="text-decoration:none; display:inline-flex; align-items:center; gap:8px;">
                        <span>🎓 View Academic Syllabus Guide</span>
                    </a>
                </div>"""

if hero_btn_old in nlp_lab_html:
    nlp_lab_html = nlp_lab_html.replace(hero_btn_old, hero_btn_new, 1)

# Add active resume / active JD sample buttons to Module 1, Module 2, Module 4
module1_samples_old = """                    <div class="sample-btn-group">
                        <button class="sample-pill prep-sample-btn" data-sample="resume_snippet">📄 Full Stack Resume</button>
                        <button class="sample-pill prep-sample-btn" data-sample="jd_snippet">📋 Cloud Engineer JD</button>
                        <button class="sample-pill prep-sample-btn" data-sample="ml_snippet">🤖 Machine Learning Profile</button>
                    </div>"""

module1_samples_new = """                    <div class="sample-btn-group">
                        <button class="sample-pill prep-sample-btn" data-sample="active_resume" style="border-color:var(--accent);color:var(--accent-lt);font-weight:700;">📄 My Uploaded Resume</button>
                        <button class="sample-pill prep-sample-btn" data-sample="active_jd" style="border-color:var(--accent);color:var(--accent-lt);font-weight:700;">📋 My Uploaded JD</button>
                        <button class="sample-pill prep-sample-btn" data-sample="resume_snippet">Full Stack Sample</button>
                        <button class="sample-pill prep-sample-btn" data-sample="ml_snippet">ML Profile Sample</button>
                    </div>"""

if module1_samples_old in nlp_lab_html:
    nlp_lab_html = nlp_lab_html.replace(module1_samples_old, module1_samples_new, 1)

# Module 4 sample buttons
module4_samples_old = """                    <div class="sample-btn-group">
                        <button class="sample-pill bert-sample-btn" data-sample="resume_snippet">Full Stack Sentence</button>
                        <button class="sample-pill bert-sample-btn" data-sample="ml_snippet">ML & Transformers Sentence</button>
                    </div>"""

module4_samples_new = """                    <div class="sample-btn-group">
                        <button class="sample-pill bert-sample-btn" data-sample="active_resume" style="border-color:var(--accent);color:var(--accent-lt);font-weight:700;">📄 My Uploaded Resume</button>
                        <button class="sample-pill bert-sample-btn" data-sample="resume_snippet">Full Stack Sentence</button>
                        <button class="sample-pill bert-sample-btn" data-sample="ml_snippet">ML & Transformers Sentence</button>
                    </div>"""

if module4_samples_old in nlp_lab_html:
    nlp_lab_html = nlp_lab_html.replace(module4_samples_old, module4_samples_new, 1)

with open(nlp_lab_html_path, 'w', encoding='utf-8') as f:
    f.write(nlp_lab_html)
print('Successfully patched SkillGapAI-Frontend/nlp-lab.html')


# ─────────────────────────────────────────────────────────────
# 6. PATCH roadmap.html (Sync with active analysis)
# ─────────────────────────────────────────────────────────────
roadmap_path = os.path.join(FRONTEND_DIR, 'roadmap.html')
with open(roadmap_path, 'r', encoding='utf-8') as f:
    roadmap_html = f.read()

roadmap_old = """        document.addEventListener('DOMContentLoaded', () => {
            const historyData = JSON.parse(localStorage.getItem('skillgap_history') || '[]');
            const grid = document.getElementById('roadmapGrid');

            if (historyData.length > 0) {
                const latest = historyData[0]; // Latest unshifted to front
                const recs = latest.recommendations || [];"""

roadmap_new = """        document.addEventListener('DOMContentLoaded', () => {
            const activeStr = sessionStorage.getItem('skillgap_active_analysis') || localStorage.getItem('skillgap_active_analysis');
            const historyData = JSON.parse(localStorage.getItem('skillgap_history') || '[]');
            const grid = document.getElementById('roadmapGrid');

            let recs = [];
            let sourceName = '';

            if (activeStr) {
                try {
                    const active = JSON.parse(activeStr);
                    if (active && active.results && active.results.recommendations) {
                        recs = active.results.recommendations;
                        sourceName = active.resumeFileName ? ` (for ${active.resumeFileName})` : '';
                    }
                } catch (e) {}
            }

            if (recs.length === 0 && historyData.length > 0) {
                const latest = historyData[0];
                recs = latest.recommendations || [];
            }

            if (recs && recs.length > 0) {"""

if roadmap_old in roadmap_html:
    roadmap_html = roadmap_html.replace(roadmap_old, roadmap_new, 1)

with open(roadmap_path, 'w', encoding='utf-8') as f:
    f.write(roadmap_html)
print('Successfully patched SkillGapAI-Frontend/roadmap.html')


# ─────────────────────────────────────────────────────────────
# 7. PATCH jobs.html (Sync with active analysis)
# ─────────────────────────────────────────────────────────────
jobs_path = os.path.join(FRONTEND_DIR, 'jobs.html')
with open(jobs_path, 'r', encoding='utf-8') as f:
    jobs_html = f.read()

jobs_old = """        document.addEventListener('DOMContentLoaded', () => {
            const history = JSON.parse(localStorage.getItem('skillgap_history') || '[]');
            
            // Clean up the role title if it exists
            let cleanTitle = (history[0]?.role || 'Software Engineer')"""

jobs_new = """        document.addEventListener('DOMContentLoaded', () => {
            const activeStr = sessionStorage.getItem('skillgap_active_analysis') || localStorage.getItem('skillgap_active_analysis');
            const history = JSON.parse(localStorage.getItem('skillgap_history') || '[]');

            let activeData = null;
            if (activeStr) {
                try { activeData = JSON.parse(activeStr); } catch (e) {}
            }

            // Clean up the role title if it exists
            let cleanTitle = (activeData?.jdFileName || history[0]?.role || 'Software Engineer')"""

if jobs_old in jobs_html:
    jobs_html = jobs_html.replace(jobs_old, jobs_new, 1)

# Also update matched / missing in jobs.html to check activeData
jobs_vars_old = """            const matched = history[0].matched || ['React', 'Node.js', 'Python'];
            const missing = history[0].missing || ['Docker', 'AWS', 'Kubernetes'];"""

jobs_vars_new = """            const matched = (activeData?.results?.matched || []).map(s => s.name || s).length > 0
                ? (activeData.results.matched || []).map(s => s.name || s)
                : (history[0]?.matched || ['React', 'Node.js', 'Python']);
            const missing = (activeData?.results?.missing || []).map(s => s.name || s).length > 0
                ? (activeData.results.missing || []).map(s => s.name || s)
                : (history[0]?.missing || ['Docker', 'AWS', 'Kubernetes']);"""

if jobs_vars_old in jobs_html:
    jobs_html = jobs_html.replace(jobs_vars_old, jobs_vars_new, 1)

jobs_match_old = "const match1 = history[0].matchPct || 88;"
jobs_match_new = "const match1 = activeData?.results?.matchPct || history[0]?.matchPct || 88;"
if jobs_match_old in jobs_html:
    jobs_html = jobs_html.replace(jobs_match_old, jobs_match_new, 1)

with open(jobs_path, 'w', encoding='utf-8') as f:
    f.write(jobs_html)
print('Successfully patched SkillGapAI-Frontend/jobs.html')
