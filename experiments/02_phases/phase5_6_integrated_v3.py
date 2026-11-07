#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5.1/6 Integrated: Consciousness + Memory Reconstruction
Phase5（意識の間欠性）に Phase6（記憶再構成）を統合した“次の一段”の実装。

狙い（完成度を一段上げる点）:
1) Phase6を Phase5 のメインループへ統合（記憶が同期・自己・意識に影響）
2) 同期に「記憶ミスマッチ」を導入（簡易だがノイズ依存を下げる方向）
3) ロバスト性テスト（ノイズ量などを変えて指標がどう変わるか）

注意:
- これは理論の“本体統合”の第一版。同期の高度化（PLV/MI/Corr）は次段。
- 医療用途ではなく、計算モデル/研究用デモとして扱うこと。
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# -----------------------
# Phase6: Memory unit
# -----------------------
@dataclass
class Memory:
    pattern: str
    original_qualia: float
    original_emotion: float
    current_qualia: float = field(init=False)
    current_emotion: float = field(init=False)
    recall_count: int = 0
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        self.current_qualia = self.original_qualia
        self.current_emotion = self.original_emotion

    def reconstruct(self, current_state: Dict, integration_weight: float = 0.1) -> Dict:
        """
        Reconstruct memory based on current state.
        記憶は“取り出す”のではなく、“現在”を混ぜて再構成する。
        """
        self.recall_count += 1

        old_q = self.current_qualia
        old_e = self.current_emotion

        self.current_qualia = self.current_qualia * (1 - integration_weight) + current_state["qualia"] * integration_weight
        self.current_emotion = self.current_emotion * (1 - integration_weight) + current_state["emotion"] * integration_weight

        self.history.append({
            "n": self.recall_count,
            "state": dict(current_state),
            "dq": self.current_qualia - old_q,
            "de": self.current_emotion - old_e,
        })

        return {
            "original_qualia": self.original_qualia,
            "reconstructed_qualia": self.current_qualia,
            "original_emotion": self.original_emotion,
            "reconstructed_emotion": self.current_emotion,
            "drift_qualia": self.current_qualia - self.original_qualia,
            "drift_emotion": self.current_emotion - self.original_emotion,
            "recall_count": self.recall_count,
        }


