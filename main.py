import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient

from agent import build_agent


SYSTEM_PROMPT = """
You are a helpful AI assistant.

You have access to tools provided by an MCP server.
Use them whenever they are useful.
"""


async def main():

    # Connect to the MCP server
    client = MultiServerMCPClient(
        {
            "demo": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            }
        },
        tool_name_prefix=True,
    )

    # Discover available tools
    tools = await client.get_tools()

    print("Available tools:")
    for tool in tools:
        print(" -", tool.name)

    # Create the agent
    graph = build_agent(
        model_alias="qwen3",
        tools=tools,
    )

    while True:

        query = input("\n> ")

        if query.lower() in ["exit", "quit"]:
            break

        result = await graph.ainvoke(
            {
                "messages": [
                    ("system", SYSTEM_PROMPT),
                    ("human", query),
                ]
            }
        )

        print("\nAssistant:")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
