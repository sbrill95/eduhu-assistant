#!/usr/bin/env python3
"""
eduhu-assistant Benchmark Suite
================================
Automatisierte Tests für Chat-Qualität, Memory, RAG, Research und API-Zuverlässigkeit.

Usage:
    python benchmarks.py [--url https://custom-url.com] [--password YOUR_PASSWORD]
"""

import asyncio
import httpx
import json
import re
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_BASE_URL = "https://eduhu-assistant.onrender.com"
TEACHER_ID = "a4d218bd-4ac8-4ce3-8d41-c85db8be6e32"
TEACHER_USERNAME = "krake26"
DEFAULT_PASSWORD = "your_password_here"  # Override via --password

TIMEOUT = 60.0  # seconds for API calls


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class BenchmarkResult:
    """Single benchmark test result"""
    name: str
    category: str
    input_data: str
    expected_pattern: str
    actual_output: str
    passed: bool
    latency_ms: float
    error: Optional[str] = None


@dataclass
class CategoryScore:
    """Score summary for a benchmark category"""
    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    avg_latency_ms: float
    pass_rate: float


# ============================================================================
# Test Client
# ============================================================================

class EduHuBenchmark:
    def __init__(self, base_url: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.password = password
        self.teacher_id = TEACHER_ID
        self.username = TEACHER_USERNAME
        self.session_token: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.results: List[BenchmarkResult] = []
        
    async def login(self) -> bool:
        """Authenticate and get teacher_id"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json={"password": self.password}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.teacher_id = data.get("teacher_id", self.teacher_id)
                    name = data.get("name", "?")
                    print(f"✅ Login successful ({name}, {self.teacher_id})")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False
    
    def headers(self) -> Dict[str, str]:
        """Get auth headers"""
        if self.session_token:
            return {"Authorization": f"Bearer {self.session_token}"}
        return {}
    
    async def send_message(self, message: str) -> tuple[Optional[str], float]:
        """Send chat message and return (response, latency_ms)"""
        start = time.time()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                payload = {
                    "message": message,
                    "teacher_id": self.teacher_id
                }
                if self.conversation_id:
                    payload["conversation_id"] = self.conversation_id
                
                response = await client.post(
                    f"{self.base_url}/api/chat/send",
                    json=payload,
                    headers=self.headers()
                )
                latency = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.conversation_id = data.get("conversation_id")
                    # API returns {conversation_id, message: {content, ...}}
                    msg = data.get("message", {})
                    content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                    return content, latency
                else:
                    return None, latency
            except Exception as e:
                latency = (time.time() - start) * 1000
                print(f"⚠️  Message error: {e}")
                return None, latency
    
    async def get_conversation_history(self) -> tuple[Optional[List], float]:
        """Get conversation history"""
        start = time.time()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/chat/history",
                    params={"conversation_id": self.conversation_id},
                    headers=self.headers()
                )
                latency = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("messages", []), latency
                return None, latency
            except Exception as e:
                latency = (time.time() - start) * 1000
                return None, latency
    
    async def get_profile(self) -> tuple[Optional[Dict], float]:
        """Get teacher profile"""
        start = time.time()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/profile/{self.teacher_id}",
                    headers=self.headers()
                )
                latency = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    return response.json(), latency
                return None, latency
            except Exception as e:
                latency = (time.time() - start) * 1000
                return None, latency
    
    def add_result(self, category: str, name: str, input_data: str, 
                   expected_pattern: str, actual: str, latency: float, error: Optional[str] = None):
        """Add benchmark result"""
        passed = bool(re.search(expected_pattern, actual, re.IGNORECASE | re.DOTALL)) if actual else False
        
        result = BenchmarkResult(
            name=name,
            category=category,
            input_data=input_data[:200],  # Truncate for readability
            expected_pattern=expected_pattern,
            actual_output=actual[:500] if actual else "None",  # Truncate
            passed=passed,
            latency_ms=round(latency, 2),
            error=error
        )
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} [{category}] {name} ({latency:.0f}ms)")
    
    # ========================================================================
    # Benchmark Categories
    # ========================================================================
    
    async def benchmark_chat_quality(self):
        """Category 1: Chat Quality Tests"""
        print("\n" + "="*60)
        print("📝 CATEGORY 1: CHAT QUALITY")
        print("="*60)
        
        tests = [
            {
                "name": "Unterrichtsplanung Elektrizität",
                "message": "Erstelle eine Doppelstunde zum Thema Elektrizität für Klasse 9",
                "expected": r"(stromkreis|spannung|widerstand|90\s*min|doppelstunde|einführung|experiment)",
            },
            {
                "name": "Quiz Lichtbrechung",
                "message": "Erstelle ein Quiz mit 5 Fragen zur Lichtbrechung",
                "expected": r"(frage.*1|frage.*2|frage.*3|brechung|einfallswinkel|snellius)",
            },
            {
                "name": "Differenzierung Photosynthese",
                "message": "Erkläre Photosynthese für Klasse 5 und für Klasse 10",
                "expected": r"(klasse\s*5|klasse\s*10|einfacher|komplex|chlorophyll|glucose|atp)",
            },
            {
                "name": "Elternbrief Wandertag",
                "message": "Schreibe einen Elternbrief für den Wandertag am 15. März",
                "expected": r"(liebe\s+eltern|wandertag|15\.?\s*märz|uhrzeit|treffpunkt|unterschrift)",
            },
        ]
        
        for test in tests:
            response, latency = await self.send_message(test["message"])
            self.add_result(
                category="Chat Quality",
                name=test["name"],
                input_data=test["message"],
                expected_pattern=test["expected"],
                actual=response or "",
                latency=latency
            )
            await asyncio.sleep(1)  # Rate limiting
    
    async def benchmark_memory_agent(self):
        """Category 2: Memory Agent Tests"""
        print("\n" + "="*60)
        print("🧠 CATEGORY 2: MEMORY AGENT")
        print("="*60)
        
        # Reset conversation for clean memory test
        self.conversation_id = None
        
        # Test 1: Implicit memory extraction
        msg1 = "Ich unterrichte Mathe und Bio in Klasse 7"
        response1, latency1 = await self.send_message(msg1)
        self.add_result(
            category="Memory Agent",
            name="Implicit Memory Extraction",
            input_data=msg1,
            expected_pattern=r"(mathe|bio|klasse\s*7|fächer|verstanden|gespeichert)",
            actual=response1 or "",
            latency=latency1
        )
        await asyncio.sleep(2)
        
        # Test 2: Explicit memory request
        msg2 = "Merk dir: Klasse 8a hat Schwierigkeiten mit Bruchrechnung"
        response2, latency2 = await self.send_message(msg2)
        self.add_result(
            category="Memory Agent",
            name="Explicit Memory Storage",
            input_data=msg2,
            expected_pattern=r"(gemerkt|gespeichert|notiert|bruchrechnung|8a)",
            actual=response2 or "",
            latency=latency2
        )
        await asyncio.sleep(2)
        
        # Test 3: Memory retrieval in next message
        msg3 = "Welche Themen sollte ich mit meinen Klassen wiederholen?"
        response3, latency3 = await self.send_message(msg3)
        self.add_result(
            category="Memory Agent",
            name="Memory Retrieval",
            input_data=msg3,
            expected_pattern=r"(bruchrechnung|8a|mathe|bio|klasse\s*7)",
            actual=response3 or "",
            latency=latency3
        )
    
    async def benchmark_curriculum_rag(self):
        """Category 3: Curriculum RAG Tests"""
        print("\n" + "="*60)
        print("📚 CATEGORY 3: CURRICULUM RAG")
        print("="*60)
        
        # Reset conversation
        self.conversation_id = None
        
        tests = [
            {
                "name": "Lehrplan Optik Klasse 8",
                "message": "Was steht im Lehrplan zu Optik Klasse 8?",
                "expected": r"(lichtbrechung|reflexion|linsen|schatten|lehrplan|kompetenz|sachsen)",
            },
            {
                "name": "Kompetenzen Elektrizitätslehre",
                "message": "Welche Kompetenzen für Elektrizitätslehre?",
                "expected": r"(stromkreis|spannung|widerstand|kompetenz|schüler|erkennen|beschreiben)",
            },
            {
                "name": "Semantische Suche Halbleiter",
                "message": "Wie unterrichte ich Halbleiter?",
                "expected": r"(halbleiter|klasse\s*9|physik|dotierung|diode|lehrplan|kompetenz)",
            },
        ]
        
        for test in tests:
            response, latency = await self.send_message(test["message"])
            self.add_result(
                category="Curriculum RAG",
                name=test["name"],
                input_data=test["message"],
                expected_pattern=test["expected"],
                actual=response or "",
                latency=latency
            )
            await asyncio.sleep(1)
    
    async def benchmark_research_agent(self):
        """Category 4: Research Agent Tests"""
        print("\n" + "="*60)
        print("🔍 CATEGORY 4: RESEARCH AGENT")
        print("="*60)
        
        self.conversation_id = None
        
        msg = "Aktuelle Methoden für Physikunterricht"
        response, latency = await self.send_message(msg)
        
        # Check for URLs or source references
        has_urls = bool(re.search(r"(https?://|www\.|quelle|referenz|link|\[.*\]\(http)", response or "", re.IGNORECASE))
        
        self.add_result(
            category="Research Agent",
            name="Web Search for Teaching Methods",
            input_data=msg,
            expected_pattern=r"(https?://|www\.|quelle|referenz|link|methode|experiment)",
            actual=response or "",
            latency=latency
        )
    
    async def benchmark_summary_agent(self):
        """Category 5: Summary Agent Tests"""
        print("\n" + "="*60)
        print("📋 CATEGORY 5: SUMMARY AGENT")
        print("="*60)
        
        self.conversation_id = None
        
        # Send 12+ messages to trigger summary
        messages = [
            "Hallo, wie geht es dir?",
            "Ich plane eine Unterrichtsstunde.",
            "Das Thema ist Mechanik.",
            "Klasse 10, Gymnasium.",
            "Was sind gute Experimente?",
            "Wie lange sollte die Einführung sein?",
            "Gibt es Videos dazu?",
            "Welche Hausaufgaben passen?",
            "Wie bewerte ich das?",
            "Was kommt in der Klausur dran?",
            "Hast du Beispielaufgaben?",
            "Danke für die Hilfe!",
            "Kannst du die wichtigsten Punkte zusammenfassen?",
        ]
        
        print(f"   Sending {len(messages)} messages...")
        last_response = ""
        total_latency = 0
        
        for i, msg in enumerate(messages, 1):
            response, latency = await self.send_message(msg)
            total_latency += latency
            if response:
                last_response = response
            print(f"   Message {i}/{len(messages)} sent")
            await asyncio.sleep(0.5)
        
        # Check if summary exists in response or history
        history, hist_latency = await self.get_conversation_history()
        total_latency += hist_latency
        
        has_summary = bool(re.search(r"(zusammenfassung|überblick|hauptpunkte|mechanik.*klasse.*10)", 
                                     last_response or "", re.IGNORECASE))
        
        self.add_result(
            category="Summary Agent",
            name="Long Conversation Summary",
            input_data=f"Sent {len(messages)} messages",
            expected_pattern=r"(zusammenfassung|überblick|mechanik|klasse.*10|experimente)",
            actual=last_response,
            latency=total_latency / len(messages)
        )
    
    async def benchmark_system_prompt(self):
        """Category 6: System Prompt & Context Tests"""
        print("\n" + "="*60)
        print("⚙️  CATEGORY 6: SYSTEM PROMPT & CONTEXT")
        print("="*60)
        
        # Test 1: Profile context in response
        profile, prof_latency = await self.get_profile()
        
        if profile:
            bundesland = profile.get("bundesland", "unknown")
            faecher = profile.get("subjects", [])
            
            self.conversation_id = None
            msg = "Was kannst du mir über meinen Lehrplan sagen?"
            response, latency = await self.send_message(msg)
            
            # Check if profile data appears in context
            pattern = f"({bundesland}|{'|'.join(faecher[:3]) if faecher else 'physik|mathe'})"
            
            self.add_result(
                category="System Prompt",
                name="Profile Context in Response",
                input_data=msg,
                expected_pattern=pattern,
                actual=response or "",
                latency=latency
            )
        
        # Test 2: Memory context usage (reuse memory test conversation)
        # Already tested in memory_agent section
        print("   (Memory context usage tested in Memory Agent section)")
    
    async def benchmark_api_reliability(self):
        """Category 7: API Reliability & Error Handling"""
        print("\n" + "="*60)
        print("🔧 CATEGORY 7: API RELIABILITY")
        print("="*60)
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test 1: Login endpoint
            start = time.time()
            try:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json={"password": self.password}
                )
                latency = (time.time() - start) * 1000
                passed = response.status_code == 200 and response.headers.get("content-type", "").startswith("application/json")
                self.add_result(
                    category="API Reliability",
                    name="Login Endpoint",
                    input_data=f"POST /api/auth/login",
                    expected_pattern="200",
                    actual=f"Status {response.status_code}",
                    latency=latency
                )
            except Exception as e:
                self.add_result(
                    category="API Reliability",
                    name="Login Endpoint",
                    input_data=f"POST /api/auth/login",
                    expected_pattern="200",
                    actual=f"Error: {e}",
                    latency=0,
                    error=str(e)
                )
            
            # Test 2: Invalid credentials
            start = time.time()
            try:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json={"password": "wrong_password_123"}
                )
                latency = (time.time() - start) * 1000
                passed = response.status_code in [401, 403]
                self.add_result(
                    category="API Reliability",
                    name="Invalid Credentials Handling",
                    input_data=f"POST /api/auth/login (invalid creds)",
                    expected_pattern="401|403",
                    actual=f"Status {response.status_code}",
                    latency=latency
                )
            except Exception as e:
                pass
            
            # Test 3: Empty message handling
            start = time.time()
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat/send",
                    json={"message": "", "teacher_id": self.teacher_id},
                    headers=self.headers()
                )
                latency = (time.time() - start) * 1000
                # Should either reject (400) or handle gracefully (200)
                passed = response.status_code in [200, 400, 422]
                self.add_result(
                    category="API Reliability",
                    name="Empty Message Handling",
                    input_data="POST /api/chat/send (empty message)",
                    expected_pattern="200|400|422",
                    actual=f"Status {response.status_code}",
                    latency=latency
                )
            except Exception as e:
                pass
            
            # Test 4: Missing teacher_id
            start = time.time()
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat/send",
                    json={"message": "Hello"},
                    headers=self.headers()
                )
                latency = (time.time() - start) * 1000
                passed = response.status_code in [400, 422]
                self.add_result(
                    category="API Reliability",
                    name="Missing teacher_id Handling",
                    input_data="POST /api/chat/send (no teacher_id)",
                    expected_pattern="400|422",
                    actual=f"Status {response.status_code}",
                    latency=latency
                )
            except Exception as e:
                pass
            
            # Test 5: Conversation history endpoint
            if self.conversation_id:
                history, hist_latency = await self.get_conversation_history()
                passed = history is not None
                self.add_result(
                    category="API Reliability",
                    name="Conversation History Endpoint",
                    input_data=f"GET /api/chat/history",
                    expected_pattern="200",
                    actual=f"Returned {len(history) if history else 0} messages",
                    latency=hist_latency
                )
    
    # ========================================================================
    # Reporting
    # ========================================================================
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        categories = {}
        
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        category_scores = []
        for cat_name, cat_results in categories.items():
            total = len(cat_results)
            passed = sum(1 for r in cat_results if r.passed)
            failed = total - passed
            avg_latency = sum(r.latency_ms for r in cat_results) / total if total > 0 else 0
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            category_scores.append(CategoryScore(
                category=cat_name,
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                avg_latency_ms=round(avg_latency, 2),
                pass_rate=round(pass_rate, 2)
            ))
        
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r.passed)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": self.base_url,
            "teacher_id": self.teacher_id,
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_tests - total_passed,
                "overall_pass_rate": round(overall_pass_rate, 2)
            },
            "categories": [asdict(cs) for cs in category_scores],
            "detailed_results": [asdict(r) for r in self.results]
        }
        
        return report
    
    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 BENCHMARK SUMMARY")
        print("="*60)
        
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        for cat_name, cat_results in categories.items():
            total = len(cat_results)
            passed = sum(1 for r in cat_results if r.passed)
            pass_rate = (passed / total * 100) if total > 0 else 0
            avg_latency = sum(r.latency_ms for r in cat_results) / total if total > 0 else 0
            
            status_icon = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 50 else "❌"
            print(f"\n{status_icon} {cat_name}")
            print(f"   Tests: {passed}/{total} passed ({pass_rate:.1f}%)")
            print(f"   Avg Latency: {avg_latency:.0f}ms")
        
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r.passed)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "-"*60)
        print(f"OVERALL: {total_passed}/{total_tests} tests passed ({overall_pass_rate:.1f}%)")
        print("="*60)


# ============================================================================
# Main Execution
# ============================================================================

async def run_benchmarks(base_url: str, password: str):
    """Run all benchmark suites"""
    print("="*60)
    print("🎯 eduhu-assistant BENCHMARK SUITE")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Teacher: {TEACHER_USERNAME} ({TEACHER_ID})")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    benchmark = EduHuBenchmark(base_url, password)
    
    # Login
    if not await benchmark.login():
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Run all benchmark categories
    await benchmark.benchmark_chat_quality()
    await benchmark.benchmark_memory_agent()
    await benchmark.benchmark_curriculum_rag()
    await benchmark.benchmark_research_agent()
    await benchmark.benchmark_summary_agent()
    await benchmark.benchmark_system_prompt()
    await benchmark.benchmark_api_reliability()
    
    # Generate report
    benchmark.print_summary()
    
    report = benchmark.generate_report()
    report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Full report saved to: {report_file}")
    print("\n✅ Benchmark suite completed!")


def main():
    parser = argparse.ArgumentParser(description="eduhu-assistant Benchmark Suite")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="Base URL of the API")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Password for authentication")
    
    args = parser.parse_args()
    
    if args.password == "your_password_here":
        print("⚠️  Warning: Using default password. Set with --password YOUR_PASSWORD")
        print("   (Continuing anyway...)\n")
    
    asyncio.run(run_benchmarks(args.url, args.password))


if __name__ == "__main__":
    main()