# -----------------------
# Phase5: Consciousness system (with Phase6 integrated)
# -----------------------
class ConsciousnessSystemIntegrated:
    """
    Phase5の意識判定ループに Phase6の“記憶再構成”を接続した統合版。
    """

    def __init__(
        self,
        threshold: float = 0.3,
        memory_capacity: int = 200,
        integration_weight: float = 0.1,
        noise_max: float = 0.2,
        base_sync_weight: float = 0.7,
        mismatch_weight: float = 0.2,
        emotion_weight: float = 0.1,
        novelty_penalty: float = 0.0008,
        context_gain: float = 0.25,
        context_noise: float = 0.05,
        seed: Optional[int] = None,
    ):
        if seed is not None:
            random.seed(seed)

        self.THRESHOLD = threshold
        self.integration_weight = integration_weight

        # knobs for robustness sweeps
        self.noise_max = noise_max
        self.base_sync_weight = base_sync_weight
        self.mismatch_weight = mismatch_weight
        self.emotion_weight = emotion_weight
        self.novelty_penalty = novelty_penalty  # prediction error tends to fragment self
        self.context_gain = context_gain
        self.context_noise = context_noise

        # Expanded qualia
        self.qualia_types = [
            "pain", "warm", "cold", "sweet", "sour", "bitter",
            "red", "blue", "green", "loud", "quiet", "smooth"
        ]
        self.qualia_values = {
            "pain": -0.9, "warm": -0.2, "cold": -0.4,
            "sweet": +0.7, "sour": -0.3, "bitter": -0.6,
            "red": +0.3, "blue": +0.2, "green": +0.4,
            "loud": -0.5, "quiet": +0.3, "smooth": +0.5
        }

        # State
        self.step_count = 0
        self.memory_buffer: List[str] = []
        self.memory_capacity = memory_capacity

        self.self_strength = 0.0
        self.sync_score = 0.0
        self.is_conscious = False

        # Emotion state (new in integration)
        self.current_emotion = 0.0  # [-1, +1] drifted by stimuli

        # Memories by pattern (simple: 1 memory per stimulus)
        self.memories: Dict[str, Memory] = {}

        # Tracking
        self.sync_history: List[float] = []
        self.self_history: List[float] = []
        self.emotion_history: List[float] = []
        self.consciousness_history: List[int] = []
        self.recall_events: List[Dict] = []
        self.threshold_crossed_at: Optional[int] = None
        self.consciousness_count = 0

    # ---------- helpers ----------
    def _update_emotion(self, qualia_value: float):
        """Phase6系：現在感情は刺激の累積でドリフトする"""
        self.current_emotion = self.current_emotion * 0.7 + qualia_value * 0.3
        # clamp (simple)
        self.current_emotion = max(-1.0, min(1.0, self.current_emotion))

    def _ensure_memory(self, stimulus: str, qualia_value: float):
        if stimulus not in self.memories:
            # 初回作成時点の“感情コンテキスト”も保存
            self.memories[stimulus] = Memory(
                pattern=stimulus,
                original_qualia=qualia_value,
                original_emotion=self.current_emotion,
            )

    def _maybe_recall_and_reconstruct(self, stimulus: str, qualia_value: float, prediction_error: float) -> Tuple[Optional[Dict], float, float]:
        """
        記憶の呼び出し（再構成）を“同期/意識に関係しうるタイミング”で発火させる。
        ここでは簡易に「予測誤差が大きい」 or 「意識に入る直前」をトリガにする。
        """
        self._ensure_memory(stimulus, qualia_value)
        mem = self.memories[stimulus]

        # trigger policy
        trigger = (prediction_error >= 1.0) or (self.self_strength >= self.THRESHOLD and random.random() < 0.15)

        if not trigger:
            return None, qualia_value, 0.0

        # Contextualized "now" qualia: mood and noise slightly modulate interpretation
        # 文脈化された現在クオリア：気分（emotion）と微小ノイズが“感じ方”を揺らす
        now_qualia = qualia_value + self.context_gain * self.current_emotion + random.uniform(-self.context_noise, self.context_noise)
        current_state = {
            "qualia": now_qualia,
            "emotion": self.current_emotion,
            "self_strength": self.self_strength,
        }
        rec = mem.reconstruct(current_state, integration_weight=self.integration_weight)

        # memory mismatch: conflict between current sensation and reconstructed memory
        mismatch = min(1.0, abs(rec["reconstructed_qualia"] - qualia_value))

        # feed-back: "remembering changes what you feel now" (lightweight)
        effective_qualia = 0.6 * qualia_value + 0.4 * rec["reconstructed_qualia"]

        self.recall_events.append({
            "step": self.step_count,
            "stimulus": stimulus,
            "prediction_error": prediction_error,
            "mismatch": mismatch,
            "drift_qualia": rec["drift_qualia"],
            "drift_emotion": rec["drift_emotion"],
            "recall_count": rec["recall_count"],
        })
        return rec, effective_qualia, mismatch

    # ---------- main loop ----------
    def process_step(self, environment: str = "focused") -> Dict:
        self.step_count += 1

        # stimulus selection (same as Phase5)
        if environment == "focused":
            stimulus = random.choice(self.qualia_types[:3])
        else:
            stimulus = random.choice(self.qualia_types)

        qualia_value = self.qualia_values[stimulus]

        # update emotion first (so that “now” influences reconstruction)
        self._update_emotion(qualia_value)

        # short-term buffer (for prediction + pattern repetition)
        self.memory_buffer.append(stimulus)
        if len(self.memory_buffer) > self.memory_capacity:
            self.memory_buffer.pop(0)

        # prediction error (simple: repeat last)
        if len(self.memory_buffer) >= 2:
            prediction = self.memory_buffer[-2]
            prediction_error = 0.0 if prediction == stimulus else 1.0
        else:
            prediction = None
            prediction_error = 1.0

        # self_strength from repetition (Phase5)
        pattern_matches = 0
        if len(self.memory_buffer) >= 10:
            recent = self.memory_buffer[-10:]
            for i in range(len(recent) - 1):
                if recent[i] == recent[i + 1]:
                    pattern_matches += 1

        self.self_strength += 0.001 * pattern_matches
        # Novelty/overload penalty: frequent surprises weaken self-coherence
        # 新奇性（予測外の連続）は自己一貫性を弱める（分散環境でselfが育ちにくい理由）
        self.self_strength -= self.novelty_penalty * prediction_error
        self.self_strength = max(0.0, min(self.self_strength, 1.0))

        # recall & reconstruct (Phase6 integrated)
        rec, effective_qualia, mismatch = self._maybe_recall_and_reconstruct(stimulus, qualia_value, prediction_error)

        # sync score (improved: prediction_error + mismatch + emotion magnitude)
        base = prediction_error * self.base_sync_weight
        mismatch_term = mismatch * self.mismatch_weight
        emotion_term = abs(self.current_emotion) * self.emotion_weight
        noise = random.uniform(0.0, self.noise_max)

        self.sync_score = base + mismatch_term + emotion_term + noise
        self.sync_score = min(1.0, self.sync_score)

        # consciousness determination
        was_conscious = self.is_conscious
        self.is_conscious = (self.sync_score >= self.THRESHOLD and self.self_strength >= self.THRESHOLD)

        if self.is_conscious:
            self.consciousness_count += 1

        if self.is_conscious and not was_conscious and self.threshold_crossed_at is None:
            self.threshold_crossed_at = self.step_count

        # tracking
        self.sync_history.append(self.sync_score)
        self.self_history.append(self.self_strength)
        self.emotion_history.append(self.current_emotion)
        self.consciousness_history.append(1 if self.is_conscious else 0)

        return {
            "step": self.step_count,
            "stimulus": stimulus,
            "qualia": qualia_value,
            "effective_qualia": effective_qualia,
            "emotion": self.current_emotion,
            "prediction_error": prediction_error,
            "pattern_matches": pattern_matches,
            "self_strength": self.self_strength,
            "sync_score": self.sync_score,
            "mismatch": mismatch,
            "is_conscious": self.is_conscious,
            "recalled": rec is not None,
        }

    def run(self, steps: int = 10000, environment: str = "focused") -> Dict:
        for _ in range(steps):
            self.process_step(environment=environment)

        # stats
        cons_rate = self.consciousness_count / max(1, self.step_count)
        conscious_syncs = [s for s, c in zip(self.sync_history, self.consciousness_history) if c == 1]
        unconscious_syncs = [s for s, c in zip(self.sync_history, self.consciousness_history) if c == 0]
        avg_sync_c = statistics.mean(conscious_syncs) if conscious_syncs else 0.0
        avg_sync_u = statistics.mean(unconscious_syncs) if unconscious_syncs else 0.0

        # memory drift summary (only for recalled items)
        drifts_q = [e["drift_qualia"] for e in self.recall_events]
        drifts_e = [e["drift_emotion"] for e in self.recall_events]
        avg_dq = statistics.mean(drifts_q) if drifts_q else 0.0
        avg_de = statistics.mean(drifts_e) if drifts_e else 0.0

        return {
            "steps": self.step_count,
            "environment": environment,
            "consciousness_rate": cons_rate,
            "threshold_crossed_at": self.threshold_crossed_at,
            "avg_sync_conscious": avg_sync_c,
            "avg_sync_unconscious": avg_sync_u,
            "recall_events": len(self.recall_events),
            "avg_memory_drift_qualia": avg_dq,
            "avg_memory_drift_emotion": avg_de,
            "params": {
                "threshold": self.THRESHOLD,
                "integration_weight": self.integration_weight,
                "noise_max": self.noise_max,
                "base_sync_weight": self.base_sync_weight,
                "mismatch_weight": self.mismatch_weight,
                "emotion_weight": self.emotion_weight,
                "novelty_penalty": self.novelty_penalty,
                "context_gain": self.context_gain,
                "context_noise": self.context_noise,
            },
        }


