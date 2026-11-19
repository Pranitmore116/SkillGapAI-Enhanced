/**
 * SkillGapAI — Full Professional PDF Export
 * Emoji-free (Helvetica-safe). All Unicode stripped to prevent PDF corruption.
 */
'use strict';

function exportToPDF(data) {
    try {
        if (!window.jspdf) { alert('PDF library not loaded. Please check your internet connection.'); return; }
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
        const PW = 210, PH = 297, M = 18, CW = PW - M * 2;
        let y = 0;

        // Strip all emoji and non-Helvetica-safe characters to prevent PDF corruption
        const safe = s => (s || '')
            .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
            .replace(/[\u2014\u2013]/g, '-')
            .replace(/[\u2018\u2019]/g, "'")
            .replace(/[\u201C\u201D]/g, '"')
            .replace(/\u2022/g, '*')
            .replace(/\u2550|\u2500|\u2502/g, '-')
            .replace(/[^\x20-\x7E\xA0-\xFF\n]/g, ' ')
            .replace(/\s{3,}/g, '  ')
            .trim();

        const C = {
            accent: [99, 102, 241],
            success: [16, 185, 129],
            danger: [244, 63, 94],
            warning: [245, 158, 11],
            dark: [15, 23, 42],
            light: [148, 163, 184],
            white: [248, 250, 252],
            bg2: [30, 41, 59],
            card: [20, 30, 50],
            mid: [71, 85, 105],
            navy: [10, 15, 30],
        };

        const fill = (x, fy, w, h, r, col) => {
            doc.setFillColor(...col);
            r > 0 ? doc.roundedRect(x, fy, w, h, r, r, 'F') : doc.rect(x, fy, w, h, 'F');
        };
        const txt = (s, fx, fy, opts) => {
            try { doc.text(safe(String(s || '')), fx, fy, opts || {}); } catch (e) { }
        };
        const chk = needed => {
            if (y + needed > 275) { addPageFooter(); doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22; }
        };

        function secHeader(label) {
            chk(18);
            fill(M, y, CW, 11, 2, C.bg2);
            fill(M, y, 3, 11, 0, C.accent);
            doc.setFontSize(10); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.accent);
            txt(label, M + 8, y + 7.5);
            y += 16;
        }

        function badgeRow(items, bg, fg) {
            if (!items || !items.length) return;
            let bx = M, rowY = y;
            items.forEach(s => {
                const name = safe(s.name || s);
                if (!name) return;
                doc.setFontSize(7); doc.setFont('helvetica', 'bold');
                const bw = doc.getTextWidth(name) + 8;
                if (bx + bw > PW - M) { bx = M; rowY += 9; y += 9; chk(10); }
                fill(bx, rowY, bw, 6, 2, bg);
                doc.setTextColor(...fg);
                txt(name, bx + 4, rowY + 4.3);
                bx += bw + 2;
            });
            y = rowY + 12;
        }

        function addPageFooter() {
            fill(0, PH - 11, PW, 11, 0, C.navy);
            doc.setFontSize(6.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.mid);
            txt('SkillGapAI (c) ' + new Date().getFullYear() + '  |  AI-Powered Career Intelligence', M, PH - 4.5);
        }

        const {
            matched = [], missing = [], extra = [], jdSkills = [],
            matchPct = 0, atsPct = 0, marketReadinessPct = 0, skillDiversityPct = 0,
            categoryData = [], recommendations = []
        } = data;

        const rawResume = safe(document.getElementById('raw-resume-box')?.innerText || data.raw_text || '');
        const optResume = safe(document.getElementById('optimized-resume-box')?.innerText || data.optimized_text || rawResume);
        const now = new Date();

        /* ============================================================
           PAGE 1 — PROFESSIONAL COVER PAGE
        ============================================================ */
        fill(0, 0, PW, PH, 0, C.dark);
        fill(0, 0, PW, 5, 0, C.accent);         // top bar
        fill(0, PH - 5, PW, 5, 0, C.accent);    // bottom bar

        // Brand
        doc.setFontSize(14); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.accent);
        txt('SKILLGAPAI', M, 22);
        doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
        txt('AI-Powered Career Intelligence', M, 29);
        doc.setFontSize(8); doc.setTextColor(...C.mid);
        txt(now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }), PW - M, 22, { align: 'right' });

        // Title block
        fill(M, 70, CW, 78, 4, [18, 26, 48]);
        fill(M, 70, 4, 78, 0, C.accent);
        doc.setFontSize(30); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.white);
        txt('Skill Gap', M + 12, 98);
        txt('Analysis', M + 12, 116);
        doc.setFontSize(11); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
        txt('Professional Career Intelligence Report', M + 12, 130);

        // Score badge
        const scoreCol = matchPct >= 80 ? C.success : matchPct >= 50 ? C.accent : C.danger;
        fill(PW - 66, 75, 46, 66, 4, [10, 18, 38]);
        doc.setFontSize(26); doc.setFont('helvetica', 'bold'); doc.setTextColor(...scoreCol);
        txt(matchPct + '%', PW - 43, 107, { align: 'center' });
        doc.setFontSize(7); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
        txt('MATCH SCORE', PW - 43, 116, { align: 'center' });

        // 4 mini metric boxes
        const mw = (CW - 9) / 4;
        [
            { label: 'ATS Score', val: atsPct + '%', col: C.success },
            { label: 'Market Ready', val: marketReadinessPct + '%', col: C.warning },
            { label: 'Skill Diversity', val: skillDiversityPct + '%', col: [14, 165, 233] },
            { label: 'Gaps Found', val: String(missing.length), col: C.danger },
        ].forEach((m, i) => {
            const bx = M + i * (mw + 3);
            fill(bx, 162, mw, 28, 3, [18, 26, 48]);
            doc.setFontSize(15); doc.setFont('helvetica', 'bold'); doc.setTextColor(...m.col);
            txt(m.val, bx + mw / 2, 177, { align: 'center' });
            doc.setFontSize(6); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(m.label, bx + mw / 2, 184, { align: 'center' });
        });

        // Counts strip
        fill(M, 200, CW, 20, 3, [12, 20, 38]);
        [
            { label: 'JD Skills', val: jdSkills.length, col: C.light },
            { label: 'Matched', val: matched.length, col: C.success },
            { label: 'Missing', val: missing.length, col: C.danger },
            { label: 'Bonus', val: extra.length, col: C.accent },
        ].forEach((s, i) => {
            const bx = M + i * (CW / 4);
            doc.setFontSize(13); doc.setFont('helvetica', 'bold'); doc.setTextColor(...s.col);
            txt(String(s.val), bx + CW / 8, 214, { align: 'center' });
            doc.setFontSize(6); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(s.label, bx + CW / 8, 220, { align: 'center' });
        });

        addPageFooter();

        /* ============================================================
           PAGE 2 — TABLE OF CONTENTS + EXECUTIVE SUMMARY
        ============================================================ */
        doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;

        secHeader('TABLE OF CONTENTS');
        [
            '1.  Executive Summary',
            '2.  Skills Analysis  (Matched / Missing / Bonus)',
            '3.  Category Breakdown & Progress',
            '4.  30-60-90 Day Action Plan',
            '5.  Skills Scorecard',
            '6.  Personalized Learning Recommendations',
            '7.  Original Resume',
            '8.  AI-Optimized Resume',
        ].forEach(item => {
            chk(8);
            doc.setFontSize(9); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(item, M + 6, y); y += 7;
        });
        y += 8;

        secHeader('EXECUTIVE SUMMARY');
        const verdict = matchPct >= 80
            ? 'STRONG MATCH - Your profile aligns very well with this role.'
            : matchPct >= 50
                ? 'PARTIAL MATCH - A few targeted skill additions could make you competitive.'
                : 'ACTION NEEDED - Significant gaps exist. Follow the 30-60-90 Day Action Plan below.';

        fill(M, y, CW, 14, 3, matchPct >= 80 ? [16, 60, 40] : matchPct >= 50 ? [60, 50, 10] : [70, 20, 30]);
        doc.setFontSize(9.5); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.white);
        txt(verdict, M + 6, y + 9.5);
        y += 20;

        [
            'Report Generated  : ' + now.toLocaleString(),
            'Overall Match     : ' + matchPct + '%   |   ATS Score : ' + atsPct + '%',
            'Market Readiness  : ' + marketReadinessPct + '%   |   Skill Diversity : ' + skillDiversityPct + '%',
            'JD Skills Required: ' + jdSkills.length + '   |   Matched : ' + matched.length + '   |   Gaps : ' + missing.length + '   |   Bonus : ' + extra.length,
        ].forEach(line => {
            chk(7); doc.setFontSize(8.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(line, M + 4, y); y += 7;
        });
        y += 4;

        if (matched.length) {
            chk(12);
            doc.setFontSize(8.5); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.success);
            txt('Top Matched Skills:', M + 4, y); y += 6;
            doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(matched.slice(0, 7).map(s => s.name).join('  |  '), M + 4, y); y += 9;
        }
        if (missing.length) {
            chk(12);
            doc.setFontSize(8.5); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.danger);
            txt('Critical Gaps:', M + 4, y); y += 6;
            doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(missing.slice(0, 7).map(s => s.name).join('  |  '), M + 4, y); y += 9;
        }
        addPageFooter();

        /* ============================================================
           PAGE 3 — SKILLS ANALYSIS
        ============================================================ */
        doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;

        if (matched.length) {
            secHeader('MATCHED SKILLS  [' + matched.length + ']');
            badgeRow(matched, [16, 80, 55], C.success);
            y += 2;
        }
        if (missing.length) {
            secHeader('SKILLS TO ACQUIRE  [' + missing.length + ']');
            badgeRow(missing, [80, 25, 40], C.danger);
            y += 2;
        }
        if (extra.length) {
            secHeader('BONUS SKILLS  [' + extra.length + ']');
            badgeRow(extra, [40, 42, 110], C.accent);
            y += 2;
        }

        if (categoryData.length) {
            secHeader('CATEGORY BREAKDOWN');
            categoryData.forEach(cat => {
                chk(18);
                fill(M, y, CW, 14, 2, C.card);
                doc.setFontSize(8.5); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.white);
                txt(cat.category, M + 4, y + 6);
                doc.setFontSize(7.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
                txt(cat.matched + '/' + cat.required + '  (' + cat.matchPct + '%)', PW - M - 2, y + 6, { align: 'right' });
                fill(M + 4, y + 8.5, CW - 8, 3, 1, C.bg2);
                const bc = cat.matchPct >= 70 ? C.success : cat.matchPct >= 40 ? C.warning : C.danger;
                fill(M + 4, y + 8.5, Math.max((CW - 8) * cat.matchPct / 100, 2), 3, 1, bc);
                y += 17;
            });
        }
        addPageFooter();

        /* ============================================================
           PAGE 4 — 30-60-90 DAY ACTION PLAN + SCORECARD
        ============================================================ */
        doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;
        secHeader('30 - 60 - 90 DAY ACTION PLAN');

        const highPrio = recommendations.filter(r => r.priority === 'High').slice(0, 3);
        const medPrio = recommendations.filter(r => r.priority === 'Medium').slice(0, 3);
        const lowPrio = recommendations.filter(r => r.priority !== 'High' && r.priority !== 'Medium').slice(0, 3);

        [
            { title: 'DAYS 1-30  |  Foundation  (High Priority)', col: C.danger, items: highPrio, note: 'Focus on critical gaps to become immediately competitive.' },
            { title: 'DAYS 31-60 |  Growth  (Medium Priority)', col: C.warning, items: medPrio, note: 'Build on foundations; add medium-priority skills.' },
            { title: 'DAYS 61-90 |  Polish  (Enhancement)', col: C.success, items: lowPrio, note: 'Refine and diversify; build portfolio showcase projects.' },
        ].forEach(phase => {
            chk(22);
            fill(M, y, CW, 12, 2, C.card);
            fill(M, y, 4, 12, 0, phase.col);
            doc.setFontSize(9); doc.setFont('helvetica', 'bold'); doc.setTextColor(...phase.col);
            txt(phase.title, M + 8, y + 8.3);
            y += 14;
            doc.setFontSize(7.5); doc.setFont('helvetica', 'italic'); doc.setTextColor(...C.mid);
            txt(phase.note, M + 4, y); y += 7;

            if (phase.items.length) {
                phase.items.forEach((r, i) => {
                    chk(16);
                    doc.setFontSize(9); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.white);
                    txt((i + 1) + '.  ' + (r.skill || '') + '  (' + (r.type || '') + ')', M + 6, y);
                    const al = doc.splitTextToSize(safe(r.advice || ''), CW - 14);
                    doc.setFontSize(7.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
                    al.slice(0, 2).forEach(line => { y += 5.5; chk(6); txt(line, M + 10, y); });
                    y += 7;
                });
            } else {
                chk(8); doc.setFontSize(8); doc.setFont('helvetica', 'italic'); doc.setTextColor(...C.mid);
                txt('  No specific gaps identified for this phase.', M + 4, y); y += 10;
            }
            y += 4;
        });

        chk(20); y += 4;
        secHeader('SKILLS SCORECARD SUMMARY');
        [
            { metric: 'Overall Job Match', score: matchPct, max: 100, col: matchPct >= 70 ? C.success : C.danger },
            { metric: 'ATS Optimization', score: atsPct, max: 100, col: atsPct >= 70 ? C.success : C.warning },
            { metric: 'Market Readiness', score: marketReadinessPct, max: 100, col: marketReadinessPct >= 70 ? C.success : C.warning },
            { metric: 'Skill Diversity', score: skillDiversityPct, max: 100, col: skillDiversityPct >= 60 ? C.success : C.accent },
            { metric: 'Skills Matched / JD', score: matched.length, max: Math.max(jdSkills.length, 1), col: C.success },
        ].forEach(row => {
            chk(14);
            const pct = Math.min(100, Math.round((row.score / row.max) * 100));
            fill(M, y, CW, 11, 2, C.card);
            doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
            txt(row.metric, M + 4, y + 7.5);
            doc.setFontSize(8); doc.setFont('helvetica', 'bold'); doc.setTextColor(...row.col);
            txt(row.max === 100 ? (row.score + '%') : (row.score + '/' + row.max), PW - M - 2, y + 7.5, { align: 'right' });
            fill(M + 4, y + 9, CW - 8, 2, 0, C.bg2);
            fill(M + 4, y + 9, Math.max((CW - 8) * pct / 100, 2), 2, 0, row.col);
            y += 14;
        });
        addPageFooter();

        /* ============================================================
           PAGE 5 — LEARNING RECOMMENDATIONS
        ============================================================ */
        if (recommendations.length) {
            doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;
            secHeader('PERSONALIZED LEARNING RECOMMENDATIONS');

            recommendations.slice(0, 8).forEach(r => {
                chk(34);
                fill(M, y, CW, 30, 3, C.card);
                const pc = r.priority === 'High' ? C.danger : r.priority === 'Medium' ? C.warning : C.success;
                fill(M, y, 3, 30, 0, pc);
                doc.setFontSize(6.5); doc.setFont('helvetica', 'bold'); doc.setTextColor(...pc);
                txt('[' + (r.priority || 'LOW').toUpperCase() + ']', PW - M - 3, y + 6, { align: 'right' });
                doc.setFontSize(10); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.white);
                txt(r.skill || '', M + 7, y + 7.5);
                doc.setFontSize(7.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.accent);
                txt((r.category || '') + '  |  ' + (r.type || ''), M + 7, y + 13.5);
                doc.setFontSize(7.8); doc.setTextColor(...C.light);
                const al = doc.splitTextToSize(safe(r.advice || ''), CW - 16);
                al.slice(0, 2).forEach((line, li) => txt(line, M + 7, y + 19 + li * 5));
                doc.setFontSize(7); doc.setTextColor(100, 130, 220);
                txt('Learn: ' + (r.url || ''), M + 7, y + 29.5);
                y += 34;
            });
            addPageFooter();
        }

        /* ============================================================
           PAGE — ORIGINAL RESUME
        ============================================================ */
        if (rawResume) {
            doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;
            secHeader('ORIGINAL RESUME');
            doc.splitTextToSize(rawResume, CW - 4).forEach(line => {
                chk(6); doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
                txt(line, M + 2, y); y += 5.2;
            });
            addPageFooter();
        }

        /* ============================================================
           PAGE — AI-OPTIMIZED RESUME
        ============================================================ */
        if (optResume) {
            doc.addPage(); fill(0, 0, PW, PH, 0, C.dark); y = 22;
            fill(M, y - 2, CW, 13, 2, [20, 50, 40]);
            fill(M, y - 2, 4, 13, 0, C.success);
            doc.setFontSize(10); doc.setFont('helvetica', 'bold'); doc.setTextColor(...C.success);
            txt('AI-OPTIMIZED RESUME', M + 8, y + 7);
            y += 18;
            doc.setFontSize(7.5); doc.setFont('helvetica', 'italic'); doc.setTextColor(...C.mid);
            txt('Keywords injected for ATS compatibility. Review before submitting to employers.', M + 2, y);
            y += 10;
            doc.splitTextToSize(optResume, CW - 4).forEach(line => {
                chk(6); doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.light);
                txt(line, M + 2, y); y += 5.2;
            });
            addPageFooter();
        }

        // Page numbers — applied to every page
        const total = doc.getNumberOfPages();
        for (let pg = 1; pg <= total; pg++) {
            doc.setPage(pg);
            doc.setFontSize(6.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(...C.mid);
            doc.text('Page ' + pg + ' of ' + total, PW - M, PH - 4.5, { align: 'right' });
        }

        doc.save('SkillGapAI_Full_Report.pdf');

    } catch (e) {
        console.error('[SkillGapAI] PDF export error:', e);
        alert('PDF export failed: ' + e.message);
    }
}

