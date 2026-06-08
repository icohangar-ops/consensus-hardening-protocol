#!/usr/bin/env python3
"""Generate a 3-minute CHP demo video using PIL frames + ffmpeg encoding."""

from PIL import Image, ImageDraw, ImageFont
import subprocess, os

MEDIA = "/home/z/my-project/mineral-review/consensus-hardening-protocol/docs/media"
FRAMES = f"{MEDIA}/frames"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1920, 1080
FPS = 24

# Colors
BG = (13, 17, 23)
TBG = (22, 27, 34)
BD = (48, 54, 62)
GREEN = (63, 185, 80)
CYAN = (88, 166, 255)
YELLOW = (210, 153, 34)
RED = (248, 81, 73)
WHITE = (230, 237, 243)
GRAY = (139, 148, 158)
DIM = (72, 79, 88)
PURPLE = (188, 140, 255)

# Fonts
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
    FM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    FM_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
    FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    FM_S = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
    FS_S = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    FM_T = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except:
    FB = ImageFont.load_default()
    FM = FM_B = FS = FS_S = FM_S = FM_T = ImageFont.load_default()


def new_frame():
    return Image.new("RGB", (W, H), BG)


def terminal_frame(title="chp-session - cme cli"):
    """Create a frame with a terminal window."""
    img = new_frame()
    d = ImageDraw.Draw(img)
    # Terminal bg
    d.rectangle([80, 70, 1840, 1010], fill=TBG, outline=BD)
    # Title bar
    d.rectangle([80, 70, 1840, 110], fill=(33, 38, 45))
    # Dots
    d.ellipse([100, 78, 118, 96], fill=(255, 95, 87))
    d.ellipse([128, 78, 146, 96], fill=(254, 188, 46))
    d.ellipse([156, 78, 174, 96], fill=(40, 200, 64))
    # Title
    d.text((200, 82), title, fill=GRAY, font=FM_T)
    return img, d


def text_centered(d, text, y, font, color):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, y), text, fill=color, font=font)


frame_num = 0


def save(img):
    global frame_num
    img.save(f"{FRAMES}/f{frame_num:05d}.png")
    frame_num += 1


def hold(img, seconds):
    for _ in range(int(seconds * FPS)):
        save(img)


def draw_rounded_rect(d, xy, radius, **kwargs):
    x0, y0, x1, y1 = xy
    d.rectangle([x0 + radius, y0, x1 - radius, y1], **kwargs)
    d.rectangle([x0, y0 + radius, x1, y1 - radius], **kwargs)
    d.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, **kwargs)
    d.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, **kwargs)
    d.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, **kwargs)
    d.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, **kwargs)


print("Generating frames...")

# ═════════════════════════════════════════════════════════
# Scene 1: Title Card (0:00 - 0:15) - 360 frames
# ═════════════════════════════════════════════════════════
print("  Scene 1: Title Card...", flush=True)
img = new_frame()
d = ImageDraw.Draw(img)
# Card
draw_rounded_rect(d, (560, 100, 1360, 540), 16, fill=TBG, outline=BD)
# Shield
d.rectangle([900, 210, 1020, 310], fill=CYAN)
d.rectangle([888, 175, 1032, 225], fill=CYAN)
# Texts
text_centered(d, "Consensus Hardening Protocol", 620, FB, WHITE)
text_centered(d, "Multi-Agent Decision Governance for High-Stakes Finance", 680, FS, GRAY)
text_centered(d, "cme chp-start | chp-receive | chp-validate | chp-triangulate", 740, FM_S, CYAN)
text_centered(d, "A 3-minute walkthrough", 800, FM_T, DIM)
# MIT badge
draw_rounded_rect(d, (840, 850, 1080, 886), 6, fill=TBG, outline=BD)
text_centered(d, "MIT License", 857, FM_T, GREEN)
hold(img, 15)

