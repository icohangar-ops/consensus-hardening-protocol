#!/bin/bash
# Merge Duplicate Repos on Codeberg + GitHub
# Run this on your local Mac
# 
# What this does:
#   1. RENAMES 5 Codeberg repos to match GitHub names
#   2. DELETES any zan-maker/ duplicates on GitHub (if accessible)
#   3. Creates missing repos on both platforms
#
# Usage: bash merge_duplicates.sh

set -e

: "${CB_TOKEN:?Set CB_TOKEN}"
: "${GH_TOKEN:?Set GH_TOKEN}"

echo "=== Step 1: Rename Codeberg repos to match GitHub ==="
echo ""

# Codeberg rename API: PATCH /api/v1/repos/{owner}/{repo}
rename_cb() {
    local old_name="$1"
    local new_name="$2"
    echo -n "  Renaming $old_name -> $new_name ... "
    
    result=$(curl -s -X PATCH \
        -H "Authorization: token ${CB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${new_name}\"}" \
        "https://codeberg.org/api/v1/repos/cubiczan/${old_name}")
    
    new_url=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url','ERROR'))" 2>/dev/null)
    if echo "$new_url" | grep -q "ERROR"; then
        echo "FAILED (may not exist or already renamed)"
        echo "    Raw: $(echo $result | head -c 100)"
    else
        echo "OK -> $new_url"
    fi
}

# These 5 Codeberg repos have different names than GitHub
rename_cb "finflowrl" "FinFlowRL"
rename_cb "minescope" "Minescope"
rename_cb "sec-earnings-workbench" "SEC-earnings-workbench"
rename_cb "Consensus-Hardening-Protocol-The-Differ" "consensus-hardening-protocol-differ"
rename_cb "stellar-Metal-and-mineral-traceability-and-tokenization-platform" "Stellar-critical-metal-traceability"

echo ""
echo "=== Step 2: Delete zan-maker duplicates on GitHub ==="
echo ""

# These 27 repos exist in both Cubiczan/ and zan-maker/ — delete zan-maker copies
ZAN_DUPS=(
    "autonomous-business-os" "battery-erp" "chainsight-ai"
    "closed-loop-finance" "Commodity-Price-Analyzer"
    "consensus-hardening-protocol" "convergence" "Critmin-Oracle"
    "decision-brief" "finance-cockpit" "FinFlowRL" "Genswarm-contract"
    "hedge-fund-13f-radar" "Investor-Relations-Pitch-Engine"
    "Liquify-gateway" "market-radar" "Metabocommand" "metal-price-agent"
    "Minescope" "minescope-signal" "resilient-agent" "scope-glacier"
    "scope-sentinel" "scope-vantage" "sec-earnings-workbench"
    "Stellar-critical-metal-traceability" "Swarmfi"
)

for repo in "${ZAN_DUPS[@]}"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
        -H "Authorization: token ${GH_TOKEN}" \
        "https://api.github.com/repos/zan-maker/${repo}")
    if [ "$code" = "204" ]; then
        echo "  DELETED: zan-maker/$repo"
    elif [ "$code" = "404" ]; then
        echo "  SKIP (not found): zan-maker/$repo"
    else
        echo "  FAILED ($code): zan-maker/$repo (may need different token)"
    fi
done

echo ""
echo "=== Step 3: Create missing GitHub Cubiczan repos ==="
echo ""

# These repos exist on Codeberg or zan-maker but NOT on GitHub Cubiczan
MISSING_GH=(
    "cash-flow-optimizer" "multi-agent-cfo-os" "market-sentiment-fedgpt"
    "working-capital-optimizer" "stratifi-core" "earnings-call-nlp-lab"
    "modenrich" "swarmchat" "Strata"
    "alpenglow-consensus-hardening-protocol" "cubiczan-swarm-pack"
)

for repo in "${MISSING_GH[@]}"; do
    echo -n "  Creating Cubiczan/$repo ... "
    result=$(curl -s -X POST \
        -H "Authorization: token ${GH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${repo}\",\"private\":false,\"description\":\"Cubiczan ${repo}\"}" \
        "https://api.github.com/user/repos")
    
    url=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url','ERROR'))" 2>/dev/null)
    if echo "$url" | grep -q "ERROR"; then
        msg=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','unknown'))" 2>/dev/null)
        echo "SKIP ($msg)"
    else
        echo "OK -> $url"
    fi
done

echo ""
echo "=== Step 4: Create missing Codeberg repos ==="
echo ""

MISSING_CB=(
    "cash-flow-optimizer" "multi-agent-cfo-os" "market-sentiment-fedgpt"
    "working-capital-optimizer" "stratifi-core" "earnings-call-nlp-lab"
    "modenrich" "swarmchat" "Strata"
    "alpenglow-consensus-hardening-protocol" "cubiczan-swarm-pack"
    "db-proxy" "swarmfi-preps" "IR-pitch-engine" "MetaCommand"
    "Critical-mineral-traceability-solana" "Reddit-Community-reply-assistant"
    "consensus-hardening-protocol-differ" "hedge-fund-13f-radar"
    "Cubiczan-swarm-pack" "Critical-metals-ERP" "Liquify-gateway"
)

for repo in "${MISSING_CB[@]}"; do
    echo -n "  Creating cubiczan/$repo ... "
    result=$(curl -s -X POST \
        -H "Authorization: token ${CB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${repo}\",\"private\":false}" \
        "https://codeberg.org/api/v1/user/repos")
    
    url=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url','ERROR'))" 2>/dev/null)
    if echo "$url" | grep -q "ERROR"; then
        msg=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','unknown'))" 2>/dev/null)
        echo "SKIP ($msg)"
    else
        echo "OK -> $url"
    fi
done

echo ""
echo "=== Done ==="
echo "Review the output above for any failures."
echo "You may need to separately clone+push content to newly created repos."
