# model card: `mujtaba-v1`

> A full stack developer, fine-tuned on AI products. Currently deployed at Coding The Brains.

| | |
|---|---|
| **Architecture** | Python, FastAPI, Django, PostgreSQL, React, Flutter |
| **Pretraining** | BS Computer Science (Data Science), 2022 to 2026 |
| **Fine-tuned on** | LLM agents, RAG, vision and speech models in production |
| **Languages** | English, Urdu, Pashto |
| **Inference hours** | Day or night shift |
| **License** | Open to work |

## Evals

| Benchmark | Result |
|---|---|
| Tools wired into one agent | 17, with guardrails and spend caps |
| Automated tests on one backend | 388 |
| Records loaded by one pipeline | about 2.9M |
| Image cost of a vision pipeline | down about 60%, same output |

## Known limitations

- Asks what a model costs per request before asking how smart it is.
- Won't answer without sources. A RAG habit.

## Checkpoints

- [sakinah-fyp](https://github.com/syedmujtaba-s/sakinah-fyp): emotion detection from a face photo or journal text, with guidance retrieved through RAG. FastAPI, MongoDB Atlas Vector Search, Flutter.
- [faith-brains](https://github.com/syedmujtaba-s/faith-brains): Quran and Hadith search with cited answers. FastAPI, pgvector, Next.js.
- [sidebrain-watch](https://github.com/syedmujtaba-s/sidebrain-watch): standalone Wear OS app for a wearable AI assistant. Kotlin, Jetpack Compose.

## Usage

```python
from github import mujtaba

mujtaba.hire(role="AI engineer", start="immediately")
```

[LinkedIn](https://www.linkedin.com/in/syedmujtaba-s) · mujtabashah.dev@gmail.com