# ═════════════════════════════════════════════════════════
# Scene 2: Problem Statement (0:15 - 0:40) - 600 frames
# ═════════════════════════════════════════════════════════
print("  Scene 2: Problem Statement...", flush=True)
lines = [
    (200, "When organizations deploy multiple AI agents,", WHITE, FS),
    (200, "three things break:", WHITE, FS),
    (300, "1. Context Fragmentation", RED, FS),
    (340, "   Each agent sees a different slice of the organization", GRAY, FS_S),
    (400, "2. Reasoning Opacity", YELLOW, FS),
    (440, "   Humans get conclusions without seeing how they were reached", GRAY, FS_S),
    (500, "3. Output Drift", PURPLE, FS),
    (540, "   Agents produce prose; humans need something runnable", GRAY, FS_S),
    (640, "CHP solves all three with hardened, auditable decision sessions.", CYAN, FS_S),
    (700, "Every claim is traced. Every gate is enforced.", GREEN, FS_S),
    (750, "Consensus is not enough until it is hardened.", GREEN, FB),
]
img = new_frame()
d = ImageDraw.Draw(img)
for y, text, color, font in lines:
    d.text((160, y), text, fill=color, font=font)
hold(img, 25)

# ═════════════════════════════════════════════════════════
# Scene 3: Architecture (0:40 - 1:05) - 600 frames
# ═════════════════════════════════════════════════════════
print("  Scene 3: Architecture...", flush=True)
img = new_frame()
d = ImageDraw.Draw(img)
d.text((160, 80), "Architecture: Five Composed Subsystems", fill=WHITE, font=FB)
d.text((160, 130), "Each subsystem is independently specifiable and composable", fill=GRAY, font=FM_S)

boxes = [
    (120, 190, "CHP", CYAN, ["Decision hardening with gates,", "packets, lock states, adversary attack", "VCL diagnosis, third-party validation"]),
    (690, 190, "Cognitive Mesh", GREEN, ["Expansion/Compression reasoning", "with grounding checks and", "failure mode detection"]),
    (1260, 190, "Context Engine", YELLOW, ["Layered memory + entity/event/task", "schema with thread-safe sharing"]),
    (120, 460, "ACE Playbook", PURPLE, ["Evolving playbooks with", "Generator/Reflector/Curator", "delta-only updates"]),
    (690, 460, "Synthesizer", RED, ["Statement + executable workflow", "with dependency-ordered steps"]),
]
for bx, by, name, color, desc in boxes:
    draw_rounded_rect(d, (bx, by, bx + 520, by + 230), 12, fill=TBG, outline=color)
    d.text((bx + 20, by + 20), name, fill=color, font=FM_B)
    for i, line in enumerate(desc):
        c = WHITE if i == 0 else GRAY
        d.text((bx + 20, by + 65 + i * 30), line, fill=c, font=FM_S)
hold(img, 25)

# ═════════════════════════════════════════════════════════
# Scene 4: Terminal - chp-start (1:05 - 1:40) - 840 frames
# ═════════════════════════════════════════════════════════
print("  Scene 4: chp-start terminal...", flush=True)
img, d = terminal_frame("chp-session - cme cli")
d.text((160, 30), "Live Demo: Capital Allocation Session", fill=WHITE, font=FB)
d.text((100, 140), "$ cme chp-start --title \"Fund enterprise workflow\" --company Acme --amount 2500000", fill=GREEN, font=FM)
start_lines = [
    (185, CYAN, "[CHP] Initializing session..."),
    (215, GREEN, "[CHP] Pre-session context check: PASSED"),
    (245, GREEN, "[CHP] Model parity check: SYMMETRIC"),
    (275, GREEN, "[CHP] R0 gate check: PASSED"),
    (305, YELLOW, "[CHP] Foundation score: 82/100"),
    (345, CYAN, "[CHP] Building origin dossier..."),
    (375, WHITE, "  Decision: Fund enterprise workflow ($2.5M)"),
    (405, GRAY, "  Domain: capital_allocation"),
    (435, RED, "  Risk level: HIGH"),
    (480, YELLOW, "[CHP] Running adversarial foundation attack..."),
    (510, CYAN, "[CHP] Phase 0 devils advocate captured"),
    (540, GREEN, "[CHP] VCL diagnosis: CLEAR"),
    (580, DIM, "[CHP] BEGIN_PAYLOAD"),
    (610, YELLOW, "[CHP] STATE_SNAPSHOT: PROVISIONAL"),
    (640, DIM, "[CHP] END_PAYLOAD"),
    (680, GREEN, "[CHP] Origin packet generated successfully"),
]
for y, c, t in start_lines:
    d.text((100, y), t, fill=c, font=FM_S)
