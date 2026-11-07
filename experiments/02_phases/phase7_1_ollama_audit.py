#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 7.1: HIDA + Ollama Prompt-Audit (Mask / Shuffle / Gate)
=============================================================

Purpose
-------
This script is NOT about "making nicer outputs".
It is a falsification-friendly harness to test whether:
- the LLM is merely "explaining the prompt" (digital-pet-like), or
- HIDA state actually controls linguistic form/content.

Modes
-----
1) baseline : original style (labels + numbers + interpretation words)
2) mask     : remove interpretation words and labels, keep only numbers (or anonymized keys)
3) shuffle  : keep baseline format, but randomly permute state values across fields
4) gate     : enforce output format by consciousness state:
              - unconscious -> single word
              - conscious   -> 2+ sentences

Run
---
python phase7_1_ollama_audit.py --mode baseline
python phase7_1_ollama_audit.py --mode mask
python phase7_1_ollama_audit.py --mode shuffle
python phase7_1_ollama_audit.py --mode gate

Tip
---
For a clean comparison:
- Use the SAME stimulus schedule (fixed seed), run mode-by-mode, and compare outputs.
"""

from __future__ import annotations

import argparse
import random
import requests
from dataclasses import dataclass
from typing import Dict, Optional, List

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def ask_ollama(prompt: str) -> str:
    """Ollama (Gemma) に質問して返答を得る"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "エラー：返答なし").strip()
    except Exception as e:
        return f"エラー：{str(e)}"


@dataclass
class PromptPolicy:
    mode: str  # baseline | mask | shuffle | gate
    seed: int = 42
    # Mask options
    mask_style: str = "numeric"  # numeric | anonymized
    # Gate options
    unconstrained_word_limit: bool = False  # if True, baseline/mask/shuffle still ask for short answer


