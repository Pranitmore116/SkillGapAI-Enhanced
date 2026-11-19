/**
 * theme-loader.js
 * Injected into <head> to prevent theme flickering and clean UI labels.
 */
(function () {
    try {
        const settings = JSON.parse(localStorage.getItem('user_settings') || '{}');
        if (settings.theme === 'light') {
            document.documentElement.classList.add('light-mode');
            window.addEventListener('DOMContentLoaded', () => {
                document.body.classList.add('light-mode');
            });
        }
    } catch (e) { }

    // Helper: Remove academic unit and syllabus prefixes from visible UI text
    function cleanUILabelText(str) {
        if (!str || typeof str !== 'string') return str;
        let s = str;
        s = s.replace(/^Syllabus\s*[:—–-]\s*/i, '');
        s = s.replace(/\bUnit\s+(?:I{1,3}|IV|V|VI|[1-6])\s*\(([^)]+)\)/gi, '$1');
        s = s.replace(/\bUnit\s+(?:I{1,3}|IV|V|VI|[1-6])\s*[:—–-]\s*/gi, '');
        s = s.replace(/^\s*Unit\s+(?:I{1,3}|IV|V|VI|[1-6])\s*$/gi, '');
        s = s.replace(/\bModule\s+[0-9]+\s*[:—–-]\s*/gi, '');
        s = s.replace(/\bCosine Similarity Matching Engine\b/gi, 'Cosine Similarity Engine');
        s = s.replace(/\bCosine Matching\b/gi, 'Cosine Similarity');
        s = s.replace(/\bMatching Salient Terms\b/gi, 'Shared Salient Terms');
        s = s.replace(/^[:—–-\s]+/, '').replace(/[:—–-\s]+$/, '').trim();
        return s;
    }

    function cleanElementLabels(root) {
        if (!root || !root.querySelectorAll) return;
        const selector = 'h1, h2, h3, h4, h5, h6, .lab-card-title, .card-title, .compare-title, .nlp-tab-btn, .lab-tab-btn, .syllabus-badge, th, td strong, td span';
        const elements = root.querySelectorAll(selector);
        elements.forEach(el => {
            for (let i = 0; i < el.childNodes.length; i++) {
                const node = el.childNodes[i];
                if (node.nodeType === 3 /* Node.TEXT_NODE */) {
                    const orig = node.textContent;
                    const cleaned = cleanUILabelText(orig);
                    if (cleaned !== orig && cleaned.length > 0) {
                        node.textContent = cleaned;
                    }
                }
            }
        });
    }

    window.addEventListener('DOMContentLoaded', () => {
        cleanElementLabels(document.body);

        try {
            const observer = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    if (mutation.type === 'childList') {
                        for (const addedNode of mutation.addedNodes) {
                            if (addedNode.nodeType === 1 /* Node.ELEMENT_NODE */) {
                                cleanElementLabels(addedNode);
                            }
                        }
                    }
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        } catch (e) { }
    });
})();
