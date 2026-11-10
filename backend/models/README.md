# CSE472 Deep Learning for NLP — Models & Embeddings Directory

This directory stores pretrained and fine-tuned model artifacts for **SkillGap AI**:

1. **Word Embeddings (Unit II)**:
   - `word2vec_cbow.model` / `word2vec_skipgram.model`: Domain-specific Gensim Word2Vec models trained on technical resumes, job descriptions, and skills taxonomy.
   - `glove.6B.50d.txt` / `glove.6B.100d.txt` (Optional): Pretrained Stanford GloVe embeddings (Pennington et al., 2014) for dense semantic lookup and analogies.

2. **Transformer Language Models (Unit V)**:
   - `bert-skill-ner/`: Hugging Face `DistilBERT` or `BERT-base-uncased` fine-tuned for token-level Named Entity Recognition (NER) with BIO tags (`B-SKILL`, `I-SKILL`, `O`).
   - Configuration files: `config.json`, `pytorch_model.bin` / `model.safetensors`, `vocab.txt`, `tokenizer.json`.

## Offline & Laptop Execution Strategy
- The system is architected to run seamlessly on standard laptops without GPU requirements.
- If large external model files are not downloaded, the engine automatically uses cached local embeddings and lightweight heuristic fallback without throwing unhandled exceptions or halting application functionality.

