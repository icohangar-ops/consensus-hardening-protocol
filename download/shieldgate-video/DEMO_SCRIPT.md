# ShieldGate — 3-Minute Demo Video Script
## Splunk Agentic Ops Hackathon Submission

**Target: 3:00 minutes | Speaking pace: ~150 words/min**

---

## [0:00 – 0:15] TITLE CARD + INTRO (30 words)

ShieldGate. The least-privilege authorization gateway for AI agents investigating security incidents in Splunk. Built with AuthZed SpiceDB and Splunk MCP Server.

---

## [0:15 – 0:45] THE PROBLEM (75 words)

AI agents are revolutionizing security operations. They can investigate alerts, run SPL queries, and correlate events across indexes in seconds. But here's the problem. When you give an AI agent access to Splunk, what prevents it from querying indexes it shouldn't? What stops a compromised agent from exfiltrating sensitive data? Today, there is no authorization layer that enforces least-privilege for AI agents interacting with Splunk tools. The answer is either lock them down completely, or give them the keys to everything.

---

## [0:45 – 1:20] THE SOLUTION (90 words)

ShieldGate solves this with AuthZed, a Google Zanzibar-inspired authorization system, placed between every agent and Splunk. Before any Splunk tool executes, whether it's splunk run query, splunk get alerts, or splunk get indexes, ShieldGate checks permissions via SpiceDB. We define five role profiles, each with fine-grained permissions per tool, per index. SOC Tier 1 analysts get limited SPL access. SREs can only query observability indexes. Contractors are blocked from ad-hoc queries and see redacted results. AI agents need human approval for remediation actions. Every single permission decision is logged in a real-time audit timeline.

---

## [1:20 – 2:10] LIVE DEMO WALKTHROUGH (100 words)

Let me show you. Here's our dashboard with twelve synthetic security incidents. I'm logged in as a SOC Tier 1 analyst. I click on the data exfiltration incident. The AI investigator suggests SPL queries. I click one, and you can see the AuthZed permission check, ALLOW with a constraint: limited SPL only. Now I switch to Contractor role. Notice the lock icons on security incidents. I try running the same query, and AuthZed returns DENY. Contractors cannot execute ad-hoc queries. If I click an incident, all IP addresses, usernames, and hashes are redacted. Finally, I switch to SRE. I can query the observability index just fine, but if I try to query security, I get a DENY. SREs don't have access to security data.

---

## [2:10 – 2:40] AUTHZED ARCHITECTURE (65 words)

Under the hood, ShieldGate uses AuthZed SpiceDB with a Zanzibar-style relationship-based access control schema. Permissions are not static roles, they're computed from relationships between users, teams, indexes, and tools. A user's access to an incident is derived from their team membership, which is derived from their role. This is the same authorization pattern that powers Google Docs, YouTube, and Cloud IAM at scale.

---

## [2:40 – 3:00] CLOSING (35 words)

ShieldGate turns AI agent access from a security risk into a controlled, auditable, least-privilege operation. Every tool call checked. Every query governed. Every data access logged. Built for the Splunk Agentic Ops Hackathon.

---

## WORD COUNT SUMMARY

| Section | Duration | Words |
|---|---|---|
| Intro | 0:00-0:15 | ~30 |
| Problem | 0:15-0:45 | ~75 |
| Solution | 0:45-1:20 | ~90 |
| Demo Walkthrough | 1:20-2:10 | ~100 |
| Architecture | 2:10-2:40 | ~65 |
| Closing | 2:40-3:00 | ~35 |
| **Total** | **3:00** | **~395** |
