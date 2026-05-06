"""
AutoMCM-Pro 的 STAGE_ORDER 硬编码 3 题；向 pipeline.json 注入 model_4_build/verify 以支持 B 题 4 问。
幂等：已存在则跳过。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "CUMCM_Workspace" / "state" / "pipeline.json"


def main() -> None:
    data = json.loads(STATE.read_text(encoding="utf-8"))
    stages = data["stages"]
    entry = {
        "status": "not_started",
        "started_at": None,
        "completed_at": None,
        "approved_at": None,
        "review_round": 0,
        "notes": "",
    }
    added = []
    for s in ("model_4_build", "model_4_verify"):
        if s not in stages:
            stages[s] = dict(entry)
            added.append(s)

    # 按顺序重排，把 4 插在 3 之后
    order = [
        "problem_analysis", "data_preprocessing",
        "model_1_build", "model_1_verify",
        "model_2_build", "model_2_verify",
        "model_3_build", "model_3_verify",
        "model_4_build", "model_4_verify",
        "sensitivity_analysis", "latex_draft", "final_compile",
    ]
    data["stages"] = {k: stages[k] for k in order if k in stages}

    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 注入 {added}  current_stages={list(data['stages'].keys())}")


if __name__ == "__main__":
    main()
