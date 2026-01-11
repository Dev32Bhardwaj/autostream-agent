from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from agent.intents import detect_intent
from agent.tools import mock_lead_capture
from agent.rag import load_rag
from pathlib import Path
import os

# ---------------- LLM SETUP ----------------
def llm_available():
    try:
        from langchain_openai import ChatOpenAI

        if not os.getenv("OPENAI_API_KEY"):
            return None

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # optional ping test
        # llm.invoke("ping")

        return llm

    except Exception:
        return None

LLM = llm_available()

# ---------------- KNOWLEDGE BASE ----------------
KB_PATH = Path("data/knowledge_base.md")
vectorstore = None
if KB_PATH.exists():
    vectorstore = load_rag()

def get_pricing_response(query: str):
    """Return answer from RAG or fallback to markdown text."""
    if vectorstore:
        # Simple similarity search (top 1)
        results = vectorstore.similarity_search(query, k=1)
        if results:
            return results[0].page_content

    # Fallback to raw markdown
    if KB_PATH.exists():
        return KB_PATH.read_text()
    return "Sorry, knowledge base is unavailable."

# ---------------- AGENT STATE ----------------
class AgentState(TypedDict):
    user_messages: list
    agent_messages: list
    intent: Optional[str]
    high_intent_stage: Optional[str]  # can be "name", "email", "platform", or None
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]

# ---------------- AGENT NODE ----------------
def agent_node(state: AgentState):
    # Get last user message
    if not state["user_messages"]:
        last_msg = ""
    else:
        last_msg = state["user_messages"][-1]

    # Check high-intent stage
    if state.get("high_intent_stage"):
        stage = state["high_intent_stage"]

        if stage == "name":
            state["name"] = last_msg
            state["high_intent_stage"] = "email"
            response = "Thanks! May I have your email?"
        elif stage == "email":
            state["email"] = last_msg
            state["high_intent_stage"] = "platform"
            response = "Which platform do you create content on?"
        elif stage == "platform":
            state["platform"] = last_msg
            # Capture lead
            mock_lead_capture(state["name"], state["email"], state["platform"])
            state["high_intent_stage"] = None
            response = "🎉 You're all set! Our team will reach out shortly."

    else:
        # Detect intent only if not already high-intent collection
        intent = detect_intent(last_msg)
        state["intent"] = intent

        if intent == "greeting":
            response = "Hi! 😊 How can I help you with AutoStream today?"
        elif intent == "product_inquiry":
            kb_text = get_pricing_response(last_msg)
            if LLM:
                try:
                    response = LLM.invoke(
                        f"Answer the user using ONLY the information below:\n\n{kb_text}"
                    ).content
                except Exception:
                    response = kb_text
            else:
                response = kb_text
        elif intent == "high_intent":
            # Start high-intent collection flow
            state["high_intent_stage"] = "name"
            response = "Great! Before we proceed, may I have your name?"

    # Save agent response
    state["agent_messages"].append(response)
    return state

# ---------------- GRAPH BUILDER ----------------
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.set_finish_point("agent")
    return graph.compile()