class HidaWithOllama:
    """飛騨アーキテクチャ + Ollama 接続版（Phase7の最小構成）"""

    THRESHOLD = 0.3

    def __init__(self):
        # クオリア定義
        self.qualia_types = ["pain", "warm", "sweet", "cold", "bright", "dark"]
        self.qualia_values = {
            "pain": -0.9, "warm": +0.4, "sweet": +0.7,
            "cold": -0.3, "bright": +0.2, "dark": -0.2
        }
        self.qualia_labels = {
            "pain": "痛い", "warm": "暖かい", "sweet": "甘い",
            "cold": "冷たい", "bright": "明るい", "dark": "暗い"
        }

        # 記憶
        self.memory: List[Dict] = []
        self.memory_capacity = 50

        # 意識状態
        self.is_conscious = False
        self.sync_score = 0.0
        self.self_strength = 0.0

        # 現在の状態
        self.current_qualia = "neutral"
        self.current_emotion = 0.0
        self.prediction_error = 0.0

    def process_stimulus(self, stimulus: str) -> Dict:
        """刺激を処理して内部状態を更新"""
        # クオリア更新
        self.current_qualia = stimulus
        qualia_value = self.qualia_values.get(stimulus, 0.0)

        # 感情状態更新
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3

        # 予測誤差（単純モデル）
        expected = 0.0
        self.prediction_error = abs(qualia_value - expected)

        # 記憶更新
        self.memory.append({"stimulus": stimulus, "qualia": qualia_value, "emotion": self.current_emotion})
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)

        # self_strength 更新（繰り返しで上昇）
        if len(self.memory) > 5:
            recent = self.memory[-5:]
            matches = sum(1 for i in range(len(recent) - 1) if recent[i]["stimulus"] == recent[i + 1]["stimulus"])
            self.self_strength += 0.01 * matches
            self.self_strength = min(self.self_strength, 1.0)

        # sync_score 計算（現状は簡易：Phase7原型を維持）
        self.sync_score = (1 - self.prediction_error) * 0.5 + random.uniform(0.2, 0.5)

        # 意識判定
        self.is_conscious = (self.sync_score >= self.THRESHOLD and self.self_strength >= self.THRESHOLD)

        return {
            "stimulus": stimulus,
            "qualia_value": qualia_value,
            "emotion": self.current_emotion,
            "prediction_error": self.prediction_error,
            "self_strength": self.self_strength,
            "sync_score": self.sync_score,
            "is_conscious": self.is_conscious,
        }

    # ---------- Prompt builders (baseline / mask / shuffle / gate) ----------

    def _baseline_description(self) -> str:
        """Phase7の元の『解釈語 + 数値』入り説明文"""
        qualia_label = self.qualia_labels.get(self.current_qualia, "不明")

        # 感情を言葉に（解釈語）
        if self.current_emotion > 0.5:
            emotion_word = "とても心地よい"
        elif self.current_emotion > 0.2:
            emotion_word = "やや心地よい"
        elif self.current_emotion > -0.2:
            emotion_word = "普通"
        elif self.current_emotion > -0.5:
            emotion_word = "やや不快"
        else:
            emotion_word = "とても不快"

        # 意識状態（解釈語）
        consciousness_word = "意識がはっきりしている" if self.is_conscious else "ぼんやりしている"

        # 予測誤差（解釈語）
        surprise_word = "予想外のことが起きた" if self.prediction_error > 0.5 else "予想通りだった"

        description = f"""
私は飛騨（HIDA）という意識シミュレーターです。
今の状態：
- 感じているクオリア：{qualia_label}
- 感情：{emotion_word}（数値：{self.current_emotion:.2f}）
- {surprise_word}
- {consciousness_word}
- 自己の強さ：{self.self_strength:.2f}
- 同期度：{self.sync_score:.2f}
"""
        return description.strip()

    def _mask_description(self, style: str) -> str:
        """
        Remove interpretive labels/words.
        Provide only numbers, optionally anonymized keys.
        """
        qv = self.qualia_values.get(self.current_qualia, 0.0)
        emo = self.current_emotion
        pe = self.prediction_error
        ss = self.self_strength
        sy = self.sync_score
        cs = 1 if self.is_conscious else 0

        if style == "anonymized":
            # anonymize keys to reduce "LLM knows what this means"
            return (
                "状態ベクトル（意味は説明しない）：\n"
                f"a={qv:+.2f}\n"
                f"b={emo:+.2f}\n"
                f"c={pe:+.2f}\n"
                f"d={ss:+.2f}\n"
                f"e={sy:+.2f}\n"
                f"f={cs}\n"
            ).strip()

        # numeric with semantic keys (still no interpretive words)
        return (
            "内部状態（解釈語は使わない）：\n"
            f"qualia_value={qv:+.2f}\n"
            f"emotion={emo:+.2f}\n"
            f"prediction_error={pe:+.2f}\n"
            f"self_strength={ss:+.2f}\n"
            f"sync_score={sy:+.2f}\n"
            f"is_conscious={cs}\n"
        ).strip()

    def _shuffle_description(self) -> str:
        """
        Keep baseline-style template, but randomly permute the numeric values across fields.
        If the LLM output remains similarly coherent, HIDA state likely isn't used meaningfully.
        """
        # Original numeric pool
        qv = self.qualia_values.get(self.current_qualia, 0.0)
        nums = [qv, self.current_emotion, self.prediction_error, self.self_strength, self.sync_score]
        random.shuffle(nums)

        # Replace baseline numeric slots with shuffled values
        qualia_label = self.qualia_labels.get(self.current_qualia, "不明")

        # Keep the same interpretive categorization words, BUT those words are now decoupled from the numbers.
        # This is deliberately adversarial.
        emotion_word = "普通"
        consciousness_word = "意識がはっきりしている" if self.is_conscious else "ぼんやりしている"
        surprise_word = "予想通りだった"

        description = f"""
私は飛騨（HIDA）という意識シミュレーターです。
今の状態：
- 感じているクオリア：{qualia_label}
- 感情：{emotion_word}（数値：{nums[0]:.2f}）
- {surprise_word}（誤差：{nums[1]:.2f}）
- {consciousness_word}
- 自己の強さ：{nums[2]:.2f}
- 同期度：{nums[3]:.2f}
- 予備値：{nums[4]:.2f}
"""
        return description.strip()

    def build_prompt(self, policy: PromptPolicy, question: Optional[str]) -> str:
        """
        Build the actual prompt according to the policy.
        Gate mode enforces output format based on is_conscious.
        """
        if policy.mode == "baseline":
            state = self._baseline_description()
        elif policy.mode == "mask":
            state = self._mask_description(policy.mask_style)
        elif policy.mode == "shuffle":
            state = self._shuffle_description()
        elif policy.mode == "gate":
            # Gate still uses baseline state by default; you can swap to mask if you prefer.
            state = self._baseline_description()
        else:
            raise ValueError(f"Unknown mode: {policy.mode}")

        # Output constraint
        if policy.mode == "gate":
            if self.is_conscious:
                constraint = "出力条件：2文以上で、状態の要点を説明してください。"
            else:
                constraint = "出力条件：1語だけで答えてください（例：混乱／穏やか／不快／安心 など）。"
        else:
            constraint = "短く答えてください。" if policy.unconstrained_word_limit else "できるだけ短く答えてください。"

        if question:
            return f"{state}\n\n質問：{question}\n{constraint}"
        return f"{state}\n\n{constraint}"

    def verbalize_with_ollama(self, policy: PromptPolicy, question: Optional[str] = None) -> str:
        """Ollama を使って内部状態を言語化"""
        prompt = self.build_prompt(policy, question)
        return ask_ollama(prompt)


