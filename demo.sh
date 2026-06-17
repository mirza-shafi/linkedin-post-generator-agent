#!/usr/bin/env bash
#
# demo.sh — a guided walkthrough of the LinkedIn Post Generator Agent.
# Great for recording a short demo video.
#
# Usage:
#   ./demo.sh            # uses the local virtualenv (.venv)
#   RUN_MODE=docker ./demo.sh   # runs each example through Docker instead
#
set -euo pipefail

# Pick how to run the app: local venv (default) or docker.
RUN_MODE="${RUN_MODE:-local}"

if [[ "$RUN_MODE" == "docker" ]]; then
  RUN=(docker run --rm --env-file .env linkedin-post-generator)
else
  RUN=(.venv/bin/python main.py)
fi

pause() {
  echo
  read -r -p "  ↵ Press Enter for the next example..." _ || true
  echo
}

banner() {
  echo
  echo "########################################################################"
  echo "#  $1"
  echo "########################################################################"
}

clear
banner "LinkedIn Post Generator Agent — Demo (mode: $RUN_MODE)"
echo "Built with LangChain + Google Gemini."
echo "Inputs: a topic and a language. Output: a ready-to-post LinkedIn post."
pause

banner "Example 1 — English, inspirational tone"
echo "\$ ${RUN[*]} -t \"AI in Healthcare\" -l English --tone inspirational"
echo
"${RUN[@]}" -t "AI in Healthcare" -l English --tone inspirational
pause

banner "Example 2 — Bengali (non-Latin script, fully translated)"
echo "\$ ${RUN[*]} -t \"Remote Work Productivity\" -l Bengali"
echo
"${RUN[@]}" -t "Remote Work Productivity" -l Bengali
pause

banner "Example 3 — Spanish, targeted at a specific audience"
echo "\$ ${RUN[*]} -t \"Cloud Cost Optimization\" -l Spanish --audience \"startup founders\""
echo
"${RUN[@]}" -t "Cloud Cost Optimization" -l Spanish --audience "startup founders"

banner "Demo complete ✅"
echo "Same agent, any topic, any language."
