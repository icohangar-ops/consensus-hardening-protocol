#!/bin/bash
# codeberg_final_fix.sh — Final cleanup: create missing repos, push all 4, delete old duplicates
set -u

GH_TOKEN="ghp_REDACTED_TOKEN"
CB_TOKEN="d7498dde953c0590a52666ad8ccf9a83279793fb"
GH_USER="cubiczan"
CB_USER="cubiczan"
TMPDIR=$(mktemp -d)

trap "rm -rf $TMPDIR" EXIT

# ── Phase 1: Create the 2 missing Codeberg repos ──
echo "========================================"
echo "PHASE 1: Create missing Codeberg repos"
echo "========================================"

for repo in "Stellar-critical-metal-traceability" "consensus-hardening-protocol-differ"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $CB_TOKEN" \
    "https://codeberg.org/api/v1/repos/$CB_USER/$repo")

  if [ "$status" = "200" ]; then
    echo "  ✅ $repo already exists"
  else
    echo "  Creating $repo on Codeberg..."
    result=$(curl -s -w "\n%{http_code}" \
      -X POST \
      -H "Authorization: token $CB_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$repo\",\"private\":false,\"auto_init\":false}" \
      "https://codeberg.org/api/v1/user/repos")
    code=$(echo "$result" | tail -1)
    if [ "$code" = "201" ]; then
      echo "  ✅ Created $repo"
    else
      echo "  ❌ Failed to create $repo (HTTP $code)"
    fi
  fi
  sleep 1
done

# ── Phase 2: Push all 4 repos from GitHub to Codeberg ──
echo ""
echo "========================================"
echo "PHASE 2: Push 4 repos GitHub → Codeberg"
echo "========================================"

REPOS=(
  "hedge-fund-13f-radar"
  "Investor-Relations-Pitch-Engine"
  "Stellar-critical-metal-traceability"
  "consensus-hardening-protocol-differ"
)

for repo in "${REPOS[@]}"; do
  echo ""
  echo "── $repo ──"
  dir="$TMPDIR/$repo"
  rm -rf "$dir"

  # Clone from GitHub
  if git clone --depth 1 "https://${GH_TOKEN}@github.com/${GH_USER}/${repo}.git" "$dir" 2>&1; then
    echo "  ✅ Cloned from GitHub"

    # Unshallow for Codeberg compatibility
    (cd "$dir" && git fetch --unshallow 2>&1)

    # Remove GitHub remote, add Codeberg remote
    (cd "$dir" && git remote remove origin 2>/dev/null)
    (cd "$dir" && git remote add origin "https://${CB_TOKEN}@codeberg.org/${CB_USER}/${repo}.git")

    # Push
    if (cd "$dir" && git push -u origin main 2>&1); then
      echo "  ✅ Pushed to Codeberg"
    else
      # Try master branch
      if (cd "$dir" && git push -u origin master 2>&1); then
        echo "  ✅ Pushed to Codeberg (master)"
      else
        echo "  ❌ Push failed"
      fi
    fi
  else
    echo "  ❌ Clone failed"
  fi
  sleep 1
done

# ── Phase 3: Delete old/broken repos on Codeberg ──
echo ""
echo "========================================"
echo "PHASE 3: Delete old/broken Codeberg repos"
echo "========================================"

OLD_REPOS=(
  "stellar-Metal-and-mineral-traceability-and-tokenization-platform"
  "Consensus-Hardening-Protocol-The-Differ"
  "finflowrl"
  "minescope"
  "sec-earnings-workbench"
  "critical-metals-ERP"
  "Critical-mineral-traceability-solana"
)

for repo in "${OLD_REPOS[@]}"; do
  echo "  Deleting $repo..."
  result=$(curl -s -w "\n%{http_code}" \
    -X DELETE \
    -H "Authorization: token $CB_TOKEN" \
    "https://codeberg.org/api/v1/repos/$CB_USER/$repo")
  code=$(echo "$result" | tail -1)
  if [ "$code" = "204" ] || [ "$code" = "200" ]; then
    echo "  ✅ Deleted $repo"
  else
    echo "  ❌ Failed to delete $repo (HTTP $code)"
  fi
  sleep 1
done

echo ""
echo "========================================"
echo "DONE"
echo "========================================"