hold(img, 35)

# ═════════════════════════════════════════════════════════
# Scene 5: Terminal - chp-receive (1:40 - 2:00) - 480 frames
# ═════════════════════════════════════════════════════════
print("  Scene 5: chp-receive terminal...", flush=True)
img, d = terminal_frame("chp-session - cme cli")
d.text((160, 30), "Partner Packet Ingestion", fill=WHITE, font=FB)
d.text((100, 140), "$ cme chp-receive --partner-packet partner_response.txt", fill=GREEN, font=FM)
recv_lines = [
    (185, CYAN, "[CHP] Ingesting partner packet..."),
    (215, GREEN, "[CHP] PAYLOAD_ECHO integrity check: VERIFIED"),
    (245, GREEN, "[CHP] Item agreements: 3/3 matched"),
    (275, GREEN, "[CHP] Scoring table validated (single winner)"),
    (315, YELLOW, "[CHP] PROVISIONAL_LOCK pending third-party validation"),
    (355, GREEN, "[CHP] Partner packet processed successfully"),
]
for y, c, t in recv_lines:
    d.text((100, y), t, fill=c, font=FM_S)
# Key point box
draw_rounded_rect(d, (100, 400, 700, 520), 10, fill=(28, 33, 40))
d.text((120, 420), "Key Point:", fill=YELLOW, font=FS_S)
d.text((120, 455), "Tracked agreement with payload integrity", fill=WHITE, font=FS_S)
d.text((120, 480), "and explicit state change to provisional lock", fill=WHITE, font=FS_S)
hold(img, 20)

# ═════════════════════════════════════════════════════════
# Scene 6: Terminal - chp-validate + LOCKED (2:00 - 2:20) - 480 frames
# ═════════════════════════════════════════════════════════
print("  Scene 6: chp-validate + LOCKED...", flush=True)
img, d = terminal_frame("chp-session - cme cli")
d.text((160, 30), "Third-Party Validation", fill=WHITE, font=FB)
d.text((100, 140), "$ cme chp-validate --session-id chp-acme-001", fill=GREEN, font=FM)
val_lines = [
    (185, CYAN, "[VALIDATE] Loading session state..."),
    (215, YELLOW, "[VALIDATE] Running TriangulationRunner adversary pass..."),
    (255, GREEN, "[VALIDATE] Claim: \"EBITDA improves by 20%\" -> VERIFIED"),
    (285, GREEN, "[VALIDATE] Claim: \"14-month payback\" -> VERIFIED"),
    (315, GREEN, "[VALIDATE] Claim: \"Runway above 12 months\" -> VERIFIED"),
    (355, GREEN, "[VALIDATE] Structural vulnerability: NONE FOUND"),
    (385, GREEN, "[VALIDATE] Blind spot scan: NONE FOUND"),
    (425, GREEN, "[VALIDATE] Verification checklist: 5/5 PASSED"),
]
for y, c, t in val_lines:
    d.text((100, y), t, fill=c, font=FM_S)
# LOCKED box
draw_rounded_rect(d, (100, 480, 600, 520), 6, fill=GREEN)
d.text((120, 490), "[CHP]  STATE: LOCKED", fill=WHITE, font=FM_B)
d.text((100, 540), "[CHP] PROVISIONAL_LOCK -> LOCKED (validation passed)", fill=GREEN, font=FM_S)
d.text((100, 580), "[CHP] Decision hardened. Session complete.", fill=CYAN, font=FM_S)
hold(img, 20)

