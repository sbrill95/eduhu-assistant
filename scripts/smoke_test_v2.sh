#!/bin/bash
# Quick smoke test for all new endpoints
BASE="${1:-https://eduhu-assistant.onrender.com}"
TEACHER_ID="a4d218bd-4ac8-4ce3-8d41-c85db8be6e32"

echo "🔥 Smoke Test v2 — $BASE"
echo "================================"

# 1. Health
echo -n "Health: "
curl -sf "$BASE/api/health" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('version','?'))" 2>/dev/null || echo "FAIL"

# 2. Audio share
echo -n "Audio Share: "
curl -sf -X POST "$BASE/api/audio/share" -H "Content-Type: application/json" \
  -d "{\"teacher_id\":\"$TEACHER_ID\",\"title\":\"Test\",\"audio_type\":\"tts\",\"audio_ids\":[\"test\"]}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('access_code','FAIL'))" 2>/dev/null || echo "FAIL"

# 3. Public audio page
echo -n "Public Audio: "
CODE=$(curl -sf -X POST "$BASE/api/audio/share" -H "Content-Type: application/json" \
  -d "{\"teacher_id\":\"$TEACHER_ID\",\"title\":\"Test\",\"audio_type\":\"tts\",\"audio_ids\":[\"test\"]}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_code',''))" 2>/dev/null)
if [ -n "$CODE" ]; then
  curl -sf "$BASE/api/public/audio/pages/$CODE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('title','FAIL'))" 2>/dev/null || echo "FAIL"
else
  echo "FAIL (no code)"
fi

# 4. Admin endpoints
echo -n "Knowledge Cleanup: "
curl -sf -X POST "$BASE/api/admin/knowledge-cleanup" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','FAIL'))" 2>/dev/null || echo "FAIL"

echo -n "Seed Knowledge: "
curl -sf -X POST "$BASE/api/admin/seed-knowledge" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','FAIL'))" 2>/dev/null || echo "FAIL"

# 5. TTS (may fail if ElevenLabs key not working)
echo -n "TTS: "
curl -sf --max-time 30 -X POST "$BASE/api/audio/tts" -H "Content-Type: application/json" \
  -d '{"text":"Test","voice":"educator"}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('audio_id','FAIL: '+str(d.get('detail',''))))" 2>/dev/null || echo "TIMEOUT"

echo "================================"
echo "Done."
