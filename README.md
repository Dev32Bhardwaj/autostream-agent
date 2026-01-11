# AutoStream Conversational AI Agent

## Overview

This project implements a **Conversational AI Agent** for AutoStream, a fictional SaaS platform that provides automated video editing tools for content creators. The agent is designed to:

- Understand user intent
- Answer product and pricing questions using a **RAG-based knowledge retrieval system**
- Detect high-intent users and capture lead details
- Trigger a mock backend function (`mock_lead_capture`) after collecting all necessary information

---

## Features

1. **Intent Identification**
   - `greeting` → casual user greetings
   - `product_inquiry` → questions about plans and features
   - `high_intent` → users ready to sign up

2. **RAG-Powered Knowledge Retrieval**
   - Local knowledge base stored in `data/knowledge_base.md`
   - Uses **FAISS vector store** with **HuggingFace embeddings** for semantic search
   - Falls back to raw Markdown content if LLM or embeddings fail

3. **High-Intent Lead Capture**
   - Collects **Name → Email → Platform** in order
   - Calls `mock_lead_capture()` only after all three are collected
   - Ensures agent does not prematurely trigger lead capture

4. **State Management**
   - Tracks **conversation history** using LangGraph
   - Maintains memory across multiple turns
   - Separates `user_messages` and `agent_messages`

---

## Requirements

- Python 3.9+
- Virtual environment recommended (`venv` or `conda`)
- Install dependencies:

```bash
pip install -r requirements.txt
```

### requirements.txt:
```bash
langchain==1.2.3
langgraph==1.0.5
langchain_huggingface
langchain_community
faiss-cpu
openai
```

> [!NOTE]
> faiss-cpu is required for the vector store backend.
> HuggingFaceEmbeddings allows local embeddings without OpenAI API calls.

----

## AutoStream Agent — Folder Structure

```graphsql
autostream-agent/
│
├── agent/
│   ├── graph.py          # Agent logic, state, and LangGraph nodes
│   ├── intents.py        # Intent detection logic
│   ├── rags.py           # RAG pipeline using FAISS + HuggingFace embeddings
│   ├── tools.py          # mock_lead_capture and other tools
│
├── data/
│   └── knowledge_base.md # Pricing, features, policies (Markdown)
│
├── main.py               # Entry point to run the agent
├── requirements.txt      # All dependencies
├── README.md             # Project overview, instructions, architecture, WhatsApp note
├── demo_video.mp4
└── .gitignore

```

### Recommended File Details

1. `agent/graph.py`
    * Handles the LangGraph agent node, conversation state, and intent routing.
    * Calls get_pricing_response() and mock_lead_capture().
    * Maintains AgentState with messages, intent, name, email, platform.

2. `agent/intents.py`
    * Keyword-based intent detection for:
        <ol type="a">
        <li>greeting</li>
        <li>product_inquiry</li>
        <li>high_intent</li>
        </ol>

3. `agent/rags.py`
    * Loads the knowledge base from `data/knowledge_base.md`.
    * Uses **FAISS + HuggingFace** embeddings for semantic search.
    * Exposes `load_rag()` and optionally `get_pricing_response(query)`.

4. `agent/tools.py`
    * `mock_lead_capture(name, email, platform)` function.

5. main.py
    * Starts a terminal chat session.
    * Loops through user input, appends messages to state, and invokes the graph.
    * Type exit to quit.

----

## Running the Project Locally
```bash
python main.py
```
* Type messages as the user
* Type `exit` to quit
* The agent will:
    1. Greet you
    2. Answer pricing or product questions using RAG
    3. Detect high-intent and collect **Name → Email → Platform**
    4. Call `mock_lead_capture` once all details are collected

----

## Architecture Explanation

This agent is built using **LangGraph**, a stateful graph-based framework that allows defining nodes for agent logic and managing conversation memory across multiple turns.

The agent node handles three primary functionalities:

**Intent Detection**: User messages are classified into `greeting`, `product_inquiry`, or `high_intent` using a simple keyword-based function. The intent determines the next response flow.

**Knowledge Retrieval (RAG)**: Product and pricing questions are answered by querying a local FAISS vector store with HuggingFace embeddings. This allows semantic search over the Markdown knowledge base without relying on live OpenAI API calls. If the vector store is unavailable, the agent falls back to raw Markdown text.

**Lead Capture**: For `high-intent users`, the agent sequentially collects **Name, Email, and Platform**, maintaining state using a high_intent_stage variable. The mock API function `mock_lead_capture()` is called only after all details are collected, ensuring proper tool execution.

LangGraph’s stateful memory ensures conversation history is preserved across 5–6 turns, providing contextual responses and a realistic chat experience.

----

## WhatsApp Deployment (Webhook Integration)

To deploy this agent on **WhatsApp**:
1. Use a service like **Twilio WhatsApp API** or **360dialog WhatsApp API** to receive user messages via a webhook.
2. Configure the webhook URL to point to a **Flask/FastAPI endpoint** running your LangGraph agent.
3. On receiving a message:
    * Append the user message to the agent’s `user_messages` state
    * Invoke the LangGraph graph
    * Send the agent’s response back to WhatsApp via the API

4. Maintain session state per user (e.g., using a dictionary keyed by WhatsApp from number) to handle multi-turn conversations.
5. Ensure `mock_lead_capture` or real lead capture is triggered only after collecting all required details.