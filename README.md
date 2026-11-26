# date-tool-mcp

把「查询今天日期」封装成标准 MCP（Model Context Protocol）工具，供 Claude Desktop、Cursor、Trae、ChatMCP 等任意 MCP 客户端调用。

- 作者主页：https://github.com/zxk0311/date-tool-mcp
- 许可证：MIT
- 服务名：`date-tool-mcp`
- 运行方式：stdio（本地） / SSE（网络）

---

## 项目简介

`date-tool-mcp` 是一个最小可用的 MCP Server 示例，基于官方 `FastMCP` 框架实现。

开发这个服务的想法很简单：MCP 协议虽然强大，但初学者往往卡在「写什么、怎么跑、怎么接客户端」这三步。本项目把最典型的场景——**让大模型知道今天是几号**——完整走通，代码不到 15 行，可以作为编写自己 MCP Server 的起点模板。

核心能力：

| 工具名 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `get_today` | 无 | `str` | 返回当前年月日，格式 `YYYY-MM-DD`，例如 `2026-11-26` |

工具的描述（docstring）会通过 MCP 协议自动暴露给 LLM，模型据此判断何时调用。

依托 `get_today` 这一能力，上层 Agent 可以实现：日期感知的日程安排、文件按日期归档命名、时效性内容判断、时间戳自动补全等场景。

---

## 部署指南

### 1. 环境依赖

- Python 3.10 及以上
- `mcp >= 1.28.1`

依赖已在 `requirements.txt` 中声明：

```
mcp>=1.28.1
```

### 2. 安装

```bash
pip install -r requirements.txt
```

或直接安装：

```bash
pip install "mcp>=1.28.1"
```

### 3. 运行服务

**方式一：stdio 模式（默认，推荐本地使用）**

```bash
python server.py
```

`mcp.run()` 默认走 stdio 传输，服务通过标准输入输出与客户端通信。
注意：stdio 模式下终端看起来会「卡住」，这是正常的，它必须由 MCP 客户端拉起，不要手动运行后期待输出。

**方式二：以包的方式运行**

```bash
pip install -e .
python -m date_tool_mcp          # 等价于 date-tool-mcp
```

**方式三：HTTP 模式（客户端通过网络连接时）**

```bash
python -m date_tool_mcp --transport sse               # http://127.0.0.1:8000/sse
python -m date_tool_mcp --transport streamable-http   # http://127.0.0.1:8000/mcp
```

可用 `--host` / `--port` 改监听地址，例如 `--host 0.0.0.0 --port 8000`。
启动后保持该终端不关闭，再用客户端连接对应地址。

**方式四：Docker**

```bash
docker build -t date-tool-mcp .
docker run -p 8000:8000 date-tool-mcp
```

### 4. 客户端配置

在客户端的 `mcpServers` 配置中加入：

```json
{
  "mcpServers": {
    "date-tool-mcp": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

SSE 模式配置：

```json
{
  "mcpServers": {
    "date-tool-mcp": {
      "transport": "sse",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

> 若客户端启动时报 `No module named 'mcp'`，请把 `command` 改为解释器的绝对路径，例如 `D:/anaconda3/envs/fastapi_env01/python.exe`，并把 `args` 中的 `server.py` 改为绝对路径（Windows 下用 `r"..."` 或正斜杠）。

### 5. 托管部署说明

本服务为纯 Python 实现，无外部服务依赖，可直接托管部署：

- 依赖安装：`pip install -r requirements.txt`（或 `pip install .`）
- 启动命令（HTTP 对外服务）：`python -m date_tool_mcp --transport streamable-http --host 0.0.0.0 --port 8000`
- 容器方式：按根目录 `Dockerfile` 构建，容器内同样以 `streamable-http` 启动并暴露 8000 端口
- 无需任何 API Key / 环境变量 / 数据库

项目具备标准 Python 包结构（`pyproject.toml` + `src/date_tool_mcp`），命令入口声明为：

```toml
[project.scripts]
date-tool-mcp = "date_tool_mcp:main"
```

### 6. 用代码调用（LangChain 示例）

服务端可被 `langchain-mcp-adapters` 转换为 LangChain 工具，交给 Agent 使用：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "date-tool": {
        "command": "python",
        "args": ["server.py"],
        "transport": "stdio",
    }
})

tools = await client.get_tools()   # 得到 [get_today] 工具
```

---

## 使用示例

**示例 1：Agent 自动调用**

用户提问：「今天是几号？」

Agent 识别到需要日期信息，自动调用 `get_today`，工具返回：

```
2026-11-26
```

Agent 回答：「今天是 2026 年 11 月 26 日。」

**示例 2：在 MCP Inspector 中调试**

```bash
npx @modelcontextprotocol/inspector python server.py
```

在 Inspector 界面中可看到工具列表 `get_today`，点击 `Run Tool` 即返回：

```json
{
  "content": [
    {
      "type": "text",
      "text": "2026-11-26"
    }
  ]
}
```

**示例 3：客户端接入后的效果**

在支持 MCP 的客户端中配置好本服务后，工具面板会出现 `get_today`；对话中询问日期时，模型会显示一次工具调用记录，并把返回值整合进回答。

> 建议在此处补充一张客户端工具调用效果截图，更直观。

---

## 项目结构

```
date-tool-mcp/
├── src/date_tool_mcp/
│   ├── __init__.py    # 包入口 main()，支持 --transport / --host / --port
│   ├── __main__.py    # 支持 python -m date_tool_mcp
│   └── server.py      # MCP 服务实现（FastMCP + get_today 工具）
├── server.py          # 根目录直跑脚本（python server.py，stdio）
├── pyproject.toml     # 包元信息、依赖、命令入口（[project.scripts]）
├── Dockerfile         # 容器构建，默认 streamable-http 对外服务
├── requirements.txt   # 依赖清单（pip 直装方式）
├── chatmcp.yaml       # ChatMCP 市场配置
└── README.md          # 本说明文件
```

---

## 扩展新工具

在 `server.py` 中新增函数并加 `@mcp.tool()` 装饰器即可，docstring 会作为工具说明暴露给模型：

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """两数相加。"""
    return a + b
```

重启服务后，客户端重新拉取工具列表即可看到新工具。

---

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | 当前 `python` 不是装好依赖的环境 | 用解释器绝对路径，或先激活对应虚拟环境 |
| `McpError: Connection closed` | 子进程启动即崩溃 | 检查 `args` 路径是否被转义破坏、解释器是否缺包 |
| `SyntaxWarning: invalid escape sequence '\T'` | Windows 路径用了普通字符串 | 改为 `r"D:/..."` 或正斜杠 |
| `httpx.ConnectError: All connection attempts failed` | 客户端配置为 SSE，但服务端未启动 | 先运行 `mcp.run(transport="sse")`，或改回 stdio |
| stdio 模式下终端无响应 / 闪退 | 正常现象，必须由客户端拉起 | 用客户端配置接入，不要手动跑 |

---

## License

MIT
