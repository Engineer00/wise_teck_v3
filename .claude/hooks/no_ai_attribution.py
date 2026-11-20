"""PreToolUse hook: block git commits that credit Claude / AI (owner rule: commits are authored by Engineer00 only).

Reads the tool call as JSON on stdin. Exit code 2 blocks the call and shows stderr to Claude.
"""
import json
import re
import sys

try:
    call = json.load(sys.stdin)
except Exception:
    sys.exit(0)

command = (call.get("tool_input") or {}).get("command", "") or ""
if not re.search(r"\bgit\b[^\n]*\bcommit\b", command):
    sys.exit(0)

text = command
m = re.search(r"(?:-F|--file)[ =]\s*(\"[^\"]+\"|'[^']+'|\S+)", command)
if m and m.group(1).strip("\"'") != "-":
    try:
        text += "\n" + open(m.group(1).strip("\"'"), encoding="utf-8").read()
    except OSError:
        pass

if re.search(r"co-authored-by:[^\n]*(claude|anthropic)|generated with \[?claude|claude\.com/claude-code|noreply@anthropic\.com",
             text, re.IGNORECASE):
    print("Blocked: this project's commits must not credit Claude or AI (no Co-Authored-By / 'Generated with Claude'). "
          "Remove the attribution lines and commit as Engineer00.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
