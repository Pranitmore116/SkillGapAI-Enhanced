import os

def update_index():
    index_path = os.path.join(os.path.dirname(__file__), '..', 'SkillGapAI-Frontend', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Navigation
    nav_marker = '<a href="about.html" class="side-link">'
    if 'href="nlp-lab.html"' not in content:
        nav_replacement = '''<a href="nlp-lab.html" class="side-link">
                    <span class="s-icon">🔬</span> <span class="s-text">NLP Lab</span>
                </a>
                <a href="methodology.html" class="side-link">
                    <span class="s-icon">🎓</span> <span class="s-text">Methodology</span>
                </a>
                <a href="about.html" class="side-link">'''
        content = content.replace(nav_marker, nav_replacement, 1)

    # 2. Add NLP Deep Dive Section before 'Analyze Another Job'
    deepdive_html = '''
                    <!-- ═══════════════════════════════════════════
                         ACADEMIC NLP DEEP DIVE (CSE472 COURSE UPGRADE)
                    ════════════════════════════════════════════ -->
                    <div class="nlp-deepdive-container" id="nlp-deepdive-container" style="display:none; margin: 40px 0;">
                        <div style="background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(219,39,119,0.08)); border: 1px solid var(--border); border-radius: 20px; padding: 2rem; margin-bottom: 2rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
                                <div>
                                    <span style="background: var(--accent-gradient); color: white; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase;">
                                        CSE472: Deep Learning for NLP
                                    </span>
                                    <h2 style="font-size: 1.8rem; font-weight: 800; margin-top: 0.6rem; color: var(--t1);">Academic NLP Deep Dive & Model Comparison</h2>
                                    <p style="color: var(--t2); font-size: 0.9rem; margin-top: 4px;">
                                        Comprehensive inspectability across Unit I (Text Processing & TF-IDF), Unit II (Word Embeddings), and Unit V (Transformers & BERT NER).
                                    </p>
                                </div>
                                <div style="text-align: right; background: var(--bg2); padding: 12px 20px; border-radius: 12px; border: 1px solid var(--border);">
                                    <div style="font-size: 0.75rem; color: var(--t3); text-transform: uppercase;">Multimodal Unified Score</div>
                                    <div id="unified-overall-score" style="font-size: 1.8rem; font-weight: 900; color: var(--accent-lt);">0%</div>
                                    <div style="font-size: 0.7rem; color: var(--t3);">Total Latency: <span id="unified-total-time" style="color:var(--success);">0 ms</span></div>
                                </div>
                            </div>

                            <!-- NLP Navigation Tabs -->
                            <div style="display: flex; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 1.5rem;">
                                <button type="button" class="nlp-tab-btn active" data-target="nlp-pane-prep" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    📑 Module 1: Preprocessing
                                </button>
                                <button type="button" class="nlp-tab-btn" data-target="nlp-pane-tfidf" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    📐 Module 2: TF-IDF & Cosine Math
                                </button>
                                <button type="button" class="nlp-tab-btn" data-target="nlp-pane-embeddings" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    🌐 Module 3: Word2Vec PCA Space
                                </button>
                                <button type="button" class="nlp-tab-btn" data-target="nlp-pane-bert" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    🤖 Module 4: BERT Contextual NER
                                </button>
                                <button type="button" class="nlp-tab-btn" data-target="nlp-pane-benchmark" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    📊 Module 6: Model Comparison
                                </button>
                                <button type="button" class="nlp-tab-btn" data-target="nlp-pane-lab" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px 16px;border-radius:8px;font-size:0.85rem;cursor:pointer;font-weight:600;">
                                    🧪 Interactive NLP Sandbox
                                </button>
                            </div>

                            <!-- PANE 1: PREPROCESSING EXPLORER -->
                            <div class="nlp-tab-pane active" id="nlp-pane-prep">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Syllabus: Unit I — Text Processing Pipeline</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.2rem;">
                                    Demonstrating case folding, symbol preservation (C++, C#, .NET, Node.js, CI/CD), tokenization with character spans, stopword filtering with technical whitelist, Porter stemming, and WordNet lemmatization.
                                </p>
                                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:1.5rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Raw Tokens</div>
                                        <div id="prep-token-count" style="font-size:1.4rem;font-weight:800;color:var(--accent-lt);">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Cleaned Tokens</div>
                                        <div id="prep-clean-count" style="font-size:1.4rem;font-weight:800;color:var(--success);">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Stopwords Filtered</div>
                                        <div id="prep-stopword-count" style="font-size:1.4rem;font-weight:800;color:var(--danger);">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Vocabulary Size</div>
                                        <div id="prep-vocab-size" style="font-size:1.4rem;font-weight:800;color:#60a5fa;">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Pipeline Latency</div>
                                        <div id="prep-latency" style="font-size:1.4rem;font-weight:800;color:var(--warning);">0 ms</div>
                                    </div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:16px;border-radius:12px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:8px;color:var(--t1);">Top 15 Frequent Lemmatized Terms</h4>
                                        <div id="prep-top-terms" style="display:flex;flex-wrap:wrap;"></div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:16px;border-radius:12px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:8px;color:var(--t1);">Sample Bigram & Trigram N-Grams</h4>
                                        <div id="prep-ngrams" style="display:flex;flex-wrap:wrap;"></div>
                                        <h4 style="font-size:0.95rem;margin:12px 0 8px;color:var(--t1);">Filtered Stop Words</h4>
                                        <div id="prep-removed-stops" style="display:flex;flex-wrap:wrap;"></div>
                                    </div>
                                </div>
                            </div>

                            <!-- PANE 2: TF-IDF & COSINE SIMILARITY MATH -->
                            <div class="nlp-tab-pane" id="nlp-pane-tfidf">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Syllabus: Unit I — Bag-of-Words and TF-IDF Cosine Matching</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.2rem;">
                                    Mathematical vector space model calculating exact Cosine Similarity: <code>cos(A, B) = (A · B) / (||A|| × ||B||)</code> and sublinear TF-IDF weights: <code>TF-IDF(t,d) = (1 + log(TF)) × IDF</code>.
                                </p>
                                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:1.5rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">TF-IDF Cosine</div>
                                        <div id="tfidf-cosine-score" style="font-size:1.5rem;font-weight:800;color:var(--accent-lt);">0%</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Skill-Weighted Score</div>
                                        <div id="tfidf-skill-weighted" style="font-size:1.5rem;font-weight:800;color:var(--success);">0%</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">BoW Similarity</div>
                                        <div id="tfidf-bow-score" style="font-size:1.5rem;font-weight:800;color:#60a5fa;">0%</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Vector Dot Product</div>
                                        <div id="tfidf-dot-product" style="font-size:1.3rem;font-weight:700;color:var(--t1);">0.0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">||Resume||₂ L2 Norm</div>
                                        <div id="tfidf-norm-resume" style="font-size:1.3rem;font-weight:700;color:var(--t1);">0.0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">||JD||₂ L2 Norm</div>
                                        <div id="tfidf-norm-jd" style="font-size:1.3rem;font-weight:700;color:var(--t1);">0.0</div>
                                    </div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:16px;border-radius:12px;overflow-x:auto;">
                                        <h4 style="font-size:0.95rem;margin-bottom:8px;color:var(--t1);">Top Shared Terms (Joint TF-IDF Weight)</h4>
                                        <table style="width:100%;font-size:0.8rem;border-collapse:collapse;">
                                            <thead>
                                                <tr style="background:var(--bg3);color:var(--t3);text-align:left;">
                                                    <th style="padding:6px 12px;">Term</th>
                                                    <th style="padding:6px 12px;text-align:center;">Resume</th>
                                                    <th style="padding:6px 12px;text-align:center;">JD</th>
                                                    <th style="padding:6px 12px;text-align:center;">Joint</th>
                                                </tr>
                                            </thead>
                                            <tbody id="tfidf-matched-table"></tbody>
                                        </table>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:16px;border-radius:12px;overflow-x:auto;">
                                        <h4 style="font-size:0.95rem;margin-bottom:8px;color:var(--t1);">Top Missing Terms (High JD Weight, 0 in Resume)</h4>
                                        <table style="width:100%;font-size:0.8rem;border-collapse:collapse;">
                                            <thead>
                                                <tr style="background:var(--bg3);color:var(--t3);text-align:left;">
                                                    <th style="padding:6px 12px;">Missing Requirement</th>
                                                    <th style="padding:6px 12px;text-align:center;">JD TF-IDF Weight</th>
                                                </tr>
                                            </thead>
                                            <tbody id="tfidf-missing-table"></tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>

                            <!-- PANE 3: WORD2VEC PCA 2D EMBEDDING SPACE -->
                            <div class="nlp-tab-pane" id="nlp-pane-embeddings">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Syllabus: Unit II — Dense Embeddings & PCA 2D Dimensionality Reduction</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.2rem;">
                                    Projects 50-dimensional continuous Word2Vec / GloVe embeddings onto principal orthogonal components (PC1 & PC2). Clustered by technical domain to demonstrate geometric semantic relatedness.
                                </p>
                                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:1.2rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Semantic Match Score</div>
                                        <div id="w2v-score" style="font-size:1.4rem;font-weight:800;color:var(--accent-lt);">0%</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Exact Matches</div>
                                        <div id="w2v-exact-count" style="font-size:1.4rem;font-weight:800;color:var(--success);">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Semantic Inferences</div>
                                        <div id="w2v-semantic-count" style="font-size:1.4rem;font-weight:800;color:#60a5fa;">0</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">True Gaps</div>
                                        <div id="w2v-missing-count" style="font-size:1.4rem;font-weight:800;color:var(--danger);">0</div>
                                    </div>
                                </div>
                                <div style="background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:16px;margin-bottom:1.5rem;position:relative;height:380px;">
                                    <canvas id="pcaCanvas"></canvas>
                                </div>
                                <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;">
                                    <h4 style="font-size:0.95rem;margin-bottom:8px;color:var(--t1);">Semantic Skill Bridges (Word2Vec Cosine Distance &ge; 0.50)</h4>
                                    <div id="w2v-semantic-matches-list"></div>
                                </div>
                            </div>

                            <!-- PANE 4: BERT CONTEXTUAL NER TOKEN CLASSIFICATION -->
                            <div class="nlp-tab-pane" id="nlp-pane-bert">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Syllabus: Unit V — Transformers & BERT Token Classification (BIO Tagging)</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.2rem;">
                                    Extracts named skill entities dynamically in syntactic context using bidirectional self-attention mechanisms and BIO sequence labeling (<code>B-SKILL</code>, <code>I-SKILL</code>, <code>O</code>).
                                </p>
                                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:1.2rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Model Architecture</div>
                                        <div style="font-size:1.1rem;font-weight:800;color:var(--t1);">DistilBERT (6-Layer)</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Model Status</div>
                                        <div id="bert-status" style="font-size:1.0rem;font-weight:800;color:var(--success);">Loaded</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">BERT Overlap Score</div>
                                        <div id="bert-score" style="font-size:1.4rem;font-weight:800;color:var(--accent-lt);">0%</div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:12px;border-radius:10px;text-align:center;">
                                        <div style="font-size:0.75rem;color:var(--t3);text-transform:uppercase;">Contextual Entities</div>
                                        <div id="bert-entities-count" style="font-size:1.4rem;font-weight:800;color:#60a5fa;">0</div>
                                    </div>
                                </div>
                                <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;">
                                    <h4 style="font-size:0.95rem;margin-bottom:12px;color:var(--t1);">Detected Technical Entities in Context</h4>
                                    <div id="bert-entities-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;"></div>
                                </div>
                            </div>

                            <!-- PANE 5: BENCHMARK & MODEL EVALUATION -->
                            <div class="nlp-tab-pane" id="nlp-pane-benchmark">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Syllabus: Evaluation Metrics & Multi-Approach Comparison</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.2rem;">
                                    Rigorous academic benchmarking across all 5 paradigms evaluated against ground-truth technical skill annotations.
                                </p>
                                <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:1.5rem;overflow-x:auto;">
                                    <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
                                        <thead>
                                            <tr style="background:var(--bg3);color:var(--t3);text-align:left;">
                                                <th style="padding:10px 14px;">NLP Method</th>
                                                <th style="padding:10px 14px;text-align:center;">Precision</th>
                                                <th style="padding:10px 14px;text-align:center;">Recall</th>
                                                <th style="padding:10px 14px;text-align:center;">F1-Score</th>
                                                <th style="padding:10px 14px;text-align:center;">Latency</th>
                                                <th style="padding:10px 14px;">Theoretical Tradeoffs</th>
                                            </tr>
                                        </thead>
                                        <tbody id="benchmark-table-body"></tbody>
                                    </table>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
                                    <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:12px;color:var(--t1);">BERT Supervised Token Metrics</h4>
                                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.85rem;">
                                            <div>Token Accuracy: <strong id="eval-token-acc" style="color:var(--success);">0%</strong></div>
                                            <div>Macro Precision: <strong id="eval-macro-prec" style="color:var(--accent-lt);">0%</strong></div>
                                            <div>Macro Recall: <strong id="eval-macro-rec" style="color:#60a5fa;">0%</strong></div>
                                            <div>Macro F1-Score: <strong id="eval-macro-f1" style="color:var(--warning);">0%</strong></div>
                                        </div>
                                    </div>
                                    <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:12px;color:var(--t1);">Confusion Matrix (Held-out Test Split)</h4>
                                        <div id="eval-confusion-matrix"></div>
                                    </div>
                                </div>
                            </div>

                            <!-- PANE 6: INTERACTIVE NLP SANDBOX -->
                            <div class="nlp-tab-pane" id="nlp-pane-lab">
                                <h3 style="font-size:1.1rem;margin-bottom:0.8rem;color:var(--t1);">Interactive NLP Experimentation Sandbox</h3>
                                <p style="font-size:0.85rem;color:var(--t2);margin-bottom:1.5rem;">
                                    Directly test vector arithmetic analogies in Word2Vec space or run BERT contextual token classification inference on arbitrary text.
                                </p>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
                                    <!-- Word Analogy Tester -->
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:18px;border-radius:12px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:12px;color:var(--t1);">Word2Vec Analogy Calculator</h4>
                                        <div style="font-size:0.8rem;color:var(--t3);margin-bottom:8px;">Equation: Vector(pos_b) - Vector(neg_c) + Vector(pos_a)</div>
                                        <div style="display:flex;gap:6px;align-items:center;margin-bottom:12px;">
                                            <input type="text" id="analogy-pos-a" value="python" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:6px;border-radius:6px;width:30%;font-size:0.85rem;">
                                            <span style="color:var(--t3);">+</span>
                                            <input type="text" id="analogy-pos-b" value="backend" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:6px;border-radius:6px;width:30%;font-size:0.85rem;">
                                            <span style="color:var(--t3);">-</span>
                                            <input type="text" id="analogy-neg-c" value="frontend" style="background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:6px;border-radius:6px;width:30%;font-size:0.85rem;">
                                        </div>
                                        <button type="button" class="btn btn-secondary" id="btn-run-analogy" style="width:100%;padding:8px;font-size:0.85rem;">
                                            Solve Vector Analogy →
                                        </button>
                                        <div id="analogy-result-box" style="margin-top:10px;font-size:0.85rem;color:var(--t2);"></div>
                                    </div>

                                    <!-- Custom BERT Sentence Tester -->
                                    <div style="background:var(--bg2);border:1px solid var(--border);padding:18px;border-radius:12px;">
                                        <h4 style="font-size:0.95rem;margin-bottom:12px;color:var(--t1);">Live BERT Token Classification (BIO)</h4>
                                        <textarea id="bert-custom-text" style="width:100%;height:70px;background:var(--bg3);border:1px solid var(--border);color:var(--t1);padding:8px;border-radius:6px;font-size:0.85rem;margin-bottom:10px;" placeholder="Type any sentence e.g. Engineered cloud microservices using Python, Docker, and Kubernetes on AWS."></textarea>
                                        <button type="button" class="btn btn-secondary" id="btn-run-bert-custom" style="width:100%;padding:8px;font-size:0.85rem;">
                                            Run BERT Token Classification →
                                        </button>
                                        <div id="bert-custom-results" style="margin-top:10px;"></div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
'''
    insert_marker = '<div style="text-align: center; margin-top: 40px; margin-bottom: 60px;">'
    if 'id="nlp-deepdive-container"' not in content:
        content = content.replace(insert_marker, deepdive_html + '\n' + insert_marker, 1)

    # 3. Add script tag for nlp-dashboard.js
    if 'src="js/nlp-dashboard.js"' not in content:
        script_marker = '<script src="js/app.js"></script>'
        content = content.replace(script_marker, '<script src="js/nlp-dashboard.js"></script>\n    <script src="js/app.js"></script>', 1)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("index.html successfully updated with Academic NLP Deep Dive UI!")

if __name__ == '__main__':
    update_index()
