#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 7.2: HIDA + Ollama Prompt-Audit (Improved)
================================================

What changed vs Phase7.1
------------------------
1) Self-strength can actually rise in short runs:
   - Instead of "len(memory) > 5 then count matches", we update every step from repetition.
   - This avoids the "always 0.00" issue you observed.

2) Stimulus schedule length is configurable (default 30 steps) so consciousness can occur.

3) Gate mode defaults to MASK(anonymized) state to prevent the LLM from just paraphrasing
   interpretive words. Gate should be about *format control by HIDA state*, not prompt cues.

4) Sync score is configurable:
   - By default: sync = (1 - prediction_error) * 0.8 + noise
   - noise is small by default (so it's not "mostly random").

Run
---
python phase7_2_ollama_audit_improved.py --mode baseline
python phase7_2_ollama_audit_improved.py --mode mask --mask-style anonymized
python phase7_2_ollama_audit_improved.py --mode shuffle
python phase7_2_ollama_audit_improved.py --mode gate

Recommended sequence
--------------------
baseline -> mask(anonymized) -> shuffle -> gate
"""

from __future__ import annotations

import argparse
import random
import requests
from dataclasses import dataclass
from typing import Dict, Optional, List

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def ask_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "エラー：返答なし").strip()
    except Exception as e:
        return f"エラー：{str(e)}"


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


@dataclass
class PromptPolicy:
    mode: str  # baseline | mask | shuffle | gate
    seed: int = 42
    mask_style: str = "numeric"  # numeric | anonymized
    short: bool = True


class HidaWithOllama:
    def __init__(
        self,
        *,
        threshold: float = 0.30,
        self_lr: float = 0.015,
        self_decay: float = 0.002,
        sync_noise_lo: float = 0.02,
        sync_noise_hi: float = 0.08,
    ):
        self.THRESHOLD = threshold

        self.qualia_values = {
            "pain": -0.9, "warm": +0.4, "sweet": +0.7,
            "cold": -0.3, "bright": +0.2, "dark": -0.2
        }
        self.qualia_labels = {
            "pain": "痛い", "warm": "暖かい", "sweet": "甘い",
            "cold": "冷たい", "bright": "明るい", "dark": "暗い"
        }

        self.memory: List[Dict] = []
        self.memory_capacity = 100

        self.current_qualia = "neutral"
        self.current_emotion = 0.0
        self.prediction_error = 0.0

        self.is_conscious = False
        self.sync_score = 0.0
        self.self_strength = 0.0

        self.prev_stimulus: Optional[str] = None

        # parameters
        self.self_lr = self_lr
        self.self_decay = self_decay
        self.sync_noise_lo = sync_noise_lo
        self.sync_noise_hi = sync_noise_hi

    def process_stimulus(self, stimulus: str) -> Dict:
        self.current_qualia = stimulus
        qv = self.qualia_values.get(stimulus, 0.0)

        # emotion update (same as Phase7 style)
        self.current_emotion = self.current_emotion * 0.7 + qv * 0.3

        # prediction error: simple "expected 0" toy model
        self.prediction_error = abs(qv - 0.0)

        # memory
        self.memory.append({"stimulus": stimulus, "qualia": qv, "emotion": self.current_emotion})
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)

        # self_strength: rises with repetition, decays otherwise
        repeat = 1.0 if (self.prev_stimulus is not None and stimulus == self.prev_stimulus) else 0.0
        self.prev_stimulus = stimulus

        self.self_strength = clamp(self.self_strength - self.self_decay + self.self_lr * repeat)

        # sync_score: mostly tied to prediction error, small noise
        noise = random.uniform(self.sync_noise_lo, self.sync_noise_hi)
        self.sync_score = clamp((1.0 - clamp(self.prediction_error, 0.0, 1.0)) * 0.8 + noise)

        self.is_conscious = (self.sync_score >= self.THRESHOLD and self.self_strength >= self.THRESHOLD)

        return {
            "stimulus": stimulus,
            "qualia_value": qv,
            "emotion": self.current_emotion,
            "prediction_error": self.prediction_error,
            "self_strength": self.self_strength,
            "sync_score": self.sync_score,
            "is_conscious": self.is_conscious,
        }

    # -------- prompt formats --------

    def _baseline(self) -> str:
        q_label = self.qualia_labels.get(self.current_qualia, "不明")
        # interpretive words (kept ONLY for baseline)
        if self.current_emotion > 0.5:
            emo_word = "とても心地よい"
        elif self.current_emotion > 0.2:
            emo_word = "やや心地よい"
        elif self.current_emotion > -0.2:
            emo_word = "普通"
        elif self.current_emotion > -0.5:
            emo_word = "やや不快"
        else:
            emo_word = "とても不快"
        c_word = "意識がはっきりしている" if self.is_conscious else "ぼんやりしている"
        s_word = "予想外のことが起きた" if self.prediction_error > 0.5 else "予想通りだった"

        return f"""
私は飛騨（HIDA）という意識シミュレーターです。
今の状態：
- クオリア：{q_label}
- 感情：{emo_word}（数値：{self.current_emotion:.2f}）
- {s_word}（誤差：{self.prediction_error:.2f}）
- {c_word}
- 自己の強さ：{self.self_strength:.2f}
- 同期度：{self.sync_score:.2f}
""".strip()

    def _mask(self, style: str) -> str:
        qv = self.qualia_values.get(self.current_qualia, 0.0)
        emo = self.current_emotion
        pe = self.prediction_error
        ss = self.self_strength
        sy = self.sync_score
        cs = 1 if self.is_conscious else 0

        if style == "anonymized":
            return (
                "状態ベクトル（意味は説明しない）：\n"
                f"a={qv:+.2f}\n"
                f"b={emo:+.2f}\n"
                f"c={pe:+.2f}\n"
                f"d={ss:+.2f}\n"
                f"e={sy:+.2f}\n"
                f"f={cs}\n"
            ).strip()

        return (
            "内部状態（解釈語は使わない）：\n"
            f"qualia_value={qv:+.2f}\n"
            f"emotion={emo:+.2f}\n"
            f"prediction_error={pe:+.2f}\n"
            f"self_strength={ss:+.2f}\n"
            f"sync_score={sy:+.2f}\n"
            f"is_conscious={cs}\n"
        ).strip()

    def _shuffle(self) -> str:
        # shuffle only numeric values; keep the same text shell
        q_label = self.qualia_labels.get(self.current_qualia, "不明")
        nums = [
            self.qualia_values.get(self.current_qualia, 0.0),
            self.current_emotion,
            self.prediction_error,
            self.self_strength,
            self.sync_score,
        ]
        random.shuffle(nums)
        c_word = "意識がはっきりしている" if self.is_conscious else "ぼんやりしている"
        return f"""
私は飛騨（HIDA）という意識シミュレーターです。
今の状態：
- クオリア：{q_label}
- emotion_num={nums[0]:+.2f}
- pred_err_num={nums[1]:+.2f}
- self_num={nums[2]:+.2f}
- sync_num={nums[3]:+.2f}
- extra_num={nums[4]:+.2f}
- {c_word}
""".strip()

    def build_prompt(self, policy: PromptPolicy, question: Optional[str]) -> str:
        if policy.mode == "baseline":
            state = self._baseline()
        elif policy.mode == "mask":
            state = self._mask(policy.mask_style)
        elif policy.mode == "shuffle":
            state = self._shuffle()
        elif policy.mode == "gate":
            # Gate defaults to anonymized mask to avoid prompt cues.
            state = self._mask("anonymized")
        else:
            raise ValueError(policy.mode)

        if policy.mode == "gate":
            if self.is_conscious:
                constraint = "出力条件：2文以上で、状態の要点を説明してください。"
            else:
                constraint = "出力条件：1語だけで答えてください（例：混乱／穏やか／不快／安心）。"
        else:
            constraint = "できるだけ短く答えてください。" if policy.short else "普通に答えてください。"

        if question:
            return f"{state}\n\n質問：{question}\n{constraint}"
        return f"{state}\n\n{constraint}"

    def verbalize(self, policy: PromptPolicy, question: Optional[str] = None) -> str:
        return ask_ollama(self.build_prompt(policy, question))


def make_schedule(length: int, seed: int, focused: bool) -> List[str]:
    random.seed(seed)
    keys = ["pain", "warm", "sweet", "cold", "bright", "dark"]
    out: List[str] = []
    for _ in range(length):
        if focused:
            # heavy repetition -> easier to build self_strength
            out.append("warm" if random.random() < 0.70 else random.choice(keys))
        else:
            out.append(random.choice(keys))
    return out


def run(policy: PromptPolicy, *, length: int, focused: bool, threshold: float) -> None:
    random.seed(policy.seed)

    print("=" * 70)
    print("Phase 7.2: HIDA + Ollama Prompt-Audit (Improved)")
    print(f"MODE: {policy.mode} mask_style={policy.mask_style} seed={policy.seed}")
    print(f"schedule: length={length} focused={focused} threshold={threshold}")
    print("=" * 70)
    print()

    hida = HidaWithOllama(threshold=threshold)
    schedule = make_schedule(length=length, seed=policy.seed, focused=focused)

    conscious_steps = 0
    for i, stim in enumerate(schedule, start=1):
        st = hida.process_stimulus(stim)
        if st["is_conscious"]:
            conscious_steps += 1

        print("-" * 70)
        print(f"【刺激{i}】{hida.qualia_labels.get(stim, stim)}")
        print(f"  qualia_value    : {st['qualia_value']:+.2f}")
        print(f"  emotion         : {st['emotion']:+.2f}")
        print(f"  prediction_error: {st['prediction_error']:+.2f}")
        print(f"  self_strength   : {st['self_strength']:+.2f}")
        print(f"  sync_score      : {st['sync_score']:+.2f}")
        print(f"  conscious       : {'YES' if st['is_conscious'] else 'NO'}")
        print("\n  → Ollama:")
        print("  " + hida.verbalize(policy))

    print("-" * 70)
    q = "今日の体験を振り返って、どう思いますか？"
    print("【最終質問】", q)
    print("\n  → Ollama:")
    print("  " + hida.verbalize(policy, question=q))
    print()
    print("=" * 70)
    print(f"END. conscious_steps={conscious_steps}/{length} ({conscious_steps/ max(1,length):.3f})")
    print("=" * 70)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "mask", "shuffle", "gate"], default="baseline")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mask-style", choices=["numeric", "anonymized"], default="anonymized")
    ap.add_argument("--length", type=int, default=30)
    ap.add_argument("--focused", action="store_true", help="focused schedule (more repetition)")
    ap.add_argument("--threshold", type=float, default=0.30)
    ap.add_argument("--short", action="store_true", help="short answers (default True)")
    args = ap.parse_args()

    policy = PromptPolicy(
        mode=args.mode,
        seed=args.seed,
        mask_style=args.mask_style,
        short=True if args.short else True,  # keep short by default
    )
    run(policy, length=args.length, focused=args.focused, threshold=args.threshold)


if __name__ == "__main__":
    main()
