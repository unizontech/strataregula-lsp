#!/usr/bin/env bash
set -euo pipefail
if [ -f docs/README_FOR_DEVELOPERS.md ]; then
  echo -e "\n[devcontainer] 開発前に必ず docs/README_FOR_DEVELOPERS.md を確認してください。"
fi

# --- Auto-open AGENTS.md for read-and-follow culture ---
if [ -f "AGENTS.md" ]; then
  code -r AGENTS.md >/dev/null 2>&1 || true
fi