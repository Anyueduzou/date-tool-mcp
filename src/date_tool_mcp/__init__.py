"""date-tool-mcp：最小可用的 MCP 服务示例。"""

import argparse

from .server import mcp

__version__ = "0.1.0"
__all__ = ["mcp", "main"]


def main() -> None:
    """命令行入口。

    默认 stdio（本地客户端使用）；托管部署时用 ``--transport streamable-http``
    或 ``--transport sse`` 对外提供 HTTP 服务。
    """
    parser = argparse.ArgumentParser(
        prog="date-tool-mcp",
        description="提供 get_today 工具的 MCP 服务",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="传输方式，默认 stdio",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP 模式监听地址")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 模式监听端口")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
        return

    mcp.settings.host = args.host
    mcp.settings.port = args.port
    mcp.run(transport=args.transport)
