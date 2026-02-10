# GLM OCR MCP Server

MCP server for extracting text from images and PDFs using ZhipuAI GLM-OCR.

## Usage

```json
{
  "mcpServers": {
    "glm-ocr": {
      "command": "uvx",
      "args": ["glm-ocr-mcp"],
      "env": {
        "ZHIPU_API_KEY": "your_api_key_here",
        "ZHIPU_OCR_API_URL": "https://open.bigmodel.cn/api/paas/v4/layout_parsing"
      }
    }
  }
}
```

### Using with Claude Code

```bash
claude mcp add --scope user glm-ocr \
  --env ZHIPU_API_KEY=your_api_key_here \
  --env ZHIPU_OCR_API_URL=https://open.bigmodel.cn/api/paas/v4/layout_parsing \
  -- uvx glm-ocr-mcp
```

### Using with Codex

Add MCP server with command:

```bash
codex mcp add glm-ocr \
  --env ZHIPU_API_KEY=your_api_key_here \
  --env ZHIPU_OCR_API_URL=https://open.bigmodel.cn/api/paas/v4/layout_parsing \
  -- uvx glm-ocr-mcp
```

### Tools

The server provides one tool:

- **extract_text**: Extract from local file or URL (`png`, `jpg/jpeg`, `pdf`)
  - default returns Markdown text
  - set `return_json=true` to return structured JSON without `md_results` (contains page parsing details like `bbox_2d`, `content`, `label`, etc.)

Parameters:

- **file_path**: Local file path or URL for `png`, `jpg/jpeg`, or `pdf`
- **base64_data**: Optional data URL/base64 payload (use when `file_path` is unavailable)
- **start_page_id**: Optional PDF start page (1-based, only effective for PDF)
- **end_page_id**: Optional PDF end page (1-based, only effective for PDF)
- **return_json**: Optional boolean, default `false`. `true` returns JSON; `false` returns Markdown.

### Examples

```python
# Extract text from local image
extract_text(file_path="./screenshot.png")

# Extract text from local PDF
extract_text(file_path="./document.pdf")

# Extract text from URL image
extract_text(file_path="https://example.com/test.jpg")

# Use base64/data URL
extract_text(base64_data="data:image/png;base64,iVBORw0KGgo...")

# Extract structured layout JSON
extract_text(file_path="https://example.com/test.png", return_json=True)
```

## Development

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Sync dependencies and install current project
uv sync

# Run server for testing
python -m glm_ocr_mcp.server
```

Windows PowerShell activation:
```powershell
.venv\Scripts\Activate.ps1
```

## Project Structure

```
glm-ocr-mcp/
├── pyproject.toml         # Project configuration
├── README.md              # Documentation
├── .env.example           # Environment variable template
├── src/
│   └── glm_ocr_mcp/
│       ├── __init__.py
│       ├── __main__.py    # Entry point
│       ├── ocr.py         # OCR client
│       └── server.py      # MCP server
```
