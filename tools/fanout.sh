#!/usr/bin/env bash
# Controller, Phase 1: one issue per component in plan.json, assigned to Copilot.
# usage: ENGINE=copilot|claude tools/fanout.sh <owner/repo>
#   copilot: assign the issue to the Copilot coding agent (target setup).
#   claude:  label it agent:claude for the local stand-in harness (POC).
set -euo pipefail
repo="$1"
engine="${ENGINE:-copilot}"
components=$(python3 -c 'import json;print(" ".join(json.load(open("codebase-analysis/plan.json"))["components"]))')
gh label create "agent:claude" -R "$repo" --color 7057ff --force >/dev/null
for c in $components; do
  gh label create "component:$c" -R "$repo" --color 1d76db --force >/dev/null
  body=$(cat <<BODY
Use the \`component-analysis\` skill in \`.github/skills/component-analysis/SKILL.md\`.

**Component:** \`$c\`
**Pass 1 of 3: inventory.** Write only under \`codebase-analysis/components/$c/\`.
Done when \`python tools/gate.py $c --pass 1\` prints PASS.

Later passes will come as \`@copilot\` comments on the PR you open. Keep all passes for
this component on that one PR. Apply the stop-and-ask rule in the skill if you are blocked.
BODY
)
  case "$engine" in
    copilot) gh issue create -R "$repo" --title "Analyze component: $c" --body "$body" \
               --label "component:$c" --assignee "@copilot" ;;
    claude)  gh issue create -R "$repo" --title "Analyze component: $c" \
               --body "${body//@copilot/@claude}" --label "component:$c" --label "agent:claude" ;;
    *) echo "unknown ENGINE $engine" >&2; exit 2 ;;
  esac
done
