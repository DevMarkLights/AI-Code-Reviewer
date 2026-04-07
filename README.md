# 🤖 AI Code Reviewer

An agentic code review system that analyzes GitHub Pull Requests using a parallel multi-agent pipeline. Submit a PR URL and three specialized AI agents run concurrently to detect bugs, security vulnerabilities, and performance issues — then automatically post a structured review comment directly to the PR.

**Live Demo:** [Ai Code Reviewer]([https://marks-pi.com](https://marks-pi.com/ai-code-reviewer/))

---

## Architecture

```
PR URL → FastAPI → GitHub API (fetch diff + full file context)
                         ↓
              ┌─────────────────────┐
              │    LangGraph Graph   │
              │                     │
              │      fanOut node     │
              └─────────────────────┘
               ↙          ↓         ↘
         Bug Agent  Security Agent  Performance Agent
          (Groq)       (Groq)          (Groq)
               ↘          ↓         ↙
              ┌─────────────────────┐
              │     Writer Agent    │
              │   (formats review)  │
              └─────────────────────┘
                         ↓
              GitHub API (post comment)
```

The three analysis agents run **concurrently** using LangGraph's `Send` API, meaning all three complete in the time it takes one to run. The writer agent waits for all findings to merge before formatting the final review.

---

## Features

- **Parallel agent execution** — Bug, security, and performance agents run simultaneously via LangGraph `Send`
- **Full file context** — Fetches complete file contents alongside the diff patch to avoid false positives from missing context
- **Auto-posts to GitHub** — Posts the formatted review as a comment directly on the PR
- **Grounded analysis** — Agents are prompted to analyze only what's in the diff, not hallucinate issues
- **Clean markdown output** — Structured review with emoji-labeled sections for readability

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| LLM Backend | Groq (`llama-3.3-70b-versatile`) |
| API | FastAPI |
| Frontend | React |
| GitHub Integration | GitHub REST API v3 |
| Deployment | Raspberry Pi 5 via Cloudflare Tunnel |


## Author

**Mark Lights**
- Portfolio: [markjarredlights.com](https://markjarredlights.com)
- GitHub: [@DevMarkLights](https://github.com/DevMarkLights)
