/**
 * SkillGapAI — Resume Comparison Mode
 * Compare two resumes against the same JD
 */
'use strict';

function compareResumes(data1, data2, name1, name2) {
    const scores = [
        { label: 'Match Score', v1: data1.matchPct, v2: data2.matchPct },
        { label: 'ATS Score', v1: data1.atsPct, v2: data2.atsPct },
        { label: 'Market Readiness', v1: data1.marketReadinessPct, v2: data2.marketReadinessPct },
        { label: 'Skill Diversity', v1: data1.skillDiversityPct, v2: data2.skillDiversityPct },
        { label: 'Skills Matched', v1: (data1.matched || []).length, v2: (data2.matched || []).length, isCount: true },
        { label: 'Skills Missing', v1: (data1.missing || []).length, v2: (data2.missing || []).length, isCount: true, lowerBetter: true },
        { label: 'Bonus Skills', v1: (data1.extra || []).length, v2: (data2.extra || []).length, isCount: true },
    ];

    const winner = data1.matchPct >= data2.matchPct ? name1 : name2;
    const margin = Math.abs(data1.matchPct - data2.matchPct);

    const uniqueToR1 = (data1.matched || []).filter(s => !(data2.matched || []).some(s2 => s2.name === s.name));
    const uniqueToR2 = (data2.matched || []).filter(s => !(data1.matched || []).some(s1 => s1.name === s.name));
    const sharedSkills = (data1.matched || []).filter(s => (data2.matched || []).some(s2 => s2.name === s.name));

    return { scores, winner, margin, uniqueToR1, uniqueToR2, sharedSkills, name1, name2, data1, data2 };
}

function renderComparePanel(result, containerId) {
    const el = document.getElementById(containerId);
    if (!el || !result) return;

    const { scores, winner, margin, uniqueToR1, uniqueToR2, sharedSkills, name1, name2 } = result;

    const badge = v1 => v1 > 0 ? `<span class="cmp-winner-badge">Winner</span>` : '';

    el.innerHTML = `
    <div class="cmp-wrap">

        <div class="cmp-verdict">
            <div class="cmp-verdict-icon">&#9654;</div>
            <div>
                <div class="cmp-verdict-title">${winner} leads by ${margin}%</div>
                <div class="cmp-verdict-sub">${margin === 0 ? 'Both resumes are equally matched!' : `${winner} is the stronger candidate for this role.`}</div>
            </div>
        </div>

        <div class="cmp-header-row">
            <div class="cmp-col cmp-label-col"></div>
            <div class="cmp-col cmp-r1-head">${name1}</div>
            <div class="cmp-col cmp-r2-head">${name2}</div>
        </div>

        ${scores.map(s => {
        const v1Better = s.lowerBetter ? s.v1 < s.v2 : s.v1 > s.v2;
        const v2Better = s.lowerBetter ? s.v2 < s.v1 : s.v2 > s.v1;
        const barMax = s.isCount ? Math.max(s.v1, s.v2, 1) : 100;
        return `
            <div class="cmp-row">
                <div class="cmp-col cmp-row-label">${s.label}</div>
                <div class="cmp-col cmp-val-col ${v1Better ? 'cmp-winner' : ''}">
                    <div class="cmp-val">${s.v1}${s.isCount ? '' : '%'} ${v1Better ? badge(1) : ''}</div>
                    <div class="cmp-bar-track"><div class="cmp-bar cmp-bar-r1" style="width:${Math.round(s.v1 / barMax * 100)}%"></div></div>
                </div>
                <div class="cmp-col cmp-val-col ${v2Better ? 'cmp-winner' : ''}">
                    <div class="cmp-val">${s.v2}${s.isCount ? '' : '%'} ${v2Better ? badge(1) : ''}</div>
                    <div class="cmp-bar-track"><div class="cmp-bar cmp-bar-r2" style="width:${Math.round(s.v2 / barMax * 100)}%"></div></div>
                </div>
            </div>`;
    }).join('')}

        <div class="cmp-skills-section">
            <div class="cmp-skills-col">
                <div class="cmp-skills-title" style="color:#6366f1">Only in ${name1}</div>
                <div class="cmp-badges">
                    ${uniqueToR1.length ? uniqueToR1.map(s => `<span class="cmp-badge cmp-badge-r1">${s.name}</span>`).join('') : '<span class="cmp-none">—</span>'}
                </div>
            </div>
            <div class="cmp-skills-col">
                <div class="cmp-skills-title" style="color:#10b981">Shared Skills</div>
                <div class="cmp-badges">
                    ${sharedSkills.length ? sharedSkills.map(s => `<span class="cmp-badge cmp-badge-shared">${s.name}</span>`).join('') : '<span class="cmp-none">—</span>'}
                </div>
            </div>
            <div class="cmp-skills-col">
                <div class="cmp-skills-title" style="color:#f43f5e">Only in ${name2}</div>
                <div class="cmp-badges">
                    ${uniqueToR2.length ? uniqueToR2.map(s => `<span class="cmp-badge cmp-badge-r2">${s.name}</span>`).join('') : '<span class="cmp-none">—</span>'}
                </div>
            </div>
        </div>

    </div>`;
}
