/**
 * SkillGapAI — Smart Resume Suggestions Engine
 * Detects weak verbs, missing sections, no metrics, passive voice
 */
'use strict';

const WEAK_VERBS = [
    'helped', 'worked', 'did', 'made', 'used', 'got', 'went', 'said', 'put', 'took',
    'tried', 'had', 'was', 'were', 'is', 'are', 'be', 'been', 'being', 'involved',
    'responsible for', 'assisted', 'supported', 'participated', 'handled'
];

const POWER_VERBS = {
    'helped': 'Spearheaded',
    'worked': 'Engineered',
    'made': 'Developed',
    'used': 'Leveraged',
    'got': 'Achieved',
    'tried': 'Executed',
    'involved': 'Directed',
    'responsible for': 'Oversaw',
    'assisted': 'Contributed to',
    'supported': 'Streamlined',
    'participated': 'Collaborated on',
    'handled': 'Managed',
};

const REQUIRED_SECTIONS = [
    { key: 'summary', labels: ['summary', 'objective', 'profile', 'about me'], tip: 'Add a Professional Summary (3-4 lines) showing your value proposition.' },
    { key: 'experience', labels: ['experience', 'work history', 'employment', 'career'], tip: 'Add a Work Experience section with bullet points using power verbs + metrics.' },
    { key: 'education', labels: ['education', 'degree', 'university', 'college'], tip: 'Add an Education section with degree, institution, and year.' },
    { key: 'skills', labels: ['skills', 'technologies', 'tech stack', 'expertise'], tip: 'Add a Skills section listing technical and soft skills relevant to the role.' },
    { key: 'projects', labels: ['project', 'portfolio', 'built', 'created'], tip: 'Add a Projects section with 2-3 showcase projects that prove your skills.' },
];

const METRIC_PATTERNS = [
    /\d+\s*%/,
    /\$[\d,]+/,
    /\d+\+?\s*(users|customers|clients|employees|team members|engineers|projects|systems)/i,
    /\d+x\s*(faster|improvement|increase|growth|revenue)/i,
    /saved\s+\$?[\d,]+/i,
    /increased\s+.+\d+/i,
    /reduced\s+.+\d+/i,
    /grew\s+.+\d+/i,
    /delivered\s+\d+/i,
    /managed\s+\$?[\d,]+/i,
];

/**
 * Main entry — analyse resumeText and return suggestions array
 */
