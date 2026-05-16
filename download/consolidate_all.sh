#!/bin/bash
# =============================================================================
# CUBICZAN REPO CONSOLIDATION — Run on your local Mac
# =============================================================================
# Does everything in one shot:
#   1. Renames Codeberg repos to match GitHub canonical names
#   2. Deletes old Codeberg name duplicates
#   3. Deletes 27 zan-maker/ duplicates on GitHub
#   4. Creates missing repos on both platforms
#   5. Pushes all CHP-hardened repos to Codeberg
#
# Usage:
#   export CB_TOKEN="d7498dde953c0590a52666ad8ccf9a83279793fb"
#   export GH_TOKEN="ghp_REDACTED_TOKEN"
#   export ZM_TOKEN="ghp_REDACTED_TOKEN"
#   bash consolidate_all.sh
# =============================================================================

set -e

: "${CB_TOKEN:?Set CB_TOKEN (Codeberg)}"
: "${GH_TOKEN:?Set GH_TOKEN (GitHub Cubiczan)}"
: "${ZM_TOKEN:?Set ZM_TOKEN (GitHub zan-maker with delete_repo)}"

OK=0; FAIL=0; SKIP=0

log_ok()   { echo "  ✅ $1"; OK=$((OK+1)); }
log_fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
log_skip() { echo "  ⏭️  $1"; SKIP=$((SKIP+1)); }

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 1: Rename 5 Codeberg repos to match GitHub names"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

rename_cb() {
    local old="$1" new="$2"
    local r=$(curl -s -X PATCH \
        -H "Authorization: token ${CB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${new}\"}" \
        "https://codeberg.org/api/v1/repos/cubiczan/${old}" 2>/dev/null)
    local url=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null)
    if [ -n "$url" ] && echo "$url" | grep -q "$new"; then
        log_ok "Renamed: $old → $new"
    else
        local msg=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('message','empty'))" 2>/dev/null)
        log_skip "Rename $old → $new: $msg"
    fi
    sleep 0.5
}

rename_cb "finflowrl" "FinFlowRL"
rename_cb "minescope" "Minescope"
rename_cb "sec-earnings-workbench" "SEC-earnings-workbench"
rename_cb "Consensus-Hardening-Protocol-The-Differ" "consensus-hardening-protocol-differ"
rename_cb "stellar-Metal-and-mineral-traceability-and-tokenization-platform" "Stellar-critical-metal-traceability"

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 2: Delete old Codeberg name duplicates"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

delete_cb() {
    local repo="$1"
    local code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
        -H "Authorization: token ${CB_TOKEN}" \
        "https://codeberg.org/api/v1/repos/cubiczan/${repo}")
    if [ "$code" = "204" ]; then log_ok "Deleted Codeberg: $repo"
    elif [ "$code" = "404" ]; then log_skip "Codeberg $repo: not found (already gone)"
    else log_fail "Delete Codeberg $repo: HTTP $code"
    fi
    sleep 0.5
}

delete_cb "finflowrl"
delete_cb "minescope"
delete_cb "sec-earnings-workbench"
delete_cb "stellar-critical-metal-traceability"
delete_cb "stellar-Metal-and-mineral-traceability-and-tokenization-platform"
delete_cb "Consensus-Hardening-Protocol-The-Differ"

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 3: Delete 27 zan-maker/ duplicates on GitHub"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

for repo in autonomous-business-os battery-erp closed-loop-finance \
    Commodity-Price-Analyzer consensus-hardening-protocol convergence \
    Critmin-Oracle decision-brief finance-cockpit FinFlowRL Genswarm-contract \
    hedge-fund-13f-radar Investor-Relations-Pitch-Engine Liquify-gateway \
    market-radar Metabocommand metal-price-agent Minescope minescope-signal \
    resilient-agent scope-glacier scope-sentinel scope-vantage \
    sec-earnings-workbench Stellar-critical-metal-traceability Swarmfi \
    chainsight-ai; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
        -H "Authorization: token ${ZM_TOKEN}" \
        "https://api.github.com/repos/zan-maker/${repo}")
    if [ "$code" = "204" ]; then log_ok "Deleted zan-maker/$repo"
    elif [ "$code" = "404" ]; then log_skip "zan-maker/$repo: not found"
    else log_fail "zan-maker/$repo: HTTP $code"
    fi
done

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 4: Create missing repos on GitHub Cubiczan"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

for repo in cash-flow-optimizer multi-agent-cfo-os market-sentiment-fedgpt \
    working-capital-optimizer stratifi-core earnings-call-nlp-lab modenrich \
    swarmchat Strata alpenglow-consensus-hardening-protocol; do
    r=$(curl -s -X POST -H "Authorization: token ${GH_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${repo}\",\"private\":false}" \
        "https://api.github.com/user/repos")
    url=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null)
    if [ -n "$url" ]; then log_ok "Created Cubiczan/$repo"
    else
        msg=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('errors',[{}])[0].get('message','') if json.load(sys.stdin).get('errors') else json.load(sys.stdin).get('message',''))" 2>/dev/null)
        log_skip "Cubiczan/$repo: $msg"
    fi
