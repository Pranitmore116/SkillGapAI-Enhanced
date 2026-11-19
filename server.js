/**
 * SkillGapAI — Node.js Express Server
 * Serves the SkillGapAI Frontend website and powers the Chatbot API.
 */
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());

// Serve static frontend files
app.use(express.static(path.join(__dirname, 'SkillGapAI-Frontend')));
app.use('/SkillGapAI-Frontend', express.static(path.join(__dirname, 'SkillGapAI-Frontend')));

// Default root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'SkillGapAI-Frontend', 'index.html'));
});

// ── CHATBOT LOGIC ──
const BOT_PERSONALITY = "I'm your SkillGap AI Career Assistant.";

app.post('/api/chatbot', (req, res) => {
    const { message, analysis, history } = req.body;
    const query = message.toLowerCase();

    let reply = "";

    // Rule-based logic with context awareness
    if (query.includes('skill') || query.includes('learn')) {
        if (analysis && analysis.missing && analysis.missing.length > 0) {
            const top3 = analysis.missing.slice(0, 3).map(s => s.name).join(', ');
            reply = `Based on our analysis, your most critical skill gaps are: ${top3}. I've tailored a learning roadmap for you in the "Learning Paths" section. Which one would you like to start with?`;
        } else {
            reply = "I recommend uploading a resume and job description first! Once analyzed, I can tell you exactly which technical and soft skills to prioritize.";
        }
    }
    else if (query.includes('score') || query.includes('match')) {
        if (analysis) {
            const score = analysis.matchPct;
            if (score >= 80) {
                reply = `Your match score is a strong ${score}%. You're a great fit for this role! Ensure your interview performance highlights your ${analysis.matched.slice(0, 2).map(s => s.name).join(' and ')} expertise.`;
            } else if (score >= 50) {
                reply = `Your match score is ${score}%. It's a solid start, but adding the missing ${analysis.missing.length} keywords I detected could push you into the 'Ideal Candidate' zone.`;
            } else {
                reply = `Your match score is ${score}%. This indicates a significant gap. I suggest focusing on the 'High Priority' recommendations to bridge this gap quickly.`;
            }
        } else {
            reply = "I don't see an analysis result yet. Try the 'Analyze Skill Gap' tool on the home page!";
        }
    }
    else if (query.includes('improve') || query.includes('resume') || query.includes('suggest')) {
        let personalTip = "";
        if (analysis && analysis.missing && analysis.missing.length > 0) {
            personalTip = ` For your current resume, I specifically recommend adding **${analysis.missing[0].name}** and **${analysis.missing[1]?.name || 'relevant industry tools'}** to your skills section.`;
        }
        reply = "To boost your resume quality, I recommend: 1. Adding quantifiable achievements (e.g., 'Reduced costs by 15%'), 2. Using stronger action verbs like 'Engineered' instead of 'Worked on', and 3. Ensuring your technical stack matches the job description perfectly." + personalTip;
    }
    else if (query.includes('roadmap')) {
        reply = "I can generate a 30/60/90 day learning roadmap for you. This will include weekly tasks and specific resources for each skill you're missing. Check the 'Learning Paths' tab to see it in detail!";
    }
    else if (query.includes('hello') || query.includes('hi')) {
        reply = "Hello! I'm your AI Career Assistant. I can help you understand your skill gaps, improve your resume, or find the best learning resources. What's on your mind?";
    }
    else if (query.includes('thank')) {
        reply = "You're very welcome! I'm here to help you land that dream job. Is there anything else you'd like to check?";
    }
    else {
        reply = "That's an interesting point. While I specialize in skill gap analysis, I can also help with resume tips and career roadmaps. Would you like to know how to improve your current match score?";
    }

    res.json({
        reply: reply,
        status: "success",
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(`\n🚀 SkillGapAI Server running at http://localhost:${PORT}`);
    console.log(`🌐 Website URL: http://localhost:${PORT}`);
    console.log(`💬 Chatbot API: http://localhost:${PORT}/api/chatbot\n`);
});
