from langgraph.graph import StateGraph, START, END

from orchestrator.agents import *
from orchestrator.states import State


# ---------- GRAPH ----------
def create_graph():
    workflow = StateGraph(State)

    workflow.add_node("Planner", planner_agent)
    workflow.add_node("Architect", architect_agent)
    workflow.add_node("Coder", coder_agent)

    workflow.add_edge(START, "Planner")
    workflow.add_edge("Planner", "Architect")
    workflow.add_edge("Architect", "Coder")

    # Add conditional edge ONLY - don't add regular edge to END
    workflow.add_conditional_edges(
        "Coder",
        check_coder_progress,
        {
            "continue": "Coder",  # Loops back to itself
            "end": END
        }
    )

    return workflow.compile()


def run_graph(user_request: str):
    graph = create_graph()
    output = graph.invoke({"user_request": user_request}, {"recursion_limit": 100})
    return output