"""date-tool-mcp 的 MCP 服务实现。

服务名与工具在此定义，既被 ``python -m date_tool_mcp`` 使用，
也被仓库根目录的 ``server.py`` 复用。
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("date-tool-mcp")


@mcp.tool()
def get_today() -> str:
    """返回当前的年月日，格式 YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")