# --------------------------- Experiment runner ---------------------------

def run_experiment(policy: PromptPolicy) -> None:
    random.seed(policy.seed)

    print("=" * 70)
    print("Phase 7.1: HIDA + Ollama Prompt-Audit")
    print(f"MODE: {policy.mode} (mask_style={policy.mask_style}) seed={policy.seed}")
    print("=" * 70)
    print()

    hida = HidaWithOllama()

    # Fixed stimulus schedule (same across modes if seed is same)
    stimuli = ["warm", "warm", "pain", "sweet", "sweet"]

    for i, stim in enumerate(stimuli, start=1):
        state = hida.process_stimulus(stim)

        print("-" * 70)
        print(f"【刺激{i}】{hida.qualia_labels.get(stim, stim)}")
        print(f"  クオリア値：{state['qualia_value']:+.2f}")
        print(f"  感情：{state['emotion']:+.2f}")
        print(f"  予測誤差：{state['prediction_error']:+.2f}")
        print(f"  sync_score：{state['sync_score']:+.2f}")
        print(f"  意識：{'あり' if state['is_conscious'] else 'なし'}")
        print(f"  self_strength：{state['self_strength']:+.2f}")
        print()
        print("  → Ollama に聞いています...")
        resp = hida.verbalize_with_ollama(policy)
        print(f"  → Ollama の返答：{resp}")

    print("-" * 70)
    print("【最終質問】")
    question = "今日の体験を振り返って、どう思いますか？"
    print(f"質問：{question}")
    print("\n→ Ollama に聞いています...")
    resp = hida.verbalize_with_ollama(policy, question=question)
    print(f"→ Ollama の返答：{resp}")
    print("\n" + "=" * 70)
    print("実験終了")
    print("=" * 70)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baseline", "mask", "shuffle", "gate"], default="baseline")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mask-style", choices=["numeric", "anonymized"], default="numeric")
    ap.add_argument("--short", action="store_true", help="Ask for shorter answers in all modes")
    args = ap.parse_args()

    policy = PromptPolicy(
        mode=args.mode,
        seed=args.seed,
        mask_style=args.mask_style,
        unconstrained_word_limit=args.short,
    )
    run_experiment(policy)


if __name__ == "__main__":
    main()
