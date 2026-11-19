/**
 * SkillGapAI — Career Chatbot Logic
 * Handles UI interactions and API communication
 */
'use strict';

(function () {
    const $ = id => document.getElementById(id);

    // Initial State
    const chatState = {
        isOpen: false,
        isThinking: false,
        messages: [],
    };

    // Chatbot UI Constants
    const WELCOME_MSG = "Hello! I'm your SkillGap AI Career Assistant. How can I help you today?";
    function getChatbotApiUrl() {
        if (typeof window !== 'undefined' && window.location && window.location.protocol.startsWith('http')) {
            const host = window.location.hostname;
            if (host === 'localhost' || host === '127.0.0.1') {
                return (window.location.port === '3000') ? '/api/chatbot' : 'http://localhost:3000/api/chatbot';
            }
            return '/api/chatbot';
        }
        return 'http://localhost:3000/api/chatbot';
    }
    const CHATBOT_API = getChatbotApiUrl();

    function initChatbot() {
        const toggle = $('chatbot-toggle');
        const window = $('chat-window');
        const input = $('chat-input');
        const sendBtn = $('chat-send-btn');
        const messagesContainer = $('chat-messages');

        if (!toggle || !window) return;

        // 1. Toggle Chat
        toggle.addEventListener('click', () => {
            chatState.isOpen = !chatState.isOpen;
            window.classList.toggle('active', chatState.isOpen);
            toggle.classList.toggle('active', chatState.isOpen);

            if (chatState.isOpen && chatState.messages.length === 0) {
                addMessage('bot', WELCOME_MSG);
            }
        });

        // 2. Send Message logic
        const handleSend = async () => {
            const text = input.value.trim();
            if (!text || chatState.isThinking) return;

            input.value = '';
            addMessage('user', text);
            await getBotResponse(text);
        };

        sendBtn.addEventListener('click', handleSend);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSend();
        });

        // 3. Quick Buttons
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.textContent;
                addMessage('user', text);
                getBotResponse(text);
            });
        });
    }

    function addMessage(sender, text) {
        const container = $('chat-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg msg-${sender}`;
        msgDiv.textContent = text;
        container.appendChild(msgDiv);

        // Auto-scroll
        container.scrollTop = container.scrollHeight;

        // Save to state
        chatState.messages.push({ sender, text });
    }

    function showTyping(show) {
        let loader = $('typing-loader');
        if (show) {
            if (!loader) {
                loader = document.createElement('div');
                loader.id = 'typing-loader';
                loader.className = 'msg msg-bot typing-indicator';
                loader.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
                $('chat-messages').appendChild(loader);
            }
            $('chat-messages').scrollTop = $('chat-messages').scrollHeight;
            chatState.isThinking = true;
        } else if (loader) {
            loader.remove();
            chatState.isThinking = false;
        }
    }

    async function getBotResponse(userText) {
        showTyping(true);

        const localHistory = JSON.parse(localStorage.getItem('skillgap_history') || '[]');
        const appData = window.state?.analysisResult || (localHistory.length > 0 ? localHistory[0] : null);

        try {
            const response = await fetch(CHATBOT_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userText,
                    analysis: appData,
                    history: chatState.messages
                })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            showTyping(false);
            addMessage('bot', data.reply);

        } catch (err) {
            console.warn('[Chatbot] Backend unavailable, using local fallback');
            setTimeout(() => {
                showTyping(false);
                addMessage('bot', localFallback(userText, appData));
            }, 800);
        }
    }

    function localFallback(text, analysis) {
        const query = text.toLowerCase();

        // 1. Greetings
        if (query.match(/\b(hi|hello|hey|start|help|morning)\b/)) {
            return "Hi there! I'm your AI Career Assistant. I can help you understand your skill gaps, improve your ATS score, or suggest learning paths. What do you need help with?";
        }

        // 2. Score / ATS / Match
        if (query.match(/\b(score|match|ats|percentage|rating|low)\b/)) {
            if (analysis) {
                const match = analysis.matchPct || 0;
                if (match >= 80) return `Your current match score is an excellent ${match}%. Your resume is highly optimized for this role!`;
                if (match >= 50) return `Your match score is ${match}%. You have a solid foundation, but adding a few missing keywords will boost your chances of passing the ATS.`;
                return `Your match score is ${match}%. It looks like there's a significant gap between your resume and the job requirements. Review the 'Learning Paths' tab!`;
            }
            return "Upload your resume and a job description on the home page first so I can calculate your ATS match score!";
        }

        // 3. Matched Skills / Strengths
        if (query.match(/\b(matched|good|have|know|strength|strengths|skills)\b/) && !query.match(/\b(learn|missing|gap)\b/)) {
            if (analysis && analysis.matched && analysis.matched.length > 0) {
                const topMatched = analysis.matched.slice(0, 4).map(s => (s.name || s.skill || s)).join(', ');
                return `Your strongest matching skills for this role are: ${topMatched}. Make sure these are prominently featured at the top of your resume!`;
            }
            return "Please run a scan on the home page so I can extract your matching skills.";
        }

        // 4. Missing Skills / Learning
        if (query.match(/\b(learn|missing|gap|gaps|don't have|lack|study|course)\b/)) {
            if (analysis && analysis.missing && analysis.missing.length > 0) {
                const topGaps = analysis.missing.slice(0, 4).map(s => (s.name || s.skill || s)).join(', ');
                return `Based on the job description, you are missing these key skills: ${topGaps}. I highly recommend checking the 'Learning Paths' tab for courses on these exact topics.`;
            }
            if (analysis) return "Great news! You aren't missing any major technical skills for this role.";
            return "I need to analyze your resume against a job description first to identify your skill gaps.";
        }

        // 5. Resume Tips / Improvement
        if (query.match(/\b(improve|resume|cv|better|tips|advice)\b/)) {
            if (analysis && analysis.missing && analysis.missing.length > 0) {
                const someMissing = analysis.missing.slice(0, 2).map(s => (s.name || s.skill || s)).join(' and ');
                return `To improve your resume specifically for this role, try adding ${someMissing} to your experience if you have used them. Also, use quantifiable metrics (like "% increased" or "$ saved") in your bullet points to stand out.`;
            }
            return "To build a professional resume, always start bullet points with strong action verbs (e.g., 'Spearheaded', 'Optimized'), include quantifiable impact metrics, and keep it to 1-2 pages maximum.";
        }

        // 6. Job Matches / Roles
        if (query.match(/\b(job|roles|titles|positions|apply)\b/)) {
            if (analysis && analysis.role && analysis.role !== 'Analysis') {
                return `You recently analyzed a JD for "${analysis.role}". Check the 'Job Matches' tab in the sidebar to see similar roles that match your validated skillset!`;
            }
            return "Head over to the 'Job Matches' tab! Our AI uses your actual skill profile to match you with realistic job titles and salaries in the market.";
        }

        // 7. General Career / ATS Knowledge
        if (query.match(/\b(format|font|length|pages|ats rule|rules|layout)\b/)) {
            return "For ATS systems, use a clean layout without columns, graphics, or complex tables. Stick to standard fonts like Arial or Calibri, and keep it to 1 page if you have <5 years of experience, or 2 pages max if you have more.";
        }

        // 8. Interview
        if (query.match(/\b(interview|questions|prep|prepare)\b/)) {
            if (analysis && analysis.missing && analysis.missing.length > 0) {
                return `For interviews, be ready to explain how you plan to learn the skills you lack, like ${analysis.missing[0].name || analysis.missing[0]}. Focus on highlighting your adaptability and fast learning!`;
            }
            return "To prepare for interviews, use the STAR method (Situation, Task, Action, Result) to structure your answers. Make sure to tailor your stories to the core requirements of the job.";
        }

        // Default Fallback
        return "That's an interesting question! While I am in local mode, I am highly specialized in helping you analyze your ATS score, identifying missing skills, suggesting learning paths, or offering resume formatting advice. What can I help you with?";
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatbot);
    } else {
        initChatbot();
    }

})();
