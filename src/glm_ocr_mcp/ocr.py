"""GLM OCR MCP Server"""

import base64
import mimetypes
import os
import time
from typing import Union

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_URL = "https://open.bigmodel.cn/api/paas/v4/layout_parsing"
API_URL = os.getenv("ZHIPU_OCR_API_URL", DEFAULT_API_URL)


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

    def _file_to_data_url(self, file_path: str) -> str:
        """Convert local file path to data URL with detected MIME type."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        return f"data:{mime_type};base64,{self._encode_file(file_path)}"

    def _extract_markdown(self, result: dict) -> str:
        """Normalize API response shape to markdown string."""
        md_results = result.get("md_results", "")
        if isinstance(md_results, str):
            return md_results
        if isinstance(md_results, list):
            parts = []
            for item in md_results:
                if isinstance(item, dict):
                    if "content" in item and isinstance(item["content"], str):
                        parts.append(item["content"])
                    elif "md" in item and isinstance(item["md"], str):
                        parts.append(item["md"])
            return "\n\n".join(part for part in parts if part)
        return ""

    def _build_payload(
        self,
        file: Union[str, bytes],
        start_page_id: int | None = None,
        end_page_id: int | None = None,
    ) -> dict:
        """Build request payload and include PDF paging options when applicable."""
        is_pdf = False
        if isinstance(file, bytes):
            file_data = (
                "data:application/octet-stream;base64,"
                f"{base64.b64encode(file).decode('utf-8')}"
            )
        elif str(file).startswith("http://") or str(file).startswith("https://"):
            file_data = file
            is_pdf = str(file).lower().split("?", 1)[0].endswith(".pdf")
        elif str(file).startswith("data:image") or str(file).startswith("data:application"):
            file_data = str(file)
            is_pdf = str(file).lower().startswith("data:application/pdf")
        elif os.path.isfile(str(file)):
            file_data = self._file_to_data_url(str(file))
            is_pdf = str(file).lower().endswith(".pdf")
        else:
            raise ValueError(f"Unsupported file format or path does not exist: {file}")

        payload = {
            "model": "glm-ocr",
            "return_crop_images": True,
            "file": file_data,
        }
        if is_pdf:
            if start_page_id is not None:
                payload["start_page_id"] = start_page_id
            if end_page_id is not None:
                payload["end_page_id"] = end_page_id
        return payload

    def _post_layout_parsing(self, payload: dict, retries: int = 3) -> dict:
        """Call layout parsing API with retry for transient server/network failures."""
        last_exc: Exception | None = None
        with httpx.Client(timeout=120) as client:
            for attempt in range(retries):
                try:
                    response = client.post(
                        API_URL,
                        headers=self.headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as exc:
                    # Do not retry client-side invalid requests.
                    if exc.response.status_code < 500:
                        raise
                    last_exc = exc
                except httpx.HTTPError as exc:
                    last_exc = exc
                if attempt < retries - 1:
                    time.sleep(0.6 * (attempt + 1))
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Unexpected empty response from OCR API")

    def parse(
        self,
        file: Union[str, bytes],
        start_page_id: int | None = None,
        end_page_id: int | None = None,
    ) -> str:
        """
        Call layout parsing API, return markdown content

        Args:
            file: File path, base64 data, or URL

        Returns:
            Parsed markdown content
        """
        payload = self._build_payload(
            file,
            start_page_id=start_page_id,
            end_page_id=end_page_id,
        )
        result = self._post_layout_parsing(payload)

        return self._extract_markdown(result)

    def parse_json(
        self,
        file: Union[str, bytes],
        start_page_id: int | None = None,
        end_page_id: int | None = None,
    ) -> dict:
        """
        Call layout parsing API and return structured JSON response.

        `md_results` is removed because markdown is provided by `parse`.
        """
        payload = self._build_payload(
            file,
            start_page_id=start_page_id,
            end_page_id=end_page_id,
        )
        result = self._post_layout_parsing(payload)
        result.pop("md_results", None)
        return result


def get_ocr_client() -> ZhipuOCR:
    """Get OCR client instance"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError("Please set ZHIPU_API_KEY environment variable")
    return ZhipuOCR(api_key)
