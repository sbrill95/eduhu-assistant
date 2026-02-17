"""API-based evaluators for eduhu-assistant benchmarks."""

import asyncio
import time
from typing import Any, Dict, Optional

import httpx
from pydantic_evals.evaluators import Evaluator, EvaluationResult


class APIGenerateEval(Evaluator):
    """
    Evaluator that calls POST /api/materials/generate and validates the response.
    
    Args:
        base_url: Base URL of the API (default: env var or https://eduhu-assistant.onrender.com)
        teacher_id: Teacher ID for authentication
        expected_status: Expected HTTP status code (default: 200)
        contains_text: Optional text that must be in the response
        timeout: Request timeout in seconds (default: 120)
    """
    
    base_url: str
    teacher_id: str
    expected_status: int = 200
    contains_text: Optional[str] = None
    timeout: int = 120
    
    async def evaluate(self, case: Any) -> EvaluationResult:
        """
        Call the materials generate API and validate response.
        
        Expected case structure:
        {
            "message": "User prompt",
            "material_type": "klausur" | "differenziert" | etc.
        }
        """
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Wait between requests to respect rate limits
                await asyncio.sleep(5)
                
                response = await client.post(
                    f"{self.base_url}/api/materials/generate",
                    json={
                        "teacher_id": self.teacher_id,
                        "message": case.get("message", ""),
                        "material_type": case.get("material_type", "klausur"),
                    },
                )
                
                duration = time.time() - start_time
                
                # Check status code
                if response.status_code != self.expected_status:
                    return EvaluationResult(
                        passed=False,
                        score=0.0,
                        metadata={
                            "status_code": response.status_code,
                            "expected_status": self.expected_status,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                response_data = response.json()
                content = str(response_data.get("content", ""))
                
                # Check for required text
                if self.contains_text and self.contains_text not in content:
                    return EvaluationResult(
                        passed=False,
                        score=0.5,
                        metadata={
                            "status_code": response.status_code,
                            "contains_text": False,
                            "expected_text": self.contains_text,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                return EvaluationResult(
                    passed=True,
                    score=1.0,
                    metadata={
                        "status_code": response.status_code,
                        "duration_ms": int(duration * 1000),
                        "content_length": len(content),
                    }
                )
                
            except Exception as e:
                return EvaluationResult(
                    passed=False,
                    score=0.0,
                    metadata={
                        "error": str(e),
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }
                )


class ChatEval(Evaluator):
    """
    Evaluator that sends a chat message and validates the response.
    
    Args:
        base_url: Base URL of the API
        teacher_id: Teacher ID for authentication
        contains_text: Optional text that must be in the response
        timeout: Request timeout in seconds (default: 120)
        conversation_id: Optional conversation ID for multi-turn tests
    """
    
    base_url: str
    teacher_id: str
    contains_text: Optional[str] = None
    timeout: int = 120
    conversation_id: Optional[str] = None
    
    async def evaluate(self, case: Any) -> EvaluationResult:
        """
        Send chat message and validate response.
        
        Expected case structure:
        {
            "message": "User message",
            "conversation_id": "optional-conv-id"
        }
        """
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Wait between requests
                await asyncio.sleep(5)
                
                payload = {
                    "teacher_id": self.teacher_id,
                    "message": case.get("message", ""),
                }
                
                # Use conversation_id from case or evaluator config
                conv_id = case.get("conversation_id") or self.conversation_id
                if conv_id:
                    payload["conversation_id"] = conv_id
                
                response = await client.post(
                    f"{self.base_url}/api/chat/send",
                    json=payload,
                )
                
                duration = time.time() - start_time
                
                if response.status_code != 200:
                    return EvaluationResult(
                        passed=False,
                        score=0.0,
                        metadata={
                            "status_code": response.status_code,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                response_data = response.json()
                content = str(response_data.get("response", ""))
                
                # Check for required text
                if self.contains_text and self.contains_text not in content:
                    return EvaluationResult(
                        passed=False,
                        score=0.5,
                        metadata={
                            "status_code": response.status_code,
                            "contains_text": False,
                            "expected_text": self.contains_text,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                return EvaluationResult(
                    passed=True,
                    score=1.0,
                    metadata={
                        "status_code": response.status_code,
                        "duration_ms": int(duration * 1000),
                        "content_length": len(content),
                        "conversation_id": response_data.get("conversation_id"),
                    }
                )
                
            except Exception as e:
                return EvaluationResult(
                    passed=False,
                    score=0.0,
                    metadata={
                        "error": str(e),
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }
                )


class DOCXDownloadEval(Evaluator):
    """
    Evaluator that downloads a DOCX file and validates it.
    
    Args:
        base_url: Base URL of the API
        material_id: Material ID to download
        min_size_kb: Minimum expected file size in KB (default: 5)
        timeout: Request timeout in seconds (default: 30)
    """
    
    base_url: str
    material_id: str
    min_size_kb: int = 5
    timeout: int = 30
    
    async def evaluate(self, case: Any) -> EvaluationResult:
        """Download DOCX and validate file."""
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                await asyncio.sleep(5)
                
                response = await client.get(
                    f"{self.base_url}/api/materials/{self.material_id}/docx",
                )
                
                duration = time.time() - start_time
                
                if response.status_code != 200:
                    return EvaluationResult(
                        passed=False,
                        score=0.0,
                        metadata={
                            "status_code": response.status_code,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                content_type = response.headers.get("content-type", "")
                size_kb = len(response.content) / 1024
                
                # Check content type
                is_docx = "openxmlformats" in content_type or "officedocument" in content_type
                
                # Check size
                size_ok = size_kb >= self.min_size_kb
                
                passed = is_docx and size_ok
                
                return EvaluationResult(
                    passed=passed,
                    score=1.0 if passed else 0.0,
                    metadata={
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "size_kb": round(size_kb, 2),
                        "min_size_kb": self.min_size_kb,
                        "duration_ms": int(duration * 1000),
                    }
                )
                
            except Exception as e:
                return EvaluationResult(
                    passed=False,
                    score=0.0,
                    metadata={
                        "error": str(e),
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }
                )


class H5PAccessEval(Evaluator):
    """
    Evaluator that checks if an H5P page is accessible via access code.
    
    Args:
        base_url: Base URL of the API
        access_code: Access code to check
        timeout: Request timeout in seconds (default: 30)
    """
    
    base_url: str
    access_code: str
    timeout: int = 30
    
    async def evaluate(self, case: Any) -> EvaluationResult:
        """Check if H5P page is accessible."""
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                await asyncio.sleep(5)
                
                response = await client.get(
                    f"{self.base_url}/api/public/pages/{self.access_code}",
                )
                
                duration = time.time() - start_time
                
                if response.status_code != 200:
                    return EvaluationResult(
                        passed=False,
                        score=0.0,
                        metadata={
                            "status_code": response.status_code,
                            "duration_ms": int(duration * 1000),
                        }
                    )
                
                return EvaluationResult(
                    passed=True,
                    score=1.0,
                    metadata={
                        "status_code": response.status_code,
                        "duration_ms": int(duration * 1000),
                    }
                )
                
            except Exception as e:
                return EvaluationResult(
                    passed=False,
                    score=0.0,
                    metadata={
                        "error": str(e),
                        "duration_ms": int((time.time() - start_time) * 1000),
                    }
                )
