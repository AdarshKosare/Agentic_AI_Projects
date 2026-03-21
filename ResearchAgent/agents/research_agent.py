"""
agents/research_agent.py — ReAct-based research agent

INTERVIEW TALKING POINT:
  "ReAct stands for Reasoning + Acting. The agent alternates between:
   - Thought: 'I need to find X, let me search for Y'
   - Action: calls web_search('Y')
   - Observation: receives search results
   - ... repeat until confident ...
   - Final Answer: synthesized response

   This loop is implemented as a LangGraph state machine where each node
   is either the LLM reasoning step or the tool execution step."

WHY LANGGRAPH OVER LANGCHAIN AGENTEXECUTOR:
  LangGraph gives you explicit control over the agent loop as a graph.
  You can add conditional edges, human-in-the-loop checkpoints, parallel
  branches. AgentExecutor is a black box — LangGraph is transparent.

C++ ANALOGY:
  LangGraph state machine ≈ a state machine with explicit transitions.
  The state struct is passed between nodes, each node reads/writes it.
  Conditional edges are like switch statements on state fields.
"""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from llm import get_llm
from tools.search import SEARCH_TOOLS
from prompts.system_prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from rich.console import Console

console = Console()


# ── State Definition ────────────────────────────────────────────────────────
# INTERVIEW TALKING POINT:
#   "The State is a TypedDict — the single source of truth passed between
#    every node in the graph. add_messages is a reducer that appends new
#    messages rather than replacing the list. This is how LangGraph handles
#    the growing conversation history without you managing it manually."

class ResearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    research_topic: str
    final_report: str


# ── Node Functions ───────────────────────────────────────────────────────────

def call_llm(state: ResearchState, llm_with_tools) -> ResearchState:
    """
    LLM reasoning node.
    The LLM sees all messages so far and either:
    - Returns a tool call (want to search)
    - Returns a final text response (done researching)
    """
    messages = state["messages"]

    # Inject system prompt as first message if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=RESEARCH_AGENT_SYSTEM_PROMPT)] + list(messages)

    console.print(f"\n[bold purple]Agent thinking...[/bold purple]")
    response = llm_with_tools.invoke(messages)

    # Show what the agent is doing
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            console.print(f"[cyan]  Tool call:[/cyan] {tc['name']}({tc['args']})")
    else:
        console.print(f"[green]  Agent responding (no tool calls)[/green]")

    return {"messages": [response]}


def should_continue(state: ResearchState) -> str:
    """
    Conditional edge — the router.

    INTERVIEW TALKING POINT:
      "This is the key decision point in a ReAct loop. If the last message
       has tool_calls, we route to the tools node. If not, the agent is
       done reasoning and we go to END. This is how you prevent infinite
       loops while giving the agent freedom to search multiple times."
    """
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def save_report(state: ResearchState) -> ResearchState:
    """Extract the final response and save it as the report."""
    last_message = state["messages"][-1]
    report = last_message.content if hasattr(last_message, "content") else str(last_message)
    return {"final_report": report}


# ── Graph Builder ────────────────────────────────────────────────────────────

def build_research_agent(tools: list[BaseTool] = None) -> StateGraph:
    """
    Builds and compiles the ReAct agent graph.

    Graph structure:
        START → llm_node → [tool_node → llm_node]* → save_report → END

    The bracketed part repeats until the LLM stops calling tools.
    """
    if tools is None:
        tools = SEARCH_TOOLS

    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    # Build graph
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("llm", lambda s: call_llm(s, llm_with_tools))
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("save_report", save_report)

    # Add edges
    graph.set_entry_point("llm")
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {"tools": "tools", "end": "save_report"},
    )
    graph.add_edge("tools", "llm")          # after tool → back to LLM
    graph.add_edge("save_report", END)

    return graph.compile()


# ── Public Interface ─────────────────────────────────────────────────────────

def research(topic: str) -> str:
    """
    Main entry point. Run the research agent on a topic.

    Usage:
        from agents.research_agent import research
        report = research("Latest developments in LLM reasoning")
    """
    console.print(f"\n[bold]DeepResearch Agent[/bold]")
    console.print(f"[dim]Topic:[/dim] {topic}\n")

    agent = build_research_agent()

    initial_state: ResearchState = {
        "messages": [HumanMessage(content=f"Research this topic thoroughly: {topic}")],
        "research_topic": topic,
        "final_report": "",
    }

    final_state = agent.invoke(
        initial_state,
        config={"recursion_limit": 30},   # safety: max 30 node executions
    )

    report = final_state.get("final_report", "No report generated.")
    console.print(f"\n[bold green]Research complete![/bold green]")
    return report