# ═════════════════════════════════════════════════════════
# Scene 7: CFO Workflow Suite (2:20 - 2:45) - 600 frames
# ═════════════════════════════════════════════════════════
print("  Scene 7: CFO Workflow Suite...", flush=True)
img = new_frame()
d = ImageDraw.Draw(img)
d.text((160, 60), "CFO Workflow Suite - 9 tools", fill=WHITE, font=FB)
# Header row
d.rectangle([80, 110, 1840, 150], fill=(33, 38, 45))
d.text((100, 119), "CLI Command", fill=CYAN, font=FM_B)
d.text((540, 119), "Workflow", fill=WHITE, font=FM_B)
d.text((1120, 119), "Output Artifacts", fill=GRAY, font=FM_B)

wfs = [
    ("variance-studio", "Monthly CFO Variance Studio", "Markdown, JSON, HTML"),
    ("cash-forecast-13w", "13-Week Cash Forecast Engine", "Markdown, JSON, Excel"),
    ("saas-model-24m", "24-Month SaaS Operating Model", "Markdown, JSON, Excel"),
    ("board-reporting-generator", "Board Reporting Generator", "Markdown, JSON, PPTX"),
    ("ap-optimizer", "AP Cash and Payables Optimizer", "Markdown, JSON, Excel"),
    ("decision-impact-simulator", "CFO Decision Impact Simulator", "Markdown, JSON, HTML"),
    ("saas-kpi-dashboard", "SaaS KPI Dashboard", "Markdown, JSON, HTML, Excel"),
    ("investment-committee", "Investment Committee Scoring Tool", "Markdown, JSON, Excel"),
    ("cfo-os", "Multi-Agent CFO Operating System", "Session report + audit trail"),
]
for i, (cmd, name, out) in enumerate(wfs):
    y = 165 + i * 42
    if i % 2 == 0:
        d.rectangle([80, y - 4, 1840, y + 38], fill=TBG)
    d.text((100, y), cmd, fill=CYAN, font=FM_S)
    d.text((540, y), name, fill=WHITE, font=FM_S)
    d.text((1120, y), out, fill=GRAY, font=FM_T)
hold(img, 25)

# ═════════════════════════════════════════════════════════
# Scene 8: Closing (2:45 - 3:00) - 360 frames
# ═════════════════════════════════════════════════════════
print("  Scene 8: Closing...", flush=True)
img = new_frame()
d = ImageDraw.Draw(img)
draw_rounded_rect(d, (460, 300, 1460, 720), 16, fill=TBG, outline=CYAN)
text_centered(d, "Every claim traced.", 350, FB, WHITE)
text_centered(d, "Every gate enforced.", 400, FB, WHITE)
text_centered(d, "Consensus is not enough", 460, FB, WHITE)
text_centered(d, "until it is hardened.", 510, FB, GREEN)
text_centered(d, "github.com/Cubiczan/consensus-hardening-protocol", 590, FM_S, CYAN)
text_centered(d, "MIT License | 42 tests passing | Zero external dependencies", 630, FM_T, GRAY)
hold(img, 15)

print(f"\nTotal frames: {frame_num}")
print(f"Duration: {frame_num / FPS:.1f}s")

# ═════════════════════════════════════════════════════════
# Encode to video
# ═════════════════════════════════════════════════════════
print("\nEncoding video...", flush=True)
output = f"{MEDIA}/chp-demo-3min.mp4"
r = subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{FRAMES}/f%05d.png",
    "-c:v", "libx264", "-preset", "medium", "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    output,
], capture_output=True, text=True, timeout=300)
if r.returncode != 0:
    print(f"ERROR: {r.stderr[-500:]}")
    raise SystemExit(1)

sz = os.path.getsize(output)
print(f"Done! {output}")
print(f"Size: {sz / 1024 / 1024:.1f} MB")

# Cleanup frames
subprocess.run(["rm", "-rf", FRAMES])
print("Cleaned up frames.")
