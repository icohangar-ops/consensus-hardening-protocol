#!/bin/bash
# CHP-Hardened Repos: Push to Codeberg
# Run this on your local Mac (not the server)
# Usage: bash push_codeberg_chp.sh
#
# Prerequisites:
#   export CB_TOKEN="your-codeberg-token"
#   export GH_TOKEN="your-github-token"

set -e

: "${CB_TOKEN:?Set CB_TOKEN first}"
: "${GH_TOKEN:?Set GH_TOKEN first}"

TMPDIR="/tmp/cbp_chp_$$"
mkdir -p "$TMPDIR"
LOG="$TMPDIR/push_log.txt"
FAILED="$TMPDIR/failed.txt"

echo "=== CHP Codeberg Push Script ==="
echo "Cloning from GitHub, pushing to Codeberg"
echo "Log: $LOG"
echo ""

push_repo() {
    local gh_name="$1"
    local cb_name="$2"
    local branch="$3"
    local clone_dir="$TMPDIR/$gh_name"
    
    echo -n "  $gh_name -> $cb_name ... "
    
    # Clone from GitHub
    if ! git clone --depth 1 --branch "$branch" \
        "https://Cubiczan:${GH_TOKEN}@github.com/Cubiczan/${gh_name}.git" \
        "$clone_dir" 2>/dev/null; then
        echo "CLONE_FAIL"
        echo "$gh_name|CLONE_FAIL" >> "$FAILED"
        rm -rf "$clone_dir"
        return 1
    fi
    
    # Push to Codeberg
    if git -C "$clone_dir" push \
        "https://cubiczan:${CB_TOKEN}@codeberg.org/cubiczan/${cb_name}.git" \
        "$branch" --force 2>/dev/null; then
        echo "OK"
        echo "$gh_name|OK" >> "$LOG"
    else
        # Try creating the repo first
        curl -s -X POST \
            -H "Authorization: token ${CB_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"${cb_name}\",\"private\":false}" \
            "https://codeberg.org/api/v1/user/repos" > /dev/null 2>&1
        
        # Retry push
        if git -C "$clone_dir" push \
            "https://cubiczan:${CB_TOKEN}@codeberg.org/cubiczan/${cb_name}.git" \
            "$branch" --force 2>/dev/null; then
            echo "OK (created repo)"
            echo "$gh_name|OK_CREATED" >> "$LOG"
        else
            echo "PUSH_FAIL"
            echo "$gh_name|PUSH_FAIL|$cb_name" >> "$FAILED"
        fi
    fi
    
    rm -rf "$clone_dir"
    return 0
}

echo "--- Batch 1: Top-level repos ---"
push_repo "autonomous-business-os" "autonomous-business-os" "main"
push_repo "battery-erp" "battery-erp" "main"
push_repo "closed-loop-finance" "closed-loop-finance" "main"
push_repo "Commodity-Price-Analyzer" "Commodity-Price-Analyzer" "main"
push_repo "FinFlowRL" "finflowrl" "main"
push_repo "zan-finflowrl" "zan-finflowrl" "main"
push_repo "minescope-signal" "minescope-signal" "main"
push_repo "resilient-agent" "resilient-agent" "main"
push_repo "sec-earnings-workbench" "sec-earnings-workbench" "main"

echo ""
echo "--- Batch 2: Mineral-review repos ---"
push_repo "consensus-hardening-protocol" "consensus-hardening-protocol" "main"
push_repo "convergence" "convergence" "main"
push_repo "chainsight-ai" "chainsight-ai" "main"
push_repo "Critmin-Oracle" "Critmin-Oracle" "main"
push_repo "Genswarm-contract" "Genswarm-contract" "main"
push_repo "Stellar-critical-metal-traceability" "stellar-Metal-and-mineral-traceability-and-tokenization-platform" "main"
push_repo "Swarmfi" "Swarmfi" "main"
push_repo "metal-price-agent" "metal-price-agent" "main"
push_repo "scope-vantage" "scope-vantage" "main"
push_repo "scope-glacier" "scope-glacier" "main"
push_repo "scope-sentinel" "scope-sentinel" "main"

echo ""
echo "--- Batch 3: Remote-cloned repos ---"
push_repo "consensus-hardening-protocol-differ" "Consensus-Hardening-Protocol-The-Differ" "main"
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

echo ""
echo "=== RESULTS ==="
echo "Succeeded: $(wc -l < "$LOG" | tr -d ' ')"
echo "Failed: $(wc -l < "$FAILED" 2>/dev/null | tr -d ' ')"
if [ -f "$FAILED" ] && [ -s "$FAILED" ]; then
    echo ""
    echo "Failed repos:"
    cat "$FAILED"
fi

# Cleanup
rm -rf "$TMPDIR"
