"""LangGraph pipeline: retrieve_context -> generate_answer.

This is the core of the RAG flow. Keeping it as an explicit two-node graph
(rather than a single function) makes each stage independently traceable in
LangSmith and easy to extend later (e.g. adding a query-rewriting node).
"""

from functools import lru_cache

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app import config
from app.graph.state import RecruiterState
from app.llm.provider import get_llm
from app.prompts.recruiter import SYSTEM_PROMPT, build_user_message
from app.rag.retriever import retrieve_relevant_chunks


def retrieve_context(state: RecruiterState) -> dict:
    chunks = retrieve_relevant_chunks(state["question"])
    return {"retrieved_context": chunks}


def generate_answer(state: RecruiterState) -> dict:
    llm = get_llm()

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for turn in state.get("chat_history", []):
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    messages.append(
        HumanMessage(
            content=build_user_message(
                question=state["question"],
                profile=state.get("profile", {}),
                retrieved_context=state.get("retrieved_context", []),
            )
        )
    )

    response = llm.invoke(messages)
    return {"answer": response.text}


@lru_cache(maxsize=1)
def build_graph():
    graph = StateGraph(RecruiterState)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_answer", generate_answer)
    graph.add_edge(START, "retrieve_context")
    graph.add_edge("retrieve_context", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


def run_graph(question: str, chat_history: list[dict], profile: dict) -> RecruiterState:
    compiled = build_graph()
    return compiled.invoke(
        {
            "question": question,
            "chat_history": chat_history,
            "profile": profile,
            "retrieved_context": [],
            "answer": "",
        },
        config={
            "tags": ["recruiter-chat"],
            "metadata": {"project": config.LANGCHAIN_PROJECT},
        },
    )