function analyzeResumeSuggestions(resumeText, jdText) {
    if (!resumeText || resumeText.length < 20) return [];

    const lower = resumeText.toLowerCase();
    const suggestions = [];

    // ── 1. Weekly Verbs ───────────────────────────────────────────────
    const weakFound = [];
    WEAK_VERBS.forEach(verb => {
        const re = new RegExp('\\b' + verb + '\\b', 'gi');
        const matches = resumeText.match(re);
        if (matches && matches.length > 0) {
            weakFound.push({ verb, count: matches.length, power: POWER_VERBS[verb] || 'a stronger action verb' });
        }
    });
    if (weakFound.length > 0) {
        suggestions.push({
            type: 'weak-verbs',
            severity: 'high',
            title: 'Weak Action Verbs Detected',
            description: `Found ${weakFound.length} weak verb(s): ${weakFound.slice(0, 4).map(v => `"${v.verb}"`).join(', ')}${weakFound.length > 4 ? '...' : ''}.`,
            fixes: weakFound.slice(0, 3).map(v => `Replace "${v.verb}" with "${v.power}"`),
            icon: 'alert',
        });
    }

    // ── 2. Missing Sections ───────────────────────────────────────────
    const missingSections = [];
    REQUIRED_SECTIONS.forEach(sec => {
        const found = sec.labels.some(lbl => lower.includes(lbl));
        if (!found) missingSections.push(sec);
    });
    if (missingSections.length > 0) {
        suggestions.push({
            type: 'missing-sections',
            severity: missingSections.length >= 2 ? 'high' : 'medium',
            title: 'Missing Resume Sections',
            description: `Your resume may be missing: ${missingSections.map(s => s.key.charAt(0).toUpperCase() + s.key.slice(1)).join(', ')}.`,
            fixes: missingSections.map(s => s.tip),
            icon: 'sections',
        });
    }

    // ── 3. Missing Quantitative Metrics ──────────────────────────────
    const hasMetrics = METRIC_PATTERNS.some(p => p.test(resumeText));
    if (!hasMetrics) {
        suggestions.push({
            type: 'no-metrics',
            severity: 'high',
            title: 'No Quantifiable Achievements',
            description: 'Recruiters look for numbers. Your resume lacks measurable impact like percentages, dollar values, or user counts.',
            fixes: [
                'Add metrics: "Optimized query performance by 40%"',
                'Quantify scale: "Built a system serving 10,000+ daily users"',
                'Show impact: "Reduced deployment time from 2 hours to 15 minutes"',
            ],
            icon: 'metrics',
        });
    }

    // ── 4. Length Check ───────────────────────────────────────────────
    const wordCount = resumeText.split(/\s+/).length;
    if (wordCount < 200) {
        suggestions.push({
            type: 'too-short',
            severity: 'medium',
            title: 'Resume Too Short',
            description: `Only ~${wordCount} words detected. A strong resume typically has 400–700 words.`,
            fixes: [
                'Expand your work experience bullet points',
                'Add a projects section with 2-3 described projects',
                'Include technical details (tools, scale, impact)',
            ],
            icon: 'length',
        });
    } else if (wordCount > 900) {
        suggestions.push({
            type: 'too-long',
            severity: 'low',
            title: 'Resume May Be Too Long',
            description: `~${wordCount} words detected. Aim for one page (400–700 words) for most roles.`,
            fixes: [
                'Remove roles older than 8–10 years',
                'Cut redundant bullet points — keep only the strongest ones',
                'Summarize older positions in 1–2 lines',
            ],
            icon: 'length',
        });
    }

    // ── 5. Contact Info Check ─────────────────────────────────────────
    const hasEmail = /@\w+\.\w+/.test(resumeText);
    const hasPhone = /\+?\d[\d\s\-().]{8,}/.test(resumeText);
    if (!hasEmail || !hasPhone) {
        suggestions.push({
            type: 'contact',
            severity: 'medium',
            title: 'Incomplete Contact Information',
            description: `Missing: ${!hasEmail ? 'email address' : ''}${!hasEmail && !hasPhone ? ' and ' : ''}${!hasPhone ? 'phone number' : ''}.`,
            fixes: [
                'Add your professional email (e.g., name@gmail.com)',
                'Add your phone number and LinkedIn profile URL',
            ],
            icon: 'contact',
        });
    }

    // ── 6. JD Keyword Gaps (if JD provided) ──────────────────────────
    if (jdText && jdText.length > 50) {
        const jdLower = jdText.toLowerCase();
        const importantJdWords = jdLower
            .split(/\W+/)
            .filter(w => w.length > 5)
            .filter(w => !['position', 'company', 'looking', 'should', 'would', 'could', 'about', 'years', 'required', 'preferred'].includes(w));

        const freq = {};
        importantJdWords.forEach(w => { freq[w] = (freq[w] || 0) + 1; });
        const topJdWords = Object.entries(freq)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 15)
            .map(([w]) => w)
            .filter(w => !lower.includes(w));

        if (topJdWords.length >= 3) {
            suggestions.push({
                type: 'jd-keywords',
                severity: 'medium',
                title: 'Missing JD Keywords (ATS Risk)',
                description: `${topJdWords.length} frequent JD terms not found in your resume. ATS may filter you out.`,
                fixes: topJdWords.slice(0, 5).map(w => `Naturally incorporate "${w}" into your experience or skills`),
                icon: 'keywords',
            });
        }
    }

    return suggestions;
}

/**
 * Renders suggestion cards into a container element
 */
function renderSuggestions(suggestions, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!suggestions || suggestions.length === 0) {
        container.innerHTML = `
            <div class="sug-empty">
                <div class="sug-empty-icon">&#10003;</div>
                <div class="sug-empty-title">Great Job!</div>
                <div class="sug-empty-desc">No major resume issues detected. Your resume looks well-structured.</div>
            </div>`;
        return;
    }

    const iconMap = {
        alert: '&#9888;',
        sections: '&#9995;',
        metrics: '&#8470;',
        length: '&#9992;',
        contact: '&#9993;',
        keywords: '&#10006;',
    };

    const severityLabel = { high: 'Critical', medium: 'Suggested', low: 'Optional' };
    const severityClass = { high: 'sug-high', medium: 'sug-med', low: 'sug-low' };

    container.innerHTML = suggestions.map((s, i) => `
        <div class="sug-card ${severityClass[s.severity]}" style="animation-delay:${i * 0.08}s">
            <div class="sug-header">
                <div class="sug-icon-wrap ${severityClass[s.severity]}-bg">
                    <span class="sug-icon">${iconMap[s.icon] || '!'}</span>
                </div>
                <div class="sug-head-text">
                    <div class="sug-title">${s.title}</div>
                    <span class="sug-badge ${severityClass[s.severity]}-badge">${severityLabel[s.severity]}</span>
                </div>
            </div>
            <p class="sug-desc">${s.description}</p>
            ${s.fixes && s.fixes.length ? `
            <div class="sug-fixes">
                <div class="sug-fixes-label">How to fix:</div>
                <ul class="sug-fix-list">
                    ${s.fixes.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>` : ''}
        </div>
    `).join('');
}
