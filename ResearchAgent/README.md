# DeepResearch Agent

An autonomous multi-agent system that researches any topic, retrieves documents, reasons across sources, and produces a cited markdown report.

Built as a learning project to master agentic AI engineering — every component has interview talking points baked in.

## Architecture

```
User Query
    │
    ▼
Orchestrator Agent          ← Week 3
    ├── Research Agent       ← Week 1 ✅ (ReAct loop, web search)
    │       └── Tools: web_search, web_search_deep
    ├── RAG Agent            ← Week 2 (ChromaDB, reranking)
    └── Writer + Critic      ← Week 3 (reflection pattern)
            │
            ▼
    FastAPI Streaming API    ← Week 4
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent framework | LangGraph (state machine) |
| LLM primary | Gemini 1.5 Flash (free) |
| LLM fallback | Ollama llama3.1:8b (local) |
| Web search | Tavily API / DuckDuckGo |
| Vector DB | ChromaDB |
| Embeddings | all-MiniLM-L6-v2 |
| API | FastAPI + streaming |
| Evals | RAGAS + LangSmith |

## Setup

### 1. Clone and install

```bash
cd D:\ADARSH\Preparation\AI\GetJobReady\ai-engineering
# Copy this project folder here

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — add your GOOGLE_API_KEY (required)
# Add TAVILY_API_KEY if you have one (free at tavily.com)
```

### 3. Verify setup

```bash
python test_week1.py
```

### 4. Run

```bash
# Single query
python main.py "What are the latest breakthroughs in AI reasoning?"

# Interactive mode
python main.py
```

## Weekly Build Plan

| Week | What we build | Skills learned |
|------|--------------|----------------|
| 1 ✅ | ReAct agent + web search | LangGraph, tool use, ReAct pattern |
| 2 | RAG pipeline + ChromaDB | Embeddings, chunking, reranking |
| 3 | Multi-agent orchestration | LangGraph multi-node, reflection |
| 4 | FastAPI + evals + Docker | Production deployment, RAGAS |

## Interview Talking Points

**"What is a ReAct agent?"**
> A ReAct agent alternates between Reasoning (deciding what to do) and Acting (calling tools). LangGraph implements this as a state machine: the LLM node decides whether to call tools or finish, and conditional edges route accordingly.

**"Why LangGraph over LangChain AgentExecutor?"**
> LangGraph gives explicit control over the agent loop as a compiled graph. You can add human-in-the-loop nodes, parallel branches, and custom state — AgentExecutor is a black box.

**"How do you prevent infinite agent loops?"**
> Two mechanisms: `recursion_limit` on the graph invocation (hard cap on node executions), and the `should_continue` conditional edge that routes to END when the LLM stops calling tools.
