"""GLM OCR MCP Server - Model Context Protocol server for OCR text extraction."""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

from .ocr import get_ocr_client


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("glm-ocr-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        shared_schema = {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Local file path or URL for PNG, JPG/JPEG, or PDF. Examples: ./test.png, C:/docs/a.pdf, https://example.com/a.jpg"
                },
                "base64_data": {
                    "type": "string",
                    "description": "Optional data URL or base64 payload. Use when file_path is unavailable."
                },
                "start_page_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional PDF start page (1-based). Ignored for PNG/JPG inputs."
                },
                "end_page_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional PDF end page (1-based). Ignored for PNG/JPG inputs."
                },
                "return_json": {
                    "type": "boolean",
                    "default": False,
                    "description": "Optional, default false. Use only when structured layout details are needed (bbox_2d/content/label etc.), because JSON output is much longer."
                }
            },
            "anyOf": [
                {"required": ["file_path"]},
                {"required": ["base64_data"]},
            ],
            "additionalProperties": False,
        }
        return [
            Tool(
                name="extract_text",
                description="Extract text from local files or URLs. Supported formats: PNG, JPG/JPEG, PDF.",
                inputSchema=shared_schema
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name != "extract_text":
            raise ValueError(f"Unknown tool: {name}")

        arguments = arguments or {}
        file_path = arguments.get("file_path")
        base64_data = arguments.get("base64_data")
        start_page_id = arguments.get("start_page_id")
        end_page_id = arguments.get("end_page_id")
        return_json = bool(arguments.get("return_json", False))

        if (
            start_page_id is not None
            and end_page_id is not None
            and start_page_id > end_page_id
        ):
            return [
                TextContent(
                    type="text",
                    text="Error: start_page_id must be less than or equal to end_page_id",
                )
            ]

        # Get OCR client
        ocr = get_ocr_client()

        try:
            if base64_data:
                # Handle base64 data
                if "," in base64_data:
                    # May be data URL format
                    data_input = base64_data
                else:
                    data_input = f"data:application/octet-stream;base64,{base64_data}"
            else:
                # Handle file path
                data_input = file_path

            if return_json:
                json_result = ocr.parse_json(
                    data_input,
                    start_page_id=start_page_id,
                    end_page_id=end_page_id,
                )
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(json_result, ensure_ascii=False),
                    )
                ]

            md_content = ocr.parse(
                data_input,
                start_page_id=start_page_id,
                end_page_id=end_page_id,
            )
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
