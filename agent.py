import os

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model

#
# Model aliases
#
MODEL_ALIASES = {
    "gpt-4.1": "openai:gpt-4.1",
    "qwen3": "openai:qwen3-30b",
    "qwen3:30b": "openai:qwen3-30b",
    "qwen3:32b": "openai:qwen3-32b",
}


def init_model(model_alias: str):
    """
    Initialize a chat model from a short alias.
    """

    if model_alias not in MODEL_ALIASES:
        raise ValueError(
            f"Unknown model '{model_alias}'. "
            f"Available models: {list(MODEL_ALIASES.keys())}"
        )

    model_name = MODEL_ALIASES[model_alias]

    return init_chat_model(
        model_name,
        base_url=os.getenv("OPENAI_API_BASE", "http://localhost:8080/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
    )


def build_agent(model_alias: str, tools: list):
    """
    Build a simple LangGraph agent with MCP tools.
    """

    model = init_model(model_alias)

    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": response}

    graph = StateGraph(MessagesState)

    graph.add_node("model", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", tools_condition)
    graph.add_edge("tools", "model")

    return graph.compile()
