# Tools Reference

## Search Tools

### Tavily
```python
from dynamiq.nodes.tools import TavilyTool
from dynamiq.connections import Tavily as TavilyConnection

tavily = TavilyTool(
    connection=TavilyConnection(api_key="TAVILY_API_KEY"),
    optimized_for_agents=True  # Format output for agents
)
# Input: {"query": "search term"}
# Output: Formatted search results with sources
```

### ScaleSerp
```python
from dynamiq.nodes.tools import ScaleSerpTool
from dynamiq.connections import ScaleSerp as ScaleSerpConnection

scaleserp = ScaleSerpTool(
    connection=ScaleSerpConnection(api_key="SCALESERP_API_KEY")
)
# Input: {"query": "search term"}
# Output: Search results with URLs and snippets
```

### Jina Search
```python
from dynamiq.nodes.tools import JinaSearchTool
from dynamiq.connections import Jina as JinaConnection

jina_search = JinaSearchTool(
    connection=JinaConnection(api_key="JINA_API_KEY"),
    max_results=10,
    include_images=True
)
```

### Exa
```python
from dynamiq.nodes.tools import ExaTool
from dynamiq.connections import Exa as ExaConnection

exa = ExaTool(connection=ExaConnection(api_key="EXA_API_KEY"))
```

## Scraping Tools

### ZenRows
```python
from dynamiq.nodes.tools import ZenRowsTool
from dynamiq.connections import ZenRows as ZenRowsConnection

zenrows = ZenRowsTool(
    connection=ZenRowsConnection(api_key="ZENROWS_API_KEY"),
    url="https://example.com"  # Optional: can be in input
)
# Input: {"URL": "https://example.com"}
# Output: {"url": "...", "content": "Markdown content"}
```

### Firecrawl
```python
from dynamiq.nodes.tools import FirecrawlTool
from dynamiq.connections import Firecrawl as FirecrawlConnection

firecrawl = FirecrawlTool(
    connection=FirecrawlConnection(api_key="FIRECRAWL_API_KEY")
)
```

### Jina Scrape
```python
from dynamiq.nodes.tools import JinaScrapeTool
from dynamiq.connections import Jina as JinaConnection

jina_scrape = JinaScrapeTool(
    connection=JinaConnection(api_key="JINA_API_KEY"),
    response_format="markdown"  # or "default", "html", "text"
)
```

## Execution Tools

### Python
```python
from dynamiq.nodes.tools import Python

python_tool = Python()
# Execute arbitrary Python code
# Input: {"code": "print('hello')"}
```

### E2B Code Interpreter
```python
from dynamiq.nodes.tools import E2BInterpreterTool
from dynamiq.connections import E2B as E2BConnection

e2b = E2BInterpreterTool(
    connection=E2BConnection(api_key="E2B_API_KEY")
)
# Secure sandboxed code execution
```

### HTTP API Call
```python
from dynamiq.nodes.tools import HttpApiCall
from dynamiq.connections import HttpApiCall as HttpApiCallConnection

http_tool = HttpApiCall(
    connection=HttpApiCallConnection(
        url="https://api.example.com",
        method="GET",  # GET, POST, PUT, DELETE, PATCH
        headers={"Authorization": "Bearer token"}
    )
)
```

### SQL Executor
```python
from dynamiq.nodes.tools import SQLExecutor
from dynamiq.connections import PostgreSQL as PostgreSQLConnection

sql_executor = SQLExecutor(
    connection=PostgreSQLConnection(
        host="localhost",
        port=5432,
        database="mydb",
        user="user",
        password="password"
    )
)
```

## Utility Tools

### File Tools
```python
from dynamiq.nodes.tools import FileReadTool, FileWriteTool, FileListTool

read_tool = FileReadTool()
write_tool = FileWriteTool()
list_tool = FileListTool()
```

### Thinking Tool
```python
from dynamiq.nodes.tools import ThinkingTool

thinking = ThinkingTool()
# Helps agents reason through complex problems
```

### Todo Tool
```python
from dynamiq.nodes.tools import TodoWriteTool

todo = TodoWriteTool()
# Track task progress within agents
```

### Human Feedback
```python
from dynamiq.nodes.tools import HumanFeedbackTool

feedback = HumanFeedbackTool()
# Pause for human input during workflow
```

## MCP Integration
```python
from dynamiq.nodes.tools import MCPTool, MCPServer

mcp_tool = MCPTool(
    server=MCPServer(
        command="path/to/mcp-server",
        args=["--port", "8080"]
    )
)
```
