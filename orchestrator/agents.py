import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from tavily import TavilyClient

from orchestrator.prompts import *
from orchestrator.states import *
from orchestrator.tools import *

load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ---------- PLANNER AGENT ----------
def planner_agent(state: State):

    print("-" * 100)
    print("----- PLANNER AGENT IN PROGRESS -----")

    user_request = state.get("user_request")

    prompt = research_prompt(user_request)

    search_query = llm.invoke([HumanMessage(content=prompt)]).content.strip()

    print(f"Searching the web for '{search_query}'...")

    context_data = ""

    try:
        search_result = tavily_client.search(query=search_query, search_depth="advanced", max_results=3)

        context_data = "\n".join([
            f"- Title: {res['title']}\n  Content: {res['content']}\n  URL: {res['url']}"
            for res in search_result['results']
        ])
        print(f"PLANNER AGENT: Found relevant insights from {len(search_result['results'])} sources.")

    except Exception as e:
        print(f"PLANNER AGENT: Search failed ({e}). Proceeding with general knowledge.")
        context_data = "No search results available."

    structured_llm = llm.with_structured_output(Plan)
    system_prompt = planner_prompt(user_request, context_data)

    plan = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_request)
    ])

    print(f"\nPlan created for: {plan.project_name}\n")
    print("-" * 100)

    return {
        "Plan": plan,
        "project_name": plan.project_name
    }


# ---------- ARCHITECT AGENT ----------
def architect_agent(state: State) -> dict:

    print("-" * 100)
    print("----- ARCHITECT AGENT IN PROGRESS -----")

    plan = state.get("Plan", [])

    prompt = architect_prompt(plan=plan.model_dump_json())
    structured_llm = llm.with_structured_output(TaskPlan)
    task_plan = structured_llm.invoke(prompt)

    print(f"\n✅ Created {len(task_plan.implementation_steps)} implementation steps\n")
    print("-" * 100)

    return {
        "TaskPlan": task_plan
    }


# ---------- CODER AGENT ----------
def coder_agent(state: State) -> dict:

    print("-" * 100)
    print("----- CODER AGENT IN PROGRESS -----")

    project_name = state["project_name"]
    task_plan = state["TaskPlan"]
    current_step_idx = state.get('current_step_idx', 0)

    steps = task_plan.implementation_steps

    if current_step_idx >= len(steps):
        return {
            "messages": [AIMessage(content="All coding tasks completed.")]
        }

    current_task = steps[current_step_idx]

    print(f"👨‍💻 CODER AGENT - Step {current_step_idx + 1}/{len(steps)}")
    print(f"Working on: {current_task.filepath}\n")

    try:
        existing_content = read_file.invoke({"project_name": project_name, "path": current_task.filepath})
    except Exception:
        existing_content = "(File does not exist yet.)"

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Step {current_step_idx + 1}/{len(steps)}\n"
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing Content Length: {len(existing_content)} chars\n\n"
        f"Project Name: {project_name}\n"
        "Implement the code now."
    )

    coder_tools = [create_project_folder, create_file, write_file, update_file, read_file, list_project_files, get_relevant_image]
    llm_with_tools = llm.bind_tools(coder_tools)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    # Get initial response
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    # Execute tool calls if any
    while response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Find and execute the tool
            tool_map = {tool.name: tool for tool in coder_tools}
            if tool_name in tool_map:
                try:
                    result = tool_map[tool_name].invoke(tool_args)
                    messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))
                except Exception as e:
                    messages.append(ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_call["id"]
                    ))

        # Get next response
        response = llm_with_tools.invoke(messages)
        messages.append(response)

    return {
        "current_step_idx": current_step_idx + 1,
        "messages": messages
    }


def check_coder_progress(state: State):
    current = state.get("current_step_idx", 0)
    total = len(state["TaskPlan"].implementation_steps)

    if current >= total:
        return "end"
    return "continue"