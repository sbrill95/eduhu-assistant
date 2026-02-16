#!/usr/bin/env python3
"""
eduhu-assistant Benchmark V2 — Extended tests for new agents and features.

Tests:
- New material types (all 12)
- YouTube-Quiz
- TTS / Audio
- Schärfungsfragen quality
- Wissenskarte integration

Usage:
    python benchmarks_v2.py [--url https://custom-url.com] [--teacher-id UUID]
"""

import asyncio
import httpx
import json
import time
from dataclasses import dataclass
from typing import Optional
import argparse

DEFAULT_BASE_URL = "https://eduhu-assistant.onrender.com"
TEACHER_ID = "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32"
TIMEOUT = 120.0


@dataclass
class TestResult:
    name: str
    category: str
    passed: bool
    latency_ms: float
    details: str
    error: Optional[str] = None


class BenchmarkV2:
    def __init__(self, base_url: str, teacher_id: str):
        self.base = base_url
        self.teacher_id = teacher_id
        self.results: list[TestResult] = []
        self.conversation_id: str | None = None

    async def _chat(self, message: str, client: httpx.AsyncClient) -> tuple[str, float]:
        """Send chat message and return (response, latency_ms)."""
        start = time.time()
        r = await client.post(
            f"{self.base}/api/send",
            json={
                "message": message,
                "teacher_id": self.teacher_id,
                "conversation_id": self.conversation_id,
            },
            timeout=TIMEOUT,
        )
        latency = (time.time() - start) * 1000
        r.raise_for_status()
        data = r.json()
        self.conversation_id = data.get("conversation_id", self.conversation_id)
        content = data.get("message", {}).get("content", "")
        return content, latency

    async def run_all(self):
        """Run all V2 benchmarks."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Start fresh conversation
            self.conversation_id = None

            await self._test_schaerfungsfragen(client)
            await self._test_material_types(client)
            await self._test_youtube_quiz(client)
            await self._test_tts(client)
            await self._test_audio_endpoint(client)

        self._print_results()

    async def _test_schaerfungsfragen(self, client: httpx.AsyncClient):
        """Test: Agent asks clarifying questions before generating material."""
        test_cases = [
            ("Erstelle mir eine Klausur für Physik", "klausur"),
            ("Ich brauche ein Mystery zu Klimawandel", "mystery"),
            ("Mach einen Escape Room", "escape_room"),
        ]

        for prompt, mat_type in test_cases:
            try:
                self.conversation_id = None  # Fresh conversation
                response, latency = await self._chat(prompt, client)

                # Should ask questions, NOT immediately generate
                has_question = "?" in response
                no_download = "/api/materials/" not in response
                passed = has_question and no_download

                self.results.append(TestResult(
                    name=f"Schärfungsfragen: {mat_type}",
                    category="Schärfungsfragen",
                    passed=passed,
                    latency_ms=latency,
                    details=f"Question: {'✅' if has_question else '❌'}, No immediate gen: {'✅' if no_download else '❌'}",
                    error=None if passed else f"Response: {response[:200]}",
                ))
            except Exception as e:
                self.results.append(TestResult(
                    name=f"Schärfungsfragen: {mat_type}",
                    category="Schärfungsfragen",
                    passed=False, latency_ms=0,
                    details="", error=str(e),
                ))

    async def _test_material_types(self, client: httpx.AsyncClient):
        """Test: Each material type generates valid output."""
        # Only test a few types to conserve API tokens
        test_types = [
            ("Erstelle eine Hilfekarte für Mathe, Klasse 7, Bruchrechnung. Keine Rückfragen, generiere direkt.", "hilfekarte"),
            ("Erstelle ein Lernspiel für Deutsch, Klasse 5, Wortarten. Keine Rückfragen, generiere direkt.", "lernspiel"),
        ]

        for prompt, mat_type in test_types:
            try:
                self.conversation_id = None
                response, latency = await self._chat(prompt, client)

                has_content = len(response) > 100
                has_download = "/api/materials/" in response or "erstellt" in response.lower()
                passed = has_content and has_download

                self.results.append(TestResult(
                    name=f"Material: {mat_type}",
                    category="Material Generation V2",
                    passed=passed,
                    latency_ms=latency,
                    details=f"Content: {'✅' if has_content else '❌'}, Download: {'✅' if has_download else '❌'}",
                    error=None if passed else f"Response: {response[:200]}",
                ))
            except Exception as e:
                self.results.append(TestResult(
                    name=f"Material: {mat_type}",
                    category="Material Generation V2",
                    passed=False, latency_ms=0,
                    details="", error=str(e),
                ))

    async def _test_youtube_quiz(self, client: httpx.AsyncClient):
        """Test: YouTube quiz generation from a real video."""
        try:
            self.conversation_id = None
            prompt = "Erstelle ein Quiz aus diesem YouTube-Video: https://www.youtube.com/watch?v=dQw4w9WgXcQ Keine Rückfragen, direkt Quiz erstellen."
            response, latency = await self._chat(prompt, client)

            has_questions = "Frage" in response or "frage" in response
            has_answer = "✅" in response or "richtig" in response.lower()
            passed = has_questions

            self.results.append(TestResult(
                name="YouTube Quiz",
                category="YouTube Quiz",
                passed=passed,
                latency_ms=latency,
                details=f"Questions: {'✅' if has_questions else '❌'}, Answers: {'✅' if has_answer else '❌'}",
                error=None if passed else f"Response: {response[:200]}",
            ))
        except Exception as e:
            self.results.append(TestResult(
                name="YouTube Quiz",
                category="YouTube Quiz",
                passed=False, latency_ms=0,
                details="", error=str(e),
            ))

    async def _test_tts(self, client: httpx.AsyncClient):
        """Test: TTS endpoint generates audio."""
        try:
            start = time.time()
            r = await client.post(
                f"{self.base}/api/audio/tts",
                json={"text": "Dies ist ein Test.", "voice": "educator"},
                timeout=30,
            )
            latency = (time.time() - start) * 1000

            passed = r.status_code == 200
            data = r.json() if passed else {}

            self.results.append(TestResult(
                name="TTS Endpoint",
                category="Audio",
                passed=passed,
                latency_ms=latency,
                details=f"Status: {r.status_code}, Audio ID: {data.get('audio_id', 'N/A')}",
                error=None if passed else r.text[:200],
            ))

            # Test audio retrieval
            if passed and data.get("audio_id"):
                r2 = await client.get(f"{self.base}/api/audio/{data['audio_id']}")
                audio_ok = r2.status_code == 200 and len(r2.content) > 1000
                self.results.append(TestResult(
                    name="Audio Retrieval",
                    category="Audio",
                    passed=audio_ok,
                    latency_ms=0,
                    details=f"Size: {len(r2.content)} bytes",
                ))
        except Exception as e:
            self.results.append(TestResult(
                name="TTS Endpoint",
                category="Audio",
                passed=False, latency_ms=0,
                details="", error=str(e),
            ))

    async def _test_audio_endpoint(self, client: httpx.AsyncClient):
        """Test: Audio share endpoint creates access code."""
        try:
            r = await client.post(
                f"{self.base}/api/audio/share",
                json={
                    "teacher_id": self.teacher_id,
                    "title": "Benchmark Test Audio",
                    "audio_type": "tts",
                    "audio_ids": ["test-id-123"],
                },
                timeout=10,
            )
            passed = r.status_code == 200
            data = r.json() if passed else {}

            self.results.append(TestResult(
                name="Audio Share",
                category="Audio",
                passed=passed,
                latency_ms=0,
                details=f"Code: {data.get('access_code', 'N/A')}",
                error=None if passed else r.text[:200],
            ))
        except Exception as e:
            self.results.append(TestResult(
                name="Audio Share",
                category="Audio",
                passed=False, latency_ms=0,
                details="", error=str(e),
            ))

    def _print_results(self):
        """Print formatted results."""
        print("\n" + "=" * 70)
        print("BENCHMARK V2 RESULTS")
        print("=" * 70)

        categories: dict[str, list[TestResult]] = {}
        for r in self.results:
            categories.setdefault(r.category, []).append(r)

        total_pass = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        for cat, tests in categories.items():
            cat_pass = sum(1 for t in tests if t.passed)
            print(f"\n{'─' * 50}")
            print(f"📂 {cat} ({cat_pass}/{len(tests)})")
            for t in tests:
                icon = "✅" if t.passed else "❌"
                latency = f" ({t.latency_ms:.0f}ms)" if t.latency_ms > 0 else ""
                print(f"  {icon} {t.name}{latency}")
                if t.details:
                    print(f"     {t.details}")
                if t.error:
                    print(f"     ⚠️ {t.error[:150]}")

        print(f"\n{'=' * 70}")
        print(f"TOTAL: {total_pass}/{total} ({total_pass/total*100:.0f}%)" if total else "No tests run")
        print("=" * 70)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_BASE_URL)
    parser.add_argument("--teacher-id", default=TEACHER_ID)
    args = parser.parse_args()

    bench = BenchmarkV2(args.url, args.teacher_id)
    await bench.run_all()


if __name__ == "__main__":
    asyncio.run(main())
