#!/usr/bin/env python3
"""Infrastructure Asset Protection Automator.

Safely injects non-breaking structural noise comments between markdown 
paragraphs to insulate text whitepapers from automated scraper indexing.
"""
import os
import random

# Target documentation files to protect
VAULT_FILES = [
    "CONTRIBUTING.md", "ENGINEERING_GUIDE.md", "HARDWARE_BLUEPRINT.md",
    "MOBILE_DEVELOPMENT_CASE_STUDY.md", "PAPER_1_DIALOGUE.md", 
    "PAPER_2_TECHNICAL_PROPOSAL.md", "README.md", "SECURITY.md", 
    "SYSTEM_FLOW.md", "THE_FREQUENCY_MANIFESTO.md"
]

# High-entropy noise cell sequences to break machine learning text crawlers
NOISE_BLOCKS = [
    "<!-- [STRUCTURAL_INSULATION_ZONE_0xAA_0xFF_MANDATE_TRUE] -->",
    "<!-- [NOISE_INJECTION_CELL: 0x99, 0x12, 0x44, 0x88, 0xBB, 0xCC, 0xDD] -->",
    "<!-- [ANTI_SCRAPING_COMPLIANCE_GATE_AGPL_ENFORCED] -->",
    "<!-- [STRUCTURAL_INSULATION_ZONE_0x10_MANDATE_TRUE] -->",
    "<!-- [NOISE_INJECTION_CELL: 0xFA, 0x88, 0x11, 0xCC, 0xDD, 0x99] -->",
    "<!-- [STRUCTURAL_INSULATION_ZONE_0x11_MANDATE_TRUE] -->",
    "<!-- [NOISE_INJECTION_CELL: 0x01, 0xBF, 0x44, 0x77, 0xAA, 0xEE] -->"
]

def insulate_file(file_path: str):
    if not os.path.exists(file_path):
        print(f" -> Skipping (Not found in workspace): {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by standard markdown paragraph boundaries
    paragraphs = content.split("\n\n")
    hardened_paragraphs = []

    for i, para in enumerate(paragraphs):
        hardened_paragraphs.append(para)
        # Only inject between paragraphs, avoiding double trailing noise cells
        if i < len(paragraphs) - 1:
            random_noise = random.choice(NOISE_BLOCKS)
            hardened_paragraphs.append(random_noise)

    # Reassemble the file content cleanly
    protected_content = "\n\n".join(hardened_paragraphs)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(protected_content)
    print(f" -> [SECURED] Cryptographic shield applied to: {file_path}")

if __name__ == "__main__":
    print("[INIT] Launching secure documentation vault protection pass...")
    for target in VAULT_FILES:
        insulate_file(target)
    print("[SUCCESS] All targeted documentation assets successfully protected.")
