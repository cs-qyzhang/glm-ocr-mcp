"""GLM OCR MCP Server"""

import base64
import os
from typing import Union

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://open.bigmodel.cn/api/paas/v4/layout_parsing"


class ZhipuOCR:
    """ZhipuAI OCR Client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _encode_file(self, file_path: str) -> str:
        """Encode file to base64"""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def parse(self, file: Union[str, bytes]) -> str:
        """
        Call layout parsing API, return markdown content

        Args:
            file: File path, base64 data, or URL

        Returns:
            Parsed markdown content
        """
        # Determine input type
        if isinstance(file, bytes):
            # Raw bytes data, convert to base64 data URL
            file_data = f"data:application/octet-stream;base64,{base64.b64encode(file).decode('utf-8')}"
        elif str(file).startswith("http://") or str(file).startswith("https://"):
            file_data = file
        elif str(file).startswith("data:image") or str(file).startswith("data:application"):
            file_data = str(file)
        elif os.path.isfile(str(file)):
            # Local file to base64
            file_data = f"data:application/octet-stream;base64,{self._encode_file(str(file))}"
        else:
            raise ValueError(f"Unsupported file format or path does not exist: {file}")

        payload = {
            "model": "glm-ocr",
            "return_crop_images": True,
            "file": file_data
        }

        with httpx.Client(timeout=120) as client:
            response = client.post(
                API_URL,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        return result.get("md_results", "")


def get_ocr_client() -> ZhipuOCR:
    """Get OCR client instance"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("Please set ZHIPU_API_KEY environment variable")
    return ZhipuOCR(api_key)
