#!/usr/bin/env python3
"""
eduhu-assistant Benchmark Suite
================================
Automatisierte Tests für Chat-Qualität, Memory, RAG, Research, Material-Generierung und API-Zuverlässigkeit.

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

TIMEOUT = 90.0  # seconds for API calls (Material generation can be slow)


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
# Helpers
# ============================================================================

def stamp_to_human(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime('%H:%M:%S')


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
        self.client = httpx.AsyncClient(timeout=TIMEOUT) 
        
    async def cleanup(self):
        await self.client.aclose()

    async def login(self) -> bool:
        """Authenticate and get teacher_id"""
        try:
            response = await self.client.post(
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
        try:
            payload = {
                "message": message,
                "teacher_id": self.teacher_id
            }
            if self.conversation_id:
                payload["conversation_id"] = self.conversation_id
            
            response = await self.client.post(
                f"{self.base_url}/api/chat/send",
                json=payload,
                headers=self.headers()
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                msg = data.get("message", {})
                content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
                return content, latency
            else:
                return None, latency
        except Exception as e:
            latency = (time.time() - start) * 1000
            print(f"⚠️  Message error: {e}")
            return None, latency
    
    async def generate_material(self, topic: str, material_type: str = "exam") -> tuple[bool, str, float]:
        """Generate material and check if download link is valid"""
        start = time.time()
        try:
            # Simulate the tool call or use the material endpoint directly if available
            # Since generating material is usually done via chat tool calls in this app,
            # we will trigger it via chat and look for the tool output/download link
            
            prompt = f"Erstelle eine {material_type} zum Thema {topic} für Klasse 9. Gib mir den Download-Link."
            content, latency = await self.send_message(prompt)
            
            if not content:
                return False, "No response", latency
            
            # Check for Markdown link pattern [Label](url)
            # The app likely returns a relative URL like /api/files/...
            link_match = re.search(r'\[.*?\]\((/api/.*?)\)', content)
            
            if link_match:
                download_url = self.base_url + link_match.group(1)
                
                # Verify link validity with HEAD request
                head_resp = await self.client.head(download_url)
                if head_resp.status_code in [200, 307, 308]:
                     return True, content, latency
                else:
                     return False, f"Download link invalid: {head_resp.status_code}", latency
            else:
                return False, "No download link found in response", latency

        except Exception as e:
            latency = (time.time() - start) * 1000
            return False, str(e), latency

    async def get_conversation_history(self) -> tuple[Optional[List], float]:
        """Get conversation history"""
        start = time.time()
        try:
            response = await self.client.get(
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
        try:
            response = await self.client.get(
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
        # If expected pattern is empty, we assume it's a pass if no error occurred (for some tests)
        if not expected_pattern:
             passed = error is None
        else:
            try:
                passed = bool(re.search(expected_pattern, actual, re.IGNORECASE | re.DOTALL)) if actual else False
            except re.error:
                print(f"❌ Regex error with pattern: {expected_pattern}")
                passed = False
        
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

        # Test: Agent Rückfragen (Vage Anfrage)
        # User Audio: "Der Haupt-Agent soll die richtigen Rückfragen stellen"
        vague_msg = "Erstelle mir Material."
        resp_vague, lat_vague = await self.send_message(vague_msg)
        self.add_result(
            category="Chat Quality",
            name="Agent Ask-Back (Vague Input)",
            input_data=vague_msg,
            expected_pattern=r"(welche.*klasse|welches.*thema|welches.*fach|worum.*geht.*es)",
            actual=resp_vague or "",
            latency=lat_vague
        )
    
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

        # Test 4: Complex Scenario Persistence (User Audio Request)
        # Szenario: "Längere Konversation über Belohnungssysteme und Unterrichtsstörung (fiktiver Fall Grundschule)"
        print("\n   --- Starting Complex Memory Scenario (Grundschule/Max) ---")
        
        # Step 4a: Seed Memory
        seed_msg = "Ich habe einen Schüler Max in der 3. Klasse, der ständig den Unterricht stört. Wir probieren gerade ein Belohnungssystem mit Stickern."
        await self.send_message(seed_msg)
        await asyncio.sleep(2) # Give Memory Agent time to extract
        
        # Step 4b: New Context / Distraction
        self.conversation_id = None # Simulates "Morgen"/"Neuer Chat"
        
        # Step 4c: Recall
        recall_msg = "Wie läuft das Experiment mit Max?"
        resp_recall, lat_recall = await self.send_message(recall_msg)
        
        self.add_result(
            category="Memory Agent",
            name="Complex Scenario Persistence (Cross-Session)",
            input_data=recall_msg,
            expected_pattern=r"(max|sticker|belohnung|stört|3\.\s*klasse|grundschule)",
            actual=resp_recall or "",
            latency=lat_recall
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
        
        self.add_result(
            category="Research Agent",
            name="Web Search for Teaching Methods",
            input_data=msg,
            expected_pattern=r"(https?://|www\.|quelle|referenz|link|methode|experiment)",
            actual=response or "",
            latency=latency
        )

    async def benchmark_material_generation(self):
        """Category 5: Material Generation Tests"""
        print("\n" + "="*60)
        print("📄 CATEGORY 5: MATERIAL GENERATION")
        print("="*60)
        
        self.conversation_id = None
        
        # Test 1: Exam generation
        topic = "Mechanik (Newton)"
        success, content, latency = await self.generate_material(topic, "Klausur")
        
        self.add_result(
            category="Material Generation",
            name="Exam Generation & Download Link",
            input_data=f"Klausur: {topic}",
            expected_pattern=r"\[.*?\]\(/api/.*?\)", # Expect a markdown link
            actual=content,
            latency=latency,
            error=None if success else "Download link check failed"
        )

        await asyncio.sleep(1)

        # Test 2: Differenzierung (User Audio Request)
        # "Differenzierung (verschiedene Niveaus)"
        diff_topic = "Leseverständnis (Fabeln)"
        diff_prompt = f"Erstelle differenziertes Übungsmaterial (3 Niveaus) zum Thema {diff_topic} für Klasse 5."
        
        # We check if the AI mentions "Niveau" or labels them, and provides a download
        # Note: Material generation tool usually produces ONE file, but the text response says "Here is the material..."
        diff_content, diff_latency = await self.send_message(diff_prompt)
        
        has_download = bool(re.search(r"\[.*?\]\(/api/.*?\)", diff_content or ""))
        mentions_levels = bool(re.search(r"(niveau|basis|erweitert|starters|experts|differenz)", diff_content or "", re.IGNORECASE))
        
        self.add_result(
            category="Material Generation",
            name="Differentiation Logic",
            input_data=diff_prompt,
            expected_pattern=r"(niveau|basis|differenz)",
            actual=diff_content or "",
            latency=diff_latency,
            error=None if (has_download and mentions_levels) else "Missing download or differentiation context"
        )
    
    async def benchmark_summary_agent(self):
        """Category 6: Summary Agent Tests"""
        print("\n" + "="*60)
        print("📋 CATEGORY 6: SUMMARY AGENT")
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
        # We also check if the last response actually contains a summary of the conversation topic "Mechanik"
        
        self.add_result(
            category="Summary Agent",
            name="Long Conversation Summary",
            input_data=f"Sent {len(messages)} messages",
            expected_pattern=r"(zusammenfassung|überblick|mechanik|klasse.*10|experimente)",
            actual=last_response,
            latency=total_latency / len(messages)
        )
    
    async def benchmark_system_prompt(self):
        """Category 7: System Prompt & Context Tests"""
        print("\n" + "="*60)
        print("⚙️  CATEGORY 7: SMART PRELOADING & CONTEXT")
        print("="*60)
        
        # Test 1: Profile context in response (Smart Preloading)
        # User Audio: "Testen, ob Smart Preloading Context Loading tatsächlich getestet wird"
        profile, prof_latency = await self.get_profile()
        
        if profile:
            bundesland = profile.get("bundesland", "unknown")
            faecher = profile.get("subjects", [])
            klassenniveaus = profile.get("grades", [])
            
            self.conversation_id = None
            msg = "Was weißt du über mein Profil und meine Fächer?"
            response, latency = await self.send_message(msg)
            
            # Check if profile data appears in context
            # We construct a regex pattern based on the actual profile
            # We expect the AI to explicitly mention the data injected via system prompt
            
            p_bundesland = re.search(re.escape(bundesland), response, re.IGNORECASE)
            # Check at least one subject
            p_subject = False
            if faecher:
                p_subject = any(re.search(re.escape(f), response, re.IGNORECASE) for f in faecher)
            else:
                p_subject = True # Skip if no subjects set
                
            actual_log = f"Found Bundesland: {bool(p_bundesland)}, Found Subject: {p_subject}\nResponse: {response[:100]}..."

            self.add_result(
                category="Smart Preloading",
                name="Profile Context Verified",
                input_data=msg,
                expected_pattern=f"({bundesland}|{'|'.join(faecher) if faecher else '.*'})",
                actual=response or "",
                latency=latency,
                error=None if (p_bundesland and p_subject) else "System prompt did not inject profile data correctly"
            )
        else:
             self.add_result(
                category="Smart Preloading",
                name="Profile Context Verified",
                input_data="Get Profile",
                expected_pattern=".*",
                actual="Failed to load profile",
                latency=prof_latency,
                error="Could not load profile to verify context"
            )
    
    async def benchmark_api_reliability(self):
        """Category 8: API Reliability & Error Handling"""
        print("\n" + "="*60)
        print("🔧 CATEGORY 8: API RELIABILITY")
        print("="*60)
        
        # Test 1: Login endpoint
        start = time.time()
        try:
            response = await self.client.post(
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
            response = await self.client.post(
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
            response = await self.client.post(
                f"{self.base_url}/api/chat/send",
                json={"message": "", "teacher_id": self.teacher_id},
                headers=self.headers()
            )
            latency = (time.time() - start) * 1000
            # Should either reject (400) or handle gracefully (200) or validation error 422
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
            response = await self.client.post(
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
            self.add_result(
                category="API Reliability",
                name="Conversation History Endpoint",
                input_data=f"GET /api/chat/history",
                expected_pattern="200",
                actual=f"Returned {len(history) if history else 0} messages",
                latency=hist_latency,
                error=None if history is not None else "Failed to fetch history"
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
            
            # Print failures
            for r in cat_results:
                if not r.passed:
                     print(f"   ❌ FAILED: {r.name}")
                     if r.error:
                         print(f"      Error: {r.error}")
        
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
    
    try:
        # Login
        if not await benchmark.login():
            print("\n❌ Cannot proceed without authentication")
            return
        
        # Run all benchmark categories
        await benchmark.benchmark_chat_quality()
        await benchmark.benchmark_memory_agent()
        await benchmark.benchmark_curriculum_rag()
        await benchmark.benchmark_research_agent()
        await benchmark.benchmark_material_generation()  # New category
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
    
    finally:
        await benchmark.cleanup()


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
