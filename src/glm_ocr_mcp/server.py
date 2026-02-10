"""GLM OCR MCP Server - Model Context Protocol server for OCR text extraction."""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

from .ocr import get_ocr_client


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("glm-ocr-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="extract_text",
                description="Extract text content from images or PDF files, return Markdown format. Supports JPEG, PNG, PDF and other formats. Accepts file path or base64 encoded data.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to image or PDF file (e.g., /path/to/image.png or ./document.pdf)"
                        },
                        "base64_data": {
                            "type": "string",
                            "description": "Base64 encoded file data (optional, either file_path or base64_data required)"
                        }
                    },
                    "oneOf": ["file_path", "base64_data"],
                    "required": ["file_path"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name != "extract_text":
            raise ValueError(f"Unknown tool: {name}")

        file_path = arguments.get("file_path")
        base64_data = arguments.get("base64_data")

        # Get OCR client
        ocr = get_ocr_client()

        try:
            if base64_data:
                # Handle base64 data
                if "," in base64_data:
                    # May be data URL format
                    base64_data = base64_data.split(",", 1)[1]
                md_content = ocr.parse(base64_data.encode("utf-8"))
            else:
                # Handle file path
                md_content = ocr.parse(file_path)

            return [TextContent(type="text", text=md_content)]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"Error: File not found: {file_path}")]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"OCR parsing error: {str(e)}")]

    return server


async def run_async():
    """Run the MCP server using stdio transport asynchronously."""
    from mcp.server.stdio import stdio_server

    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


# Convenience function for running the server with stdio transport
def run():
    """Run the MCP server using stdio transport."""
    asyncio.run(run_async())


if __name__ == "__main__":
    run()
