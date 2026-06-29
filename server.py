from fastmcp import FastMCP

mcp = FastMCP("Demo Server")


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    Say hello.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="http")