def robustness_sweep(
    seeds: List[int],
    env: str,
    steps: int,
    noise_max_values: List[float],
) -> List[Dict]:
    """
    Simple robustness sweep:
    - vary noise_max (and multiple seeds)
    - record consciousness_rate and threshold crossing
    """
    results = []
    for noise_max in noise_max_values:
        rates = []
        crosses = 0
        for sd in seeds:
            sys = ConsciousnessSystemIntegrated(seed=sd, noise_max=noise_max)
            out = sys.run(steps=steps, environment=env)
            rates.append(out["consciousness_rate"])
            if out["threshold_crossed_at"] is not None:
                crosses += 1
        results.append({
            "environment": env,
            "steps": steps,
            "noise_max": noise_max,
            "mean_rate": statistics.mean(rates),
            "stdev_rate": statistics.pstdev(rates) if len(rates) > 1 else 0.0,
            "cross_ratio": crosses / len(seeds),
        })
    return results


if __name__ == "__main__":
    print("Phase5/6 Integrated Demo")
    for env in ["focused", "varied"]:
        sys = ConsciousnessSystemIntegrated(seed=0)
        out = sys.run(steps=10000, environment=env)
        print("\n---", env.upper(), "---")
        for k, v in out.items():
            if k in ("params",):
                continue
            if isinstance(v, float):
                print(f"{k}: {v:.4f}")
            else:
                print(f"{k}: {v}")
        print("params:", out["params"])

    print("\nRobustness sweep (noise_max):")
    sweep = robustness_sweep(seeds=list(range(5)), env="focused", steps=5000, noise_max_values=[0.05, 0.1, 0.2, 0.3])
    for r in sweep:
        print(r)
