# GLM OCR MCP Server

MCP server for extracting text from images and PDFs using ZhipuAI GLM-OCR.

## Installation

### Install from source (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/glm-ocr-mcp.git
cd glm-ocr-mcp
uvx --from . glm-ocr-mcp
```

### Run directly

```bash
# Run with uvx (requires setting environment variable)
ZHIPU_API_KEY=your_api_key uvx --from glm-ocr-mcp glm-ocr-mcp
```

## Configuration

Set the environment variable:
```bash
export ZHIPU_API_KEY=your_api_key_here
```

## Usage

### Using with Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "glm-ocr": {
      "command": "uvx",
      "args": ["--from", "glm-ocr-mcp", "glm-ocr-mcp"],
      "env": {
        "ZHIPU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Tools

The server provides `extract_text` tool:

- **file_path**: Path to image or PDF file (absolute or relative to working directory)
- **base64_data**: Base64 encoded file data (optional, either file_path or base64_data required)

### Examples

```python
# Extract text from image
extract_text(file_path="./screenshot.png")

# Extract text from PDF
extract_text(file_path="./document.pdf")

# Use base64 data
extract_text(base64_data="data:image/png;base64,iVBORw0KGgo...")
```

## Development

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Run server for testing
python -m glm_ocr_mcp.server
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
