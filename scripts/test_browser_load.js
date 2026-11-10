const fs = require('fs');

// Mock browser globals
global.window = global;
global.document = {
    addEventListener: (ev, fn) => {
        if (ev === 'DOMContentLoaded') setTimeout(fn, 10);
    },
    getElementById: (id) => ({
        id,
        style: {},
        classList: { add: () => {}, remove: () => {}, toggle: () => {} },
        addEventListener: () => {},
        dataset: {}
    }),
    querySelectorAll: () => [],
    createElement: () => ({
        style: {},
        classList: { add: () => {}, remove: () => {} },
        appendChild: () => {}
    }),
    body: { appendChild: () => {} },
    location: { hostname: 'localhost' }
};
global.window.location = global.document.location;
global.sessionStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
};
global.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
};
global.Chart = function() { return { destroy: () => {} }; };

try {
    console.log('Loading theme-toggle.js...');
    require('./SkillGapAI-Frontend/js/theme-toggle.js');
    console.log('Loading pdf-export.js...');
    require('./SkillGapAI-Frontend/js/pdf-export.js');
    console.log('Loading resume-suggestions.js...');
    require('./SkillGapAI-Frontend/js/resume-suggestions.js');
    console.log('Loading chatbot.js...');
    require('./SkillGapAI-Frontend/js/chatbot.js');
    console.log('Loading nlp-dashboard.js...');
    require('./SkillGapAI-Frontend/js/nlp-dashboard.js');
    console.log('Loading app.js...');
    require('./SkillGapAI-Frontend/js/app.js');
    console.log('All scripts loaded successfully without syntax/runtime errors at top level!');
} catch (e) {
    console.error('ERROR during script load:', e);
}

