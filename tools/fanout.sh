#!/usr/bin/env bash
# Controller, Phase 1: one issue per component in plan.json, assigned to Copilot.
# usage: tools/fanout.sh <owner/repo>
set -euo pipefail
repo="$1"
components=$(python3 -c 'import json;print(" ".join(json.load(open("codebase-analysis/plan.json"))["components"]))')
for c in $components; do
  body=$(cat <<BODY
Use the \`component-analysis\` skill in \`.github/skills/component-analysis/SKILL.md\`.

**Component:** \`$c\`
**Pass 1 of 3: inventory.** Write only under \`codebase-analysis/components/$c/\`.
Done when \`python tools/gate.py $c --pass 1\` prints PASS.

Later passes will come as \`@copilot\` comments on the PR you open. Keep all passes for
this component on that one PR. Apply the stop-and-ask rule in the skill if you are blocked.
BODY
)
  gh issue create -R "$repo" --title "Analyze component: $c" --body "$body" --assignee "@copilot"
done
