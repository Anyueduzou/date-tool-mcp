# date-tool-mcp

一个基于 [MCP（Model Context Protocol）](https://modelcontextprotocol.io) 的最小可用示例服务：把「查询今天日期」封装成标准 MCP 工具，供 Claude Desktop、Cursor、Trae、ChatMCP 等任意 MCP 客户端调用。

- 作者主页：https://github.com/zxk0311/date-tool-mcp
- 许可证：MIT

---

## 1. 项目结构

```
github提交的mcp/
├── server.py          # MCP 服务端主文件（FastMCP 实现，含 1 个工具）
├── requirements.txt   # 依赖清单
├── chatmcp.yaml       # ChatMCP 客户端市场配置（本地运行 + 客户端接入配置）
└── README.md          # 本说明文件
```

---

## 2. 功能说明

服务端基于官方 `FastMCP` 框架实现，目前提供 1 个工具：

| 工具名 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `get_today` | 无 | `str` | 返回当前年月日，格式 `YYYY-MM-DD`，例如 `2026-11-26` |

工具描述（docstring）会被 MCP 协议自动暴露给 LLM，模型据此判断何时调用。

---

## 3. 环境要求

- Python 3.10 及以上
- `mcp >= 1.28.1`

---

## 4. 安装

```bash
# 建议先创建 / 激活虚拟环境
pip install -r requirements.txt
```

或直接安装：

```bash
pip install "mcp>=1.28.1"
```

---

## 5. 运行

### 方式一：stdio 模式（默认，推荐本地使用）

```bash
python server.py
```

`mcp.run()` 默认走 stdio 传输，服务通过标准输入输出与客户端通信。
**不要直接在终端里手动运行后期待看到输出**——stdio 模式下终端看起来会「卡住」，这是正常的，它必须由 MCP 客户端拉起。

### 方式二：SSE / HTTP 模式（需要客户端走网络连接时）

```python
# 修改 server.py 末尾
mcp.run(transport="sse")        # 默认监听 http://127.0.0.1:8000/sse
```

启动后保持该终端不关闭，再用客户端连接该地址。

---

## 6. 客户端接入

### 6.1 通用配置（Claude Desktop / Cursor / Trae 等）

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

> 建议把 `"command"` 写成解释器的**绝对路径**，避免客户端继承了不同的环境导致缺包，例如：
> ```json
> "command": "D:/anaconda3/envs/fastapi_env01/python.exe"
> ```

### 6.2 SSE 模式配置

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

### 6.3 ChatMCP 市场配置

`chatmcp.yaml` 用于把本服务发布 / 导入 ChatMCP 市场，字段含义：

| 字段 | 说明 |
|---|---|
| `name` | 服务名，需与 `FastMCP("date-tool-mcp")` 保持一致 |
| `description` | 服务简介 |
| `author` | 作者主页 |
| `license` | 开源协议 |
| `tags` | 市场检索标签 |
| `params` | 服务启动参数定义（本服务无参数，故为空对象） |
| `local` | 本地启动命令 |
| `config` | 生成给客户端的 `mcpServers` 配置片段 |

---

## 7. 用代码调用（LangChain 示例）

服务端可以被 `langchain-mcp-adapters` 转换为 LangChain 工具，再交给 Agent 使用：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "date-tool": {
        "command": r"D:/anaconda3/envs/fastapi_env01/python.exe",
        "args": [r"D:/TRAEIDE/agent/1126/github提交的mcp/server.py"],
        "transport": "stdio",
    }
})

tools = await client.get_tools()   # 得到 [get_today] 工具
```

---

## 8. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | 当前 `python` 不是装了依赖的那个环境 | 用绝对路径指定解释器，或 `conda activate` 到装好依赖的环境 |
| `McpError: Connection closed` | 子进程启动即崩溃，客户端连不上 | 多半是 `args` 里的路径被转义破坏或解释器缺包；路径用原始字符串 `r"..."` 或正斜杠 |
| `SyntaxWarning: invalid escape sequence '\T'` | Windows 路径用了普通字符串，`\T`、`\112` 被当成转义符 | 改为 `r"D:/..."` |
| `httpx.ConnectError: All connection attempts failed` | 客户端配置为 SSE，但服务端没启动 | 先运行 `mcp.run(transport="sse")`，或改回 stdio |
| stdio 模式下终端闪退 / 无响应 | 正常现象，stdio 必须由客户端拉起 | 改用客户端配置接入，不要手动跑 |

---

## 9. 扩展新工具

在 `server.py` 中新增函数并加 `@mcp.tool()` 装饰器即可，docstring 会作为工具说明暴露给模型：

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """两数相加。"""
    return a + b
```

重启服务后，客户端重新拉取工具列表即可看到新工具。