done

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 5: Create missing repos on Codeberg"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

for repo in SEC-earnings-workbench consensus-hardening-protocol-differ \
    Stellar-critical-metal-traceability FinFlowRL Minescope \
    cash-flow-optimizer multi-agent-cfo-os market-sentiment-fedgpt \
    working-capital-optimizer stratifi-core earnings-call-nlp-lab modenrich \
    swarmchat Strata alpenglow-consensus-hardening-protocol \
    db-proxy swarmfi-preps IR-pitch-engine MetaCommand \
    Critical-mineral-traceability-solana Reddit-Community-reply-assistant \
    hedge-fund-13f-radar Critical-metals-ERP Liquify-gateway \
    Cubiczan-swarm-pack; do
    r=$(curl -s -X POST -H "Authorization: token ${CB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${repo}\",\"private\":false}" \
        "https://codeberg.org/api/v1/user/repos")
    url=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null)
    if [ -n "$url" ]; then log_ok "Created cubiczan/$repo"
    else
        msg=$(echo "$r" | python3 -c "import sys,json;print(json.load(sys.stdin).get('message',''))" 2>/dev/null)
        log_skip "cubiczan/$repo: $msg"
    fi
    sleep 0.3
done

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  PHASE 6: Push all 33 repos from GitHub → Codeberg"
echo "══════════════════════════════════════════════════════════════"
###############################################################################

push_repo() {
    local gh_name="$1"
    local cb_name="$2"
    local branch="${3:-main}"
    local tmpdir="/tmp/cbp_$$"

    echo -n "  $gh_name → cubiczan/$cb_name ... "

    # Clone from GitHub (shallow)
    if ! git clone --depth 1 --branch "$branch" \
        "https://Cubiczan:${GH_TOKEN}@github.com/Cubiczan/${gh_name}.git" \
        "$tmpdir" 2>/dev/null; then
        echo "CLONE_FAIL"
        rm -rf "$tmpdir"
        FAIL=$((FAIL+1))
        return 1
    fi

    # Push to Codeberg (force to overwrite any existing content)
    if git -C "$tmpdir" push \
        "https://cubiczan:${CB_TOKEN}@codeberg.org/cubiczan/${cb_name}.git" \
        "$branch" --force 2>/dev/null; then
        echo "OK"
        OK=$((OK+1))
    else
        echo "PUSH_FAIL"
        FAIL=$((FAIL+1))
    fi

    rm -rf "$tmpdir"
}

push_repo "autonomous-business-os" "autonomous-business-os" "main"
push_repo "battery-erp" "battery-erp" "main"
push_repo "closed-loop-finance" "closed-loop-finance" "main"
push_repo "Commodity-Price-Analyzer" "Commodity-Price-Analyzer" "main"
push_repo "FinFlowRL" "FinFlowRL" "main"
push_repo "zan-finflowrl" "zan-finflowrl" "main"
push_repo "minescope-signal" "minescope-signal" "main"
push_repo "resilient-agent" "resilient-agent" "main"
push_repo "sec-earnings-workbench" "SEC-earnings-workbench" "main"
push_repo "consensus-hardening-protocol" "consensus-hardening-protocol" "main"
push_repo "convergence" "convergence" "main"
push_repo "chainsight-ai" "chainsight-ai" "main"
push_repo "Critmin-Oracle" "Critmin-Oracle" "main"
push_repo "Genswarm-contract" "Genswarm-contract" "main"
push_repo "Stellar-critical-metal-traceability" "Stellar-critical-metal-traceability" "main"
push_repo "Swarmfi" "Swarmfi" "main"
push_repo "metal-price-agent" "metal-price-agent" "main"
push_repo "scope-vantage" "scope-vantage" "main"
push_repo "scope-glacier" "scope-glacier" "main"
push_repo "scope-sentinel" "scope-sentinel" "main"
push_repo "consensus-hardening-protocol-differ" "consensus-hardening-protocol-differ" "main"
push_repo "Critical-metals-ERP" "Critical-metals-ERP" "main"
push_repo "Critical-mineral-traceability-solana" "Critical-mineral-traceability-solana" "main"
push_repo "Cubiczan-swarm-pack" "Cubiczan-swarm-pack" "main"
push_repo "db-proxy" "db-proxy" "main"
push_repo "hedge-fund-13f-radar" "hedge-fund-13f-radar" "main"
push_repo "Investor-Relations-Pitch-Engine" "Investor-Relations-Pitch-Engine" "main"
push_repo "IR-pitch-engine" "IR-pitch-engine" "main"
push_repo "Liquify-gateway" "Liquify-gateway" "main"
push_repo "Metabocommand" "Metabocommand" "main"
push_repo "Minescope" "Minescope" "main"
push_repo "Reddit-Community-reply-assistant" "Reddit-Community-reply-assistant" "main"
push_repo "swarmfi-preps" "swarmfi-preps" "master"

###############################################################################
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  RESULTS"
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ Success: $OK"
echo "  ❌ Failed:  $FAIL"
echo "  ⏭️  Skipped: $SKIP"
echo "══════════════════════════════════════════════════════════════"
echo ""
