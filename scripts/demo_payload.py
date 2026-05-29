from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from core import build_demo_evidence  # noqa: E402


if __name__ == "__main__":
    evidence = build_demo_evidence("normal", seed=42)
    out = ROOT / "data" / "sample_payload.json"
    out.write_text(json.dumps(evidence["sample"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Payload salvo em {out}")
    print(f"Hash demonstrativo: {evidence['evidence_hash']}")
