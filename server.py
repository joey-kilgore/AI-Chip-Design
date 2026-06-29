import itertools
import os
import re
import subprocess
import tempfile

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("verilog")


@mcp.tool()
def simulate_verilog(verilog_path: str) -> dict:
    """
    Simulate a simple combinational Verilog module.

    Returns the simulator output for every possible 1-bit input combination.
    """

    with open(verilog_path) as f:
        source = f.read()

    # Find module name
    module_match = re.search(r"module\s+(\w+)\s*\(", source)
    if not module_match:
        return {"error": "Could not find module declaration."}

    module_name = module_match.group(1)

    # Find inputs
    inputs = re.findall(r"input\s+(?:wire\s+|reg\s+)?(\w+)", source)

    # Find outputs
    outputs = re.findall(r"output\s+(?:wire\s+|reg\s+)?(\w+)", source)

    if not inputs or not outputs:
        return {"error": "Could not determine module inputs/outputs."}

    tb = []

    tb.append("`timescale 1ns/1ps")
    tb.append("")
    tb.append("module tb;")
    tb.append("")

    for inp in inputs:
        tb.append(f"reg {inp};")

    for out in outputs:
        tb.append(f"wire {out};")

    tb.append("")
    tb.append(f"{module_name} dut (")

    ports = []
    for p in inputs + outputs:
        ports.append(f".{p}({p})")

    tb.append(",\n".join(ports))
    tb.append(");")
    tb.append("")
    tb.append("initial begin")

    # Every possible input combination
    for values in itertools.product([0, 1], repeat=len(inputs)):

        for name, value in zip(inputs, values):
            tb.append(f"    {name} = {value};")

        tb.append("    #1;")

        fmt = " ".join(["%b"] * (len(inputs) + len(outputs)))
        signals = ", ".join(inputs + outputs)

        tb.append(f'    $display("{fmt}", {signals});')
        tb.append("")

    tb.append("    $finish;")
    tb.append("end")
    tb.append("")
    tb.append("endmodule")

    tb_source = "\n".join(tb)

    with tempfile.TemporaryDirectory() as tmp:

        module_copy = os.path.join(tmp, "module.v")
        tb_file = os.path.join(tmp, "tb.v")
        exe = os.path.join(tmp, "sim")

        with open(module_copy, "w") as f:
            f.write(source)

        with open(tb_file, "w") as f:
            f.write(tb_source)

        compile_result = subprocess.run(
            ["iverilog", "-o", exe, module_copy, tb_file],
            capture_output=True,
            text=True,
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "stage": "compile",
                "stderr": compile_result.stderr,
            }

        run_result = subprocess.run(
            ["vvp", exe],
            capture_output=True,
            text=True,
        )

        return {
            "success": run_result.returncode == 0,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "inputs": inputs,
            "outputs": outputs,
            "testbench": tb_source,
        }


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    Say hello.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