// Individual resume PDF: just that resume's text as a clean PDF
function downloadResumePDF(boxId, filename, accentColor) {
    const text = document.getElementById(boxId)?.innerText?.trim() || '';
    if (!text) { alert('No resume content to download.'); return; }

    const safeText = text
        .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
        .replace(/[^\x20-\x7E\xA0-\xFF\n]/g, ' ')
        .replace(/\s{3,}/g, '  ');

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ unit: 'mm', format: 'a4' });
        const PW = 210, PH = 297, M = 18, CW = PW - M * 2;

        // Page background & bars
        doc.setFillColor(15, 23, 42); doc.rect(0, 0, PW, PH, 'F');
        doc.setFillColor(...accentColor); doc.rect(0, 0, PW, 5, 'F');
        doc.setFillColor(...accentColor); doc.rect(0, PH - 5, PW, 5, 'F');

        // Header
        doc.setFontSize(16); doc.setFont('helvetica', 'bold'); doc.setTextColor(248, 250, 252);
        doc.text(filename.replace(/_SkillGapAI\.pdf/, '').replace(/_/g, ' '), M, 20);
        doc.setFontSize(8); doc.setFont('helvetica', 'normal'); doc.setTextColor(148, 163, 184);
        doc.text('Generated by SkillGapAI  |  ' + new Date().toLocaleDateString(), M, 28);

        let y = 38;
        const lines = doc.splitTextToSize(safeText, CW);
        lines.forEach(line => {
            if (y > 278) {
                doc.setFillColor(15, 23, 42); doc.rect(0, 0, PW, PH, 'F');
                doc.setFillColor(...accentColor); doc.rect(0, PH - 5, PW, 5, 'F');
                doc.addPage();
                doc.setFillColor(15, 23, 42); doc.rect(0, 0, PW, PH, 'F');
                y = 20;
            }
            doc.setFontSize(8.5); doc.setFont('helvetica', 'normal'); doc.setTextColor(148, 163, 184);
            doc.text(line, M, y); y += 5.2;
        });

        doc.save(filename);
    } catch (e) { alert('PDF error: ' + e.message); }
}
