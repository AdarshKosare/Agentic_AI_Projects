from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from llm import get_llm
from tools.search import SEARCH_TOOLS
from prompts.system_prompts import (
    RESEARCH_AGENT_SYSTEM_PROMPT,
    WRITER_AGENT_PROMPT,
    CRITIC_AGENT_PROMPT,
    ORCHESTRATOR_PROMPT
)

from memory.conversation import save_session, get_context_for_query
from langgraph.prebuilt import ToolNode


class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    research_topic: str
    sub_questions: list[str]
    research_notes: str
    draft_report: str
    critic_feedback: str
    revision_count: str
    final_report: str

# ── Node 1: Orchestrator ─────────────────────────────────────────────────────
def orchestrator_node(state: MultiAgentState) -> MultiAgentState:
    """
    Breaks the research topic into focuses sub-questions.
    Returns structured JSON with sub_questions list.
    """

    llm = get_llm()
    memory_context = get_context_for_query(state["research_topic"])
    system =  ORCHESTRATOR_PROMPT
    if memory_context:
        system += f"\n\nContext from previous research:\n{memory_context}"
        response = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Research Topic: {state['research_topic']}"),
        ])

        # Parse JSON response
        import json
        try:

            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            sub_questions = data.get("sub_questions", [state["research_topic"]])
        except Exception:
            sub_questions = [state["research_topic"]]

        return {
            # Fallback if LLM doesn't return valid JSON
            "sub_questions": sub_questions,
            "messages":[response],
        }
    
def researcher_node(state: MultiAgentState ) -> MultiAgentState:
    """
    Run the ReAct search agent on each sub-questions.
    Collects all findings into research_notes
    """

    from agents.research_agent import research
    sub_questions = state["sub_questions"]
    if not sub_questions:
        sub_questions = [state["research_topic"]]

    all_notes = []

    for i, question in enumerate(sub_questions, 1):
        print(f"\nResearching sub-question {i}/{len(sub_questions)}: {question}")
        notes = research(question)
        all_notes.append(f"### Sub-question {i}: {question}\n{notes}")

    research_notes = "\n\n---\n\n".join(all_notes)
    return {
        "research_notes" : research_notes,
        "messages":[]
    }

def writer_node(state: MultiAgentState) -> MultiAgentState:
    """
    Takes research notes and writes astructured markdown report.
    It critic_feedback exists, uses it improve the draft.
    """
    llm = get_llm()

    # Build the writing prompt
    if state["critic_feedback"] and state["revision_count"] > 0:
        # Revision mode - Incorporate critic feedback
        user_prompt = f"""Topic: {state["research_topic"]}
Research notes: {state["research_notes"]}
Previous draft: {state["draft_report"]}
Critic feedback to address: {state["critic_feedback"]}

Write ian improved report and report addressing all the critic's feedback.
"""
    else:
        # First draft mode:
        user_prompt = f"""Topic: {state["research_topic"]}
Research notes:
{state["research_notes"]}
Write a comprehensive researc report based on these notes.
"""
    response = llm.invoke([
        SystemMessage(content=WRITER_AGENT_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    return {
        "draft_report": response.content,
        "messages": [response]
    }


def critic_node(state: MultiAgentState) -> MultiAgentState:
    """
    Reveiws the draft report and return s either:
    - "APPROVED" on first line - report is good
    - "NEEDS_REVESION"  on first line - followed by specific issues
    """

    llm = get_llm()

    response = llm.invoke([
        SystemMessage(content=CRITIC_AGENT_PROMPT),
        HumanMessage(content=f"""Review this research report:
Topic: {state["research_topic"]}

Report:{state["draft_report"]} 
"""),
    ])
    return {
        "critic_feedback": response.content,
        "revision_count":state["revision_count"] + 1,
        "messages":[response],
    }

def should_revise(state: MultiAgentState) -> str:
    """
    Route after critic node:
    - "end" -> critic approved OR max revision reached
    - "revise" -> needs revision AND under limit
    """

    feedback = state["critic_feedback"]
    first_line = feedback.split("\n")[0].strip()

    if first_line == "APPROVED":
        return "end"
    
    if state["revision_count"] >= 2:
        #Force exit after iteration - prevent infiinte loop
        return "end"
    
    return "revise"

# --- Node 5: Save Report ---
def save_report_node(state: MultiAgentState) -> MultiAgentState:
    """
    Final node - Saves session to memory anbd return report.
    """
    report = state["draft_report"]
    save_session(
        topic=state["research_topic"],
        report=report,
    )
    return {"final_report":report}

# --- Graph Builder ---
def build_multi_agent_graph():
    graph = StateGraph(MultiAgentState)

    # Add all nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer",writer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("save_report", save_report_node)

    # Wire edges
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator","researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer","critic")
    graph.add_conditional_edges(
        "critic",
        should_revise,
        {
            "revise":"writer",
            "end" : "save_report"
        },
    )

    graph.add_edge("save_report",END)

    return graph.compile()

# --- Public entry point ---
def run_multi_agent(topic : str) -> str:
    agent = build_multi_agent_graph()
    initial_state: MultiAgentState ={
        "messages":[],
        "research_topic": topic,
        "sub_questions": [],
        "research_notes": "",
        "draft_report": "",
        "critic_feedback":"",
        "revision_count":0,
        "final_report":"",
    }

    final_state = agent.invoke(
        initial_state,
        config={"recursin_limit": 50},
    )

    return final_state.get("final_report", "No report generated")