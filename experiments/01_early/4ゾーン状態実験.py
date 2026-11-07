"""
予測9の検証実験：集中/ゾーン状態の再現

比較実験：
- 環境A（通常）: 刺激が多様（neutral 50%）
- 環境B（集中）: 刺激が一定（pain/sweetのみ）

予測：
- A: 意識が途切れ途切れ（持続率 < 10%）
- B: 意識がほぼ持続（持続率 > 80%）

理由：
- neutral刺激 → sync_score = 0 → 意識消失
- pain/sweet刺激 → sync_score > 0 → 意識維持
"""

import random
from typing import Dict, List, Tuple


class Environment:
    """環境クラス（刺激パターンを制御）"""
    
    def __init__(self, mode: str = 'normal', seed: int = 42):
        """
        mode: 
            'normal' - 通常（neutral 50%）
            'focused' - 集中（pain/sweetのみ）
        """
        self.mode = mode
        random.seed(seed)
        self.time = 0
        
    def get_input(self) -> Dict:
        """センサー入力を返す"""
        self.time += 1
        
        if self.mode == 'normal':
            # 通常：neutral多め
            stimulus_type = random.choice(['temperature', 'taste', 'neutral'])
        elif self.mode == 'focused':
            # 集中：pain/sweetのみ
            stimulus_type = random.choice(['temperature', 'taste'])
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
        
        if stimulus_type == 'temperature':
            value = random.uniform(20, 60)
            return {'type': 'temperature', 'value': value}
        elif stimulus_type == 'taste':
            return {'type': 'taste', 'value': 1.0}
        else:  # neutral
            return {'type': 'neutral', 'value': 0.0}
    
    def apply(self, action: str):
        pass


class MinimalConsciousness:
    """最小意識システム"""
    
    def __init__(self):
        self.qualia_dna = {
            'pain': -0.9,
            'warm': -0.2,
            'sweet': +0.7
        }
        
        self.memory: List[Tuple[str, float]] = []
        self.self_strength = 0.0
        self.activity = [0.0, 0.0, 0.0, 0.0]
        
        # 統計
        self.action_count = {'avoid': 0, 'approach': 0, 'neutral': 0}
        self.conscious_count = 0  # 意識があった回数
        self.total_steps = 0
    
    def step(self, sensor_input: Dict) -> Dict:
        """1ステップの処理"""
        
        self.total_steps += 1
        
        # 第1層：身体
        self.activity[0] = 1.0 if sensor_input['value'] > 0 else 0.0
        
        # 第2層：クオリア
        quale_name = self.classify(sensor_input)
        value = self.qualia_dna.get(quale_name, 0.0)
        self.activity[1] = abs(value)
        
        # 第3層：構造化
        if value < -0.5:
            decision_value = -1.0
            action = 'avoid'
        elif value > 0.5:
            decision_value = +1.0
            action = 'approach'
        else:
            decision_value = 0.0
            action = 'neutral'
        self.activity[2] = abs(decision_value)
        self.action_count[action] += 1
        
        # 第4層：記憶
        current = (quale_name, value)
        similarity = self.compare(current)
        
        if similarity > 0.5:
            self.self_strength += 0.01 * similarity
            self.self_strength = min(1.0, self.self_strength)
        
        self.memory.append(current)
        self.activity[3] = 1.0 if len(self.memory) > 0 else 0.0
        
        # 同期スコア
        activity_sync = (self.activity[0] * self.activity[1] * 
                        self.activity[2] * self.activity[3]) ** 0.25
        direction_match = 1.0 if self._same_sign(value, decision_value) else 0.5
        memory_engagement = similarity
        
        sync_score = activity_sync * direction_match * memory_engagement
        
        # 意識判定
        conscious = (sync_score >= 0.3 and self.self_strength >= 0.3)
        
        if conscious:
            self.conscious_count += 1
        
        return {
            'time': len(self.memory),
            'quale': quale_name,
            'value': value,
            'action': action,
            'similarity': similarity,
            'self_strength': self.self_strength,
            'activity': self.activity.copy(),
            'sync_score': sync_score,
            'conscious': conscious
        }
    
    def classify(self, signal: Dict) -> str:
        if signal['type'] == 'temperature':
            if signal['value'] > 45:
                return 'pain'
            else:
                return 'warm'
        elif signal['type'] == 'taste':
            return 'sweet'
        else:
            return 'neutral'
    
    def compare(self, current: Tuple[str, float]) -> float:
        if len(self.memory) == 0:
            return 0.0
        
        recent = self.memory[-10:] if len(self.memory) >= 10 else self.memory
        matches = sum(1 for p in recent if p[0] == current[0])
        
        return matches / len(recent)
    
    def _same_sign(self, a: float, b: float) -> bool:
        if a == 0 or b == 0:
            return True
        return (a > 0) == (b > 0)
    
    def get_consciousness_rate(self) -> float:
        """意識の持続率を計算"""
        if self.total_steps == 0:
            return 0.0
        return self.conscious_count / self.total_steps


def run_experiment(mode: str, steps: int = 2000) -> Dict:
    """実験を実行"""
    system = MinimalConsciousness()
    environment = Environment(mode=mode, seed=42)
    
    results = []
    
    for t in range(steps):
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 100ステップごとに記録
        if t % 100 == 0 or t == steps - 1:
            results.append(result.copy())
    
    # self_strength >= 0.3になってからの持続率も計算
    threshold_crossed_at = None
    conscious_after_threshold = 0
    steps_after_threshold = 0
    
    for i, r in enumerate(results):
        if threshold_crossed_at is None and r['self_strength'] >= 0.3:
            threshold_crossed_at = i * 100
        
        if threshold_crossed_at is not None and i * 100 >= threshold_crossed_at:
            if r['conscious']:
                conscious_after_threshold += 1
            steps_after_threshold += 1
    
    consciousness_rate_after_threshold = (
        conscious_after_threshold / steps_after_threshold 
        if steps_after_threshold > 0 else 0.0
    )
    
    return {
        'mode': mode,
        'system': system,
        'results': results,
        'final_self_strength': system.self_strength,
        'consciousness_rate': system.get_consciousness_rate(),
        'consciousness_rate_after_threshold': consciousness_rate_after_threshold,
        'action_count': system.action_count.copy(),
        'threshold_crossed_at': threshold_crossed_at
    }


def main():
    """メイン実行"""
    print("=" * 70)
    print("予測9の検証実験：集中/ゾーン状態の再現")
    print("=" * 70)
    print()
    
    # 実験A：通常環境
    print("【実験A：通常環境（neutral含む）】")
    print("-" * 70)
    print("実行中（2000ステップ）...")
    
    exp_a = run_experiment(mode='normal', steps=2000)
    
    print(f"\n最終結果:")
    print(f"  自己強度: {exp_a['final_self_strength']:.3f}")
    print(f"  意識持続率（全体）: {exp_a['consciousness_rate']:.1%}")
    print(f"  意識持続率（閾値後）: {exp_a['consciousness_rate_after_threshold']:.1%}")
    print(f"  閾値突破: t={exp_a['threshold_crossed_at']}")
    print(f"  行動回数: {exp_a['action_count']}")
    
    print("\n" + "=" * 70)
    print()
    
    # 実験B：集中環境
    print("【実験B：集中環境（pain/sweetのみ）】")
    print("-" * 70)
    print("実行中（2000ステップ）...")
    
    exp_b = run_experiment(mode='focused', steps=2000)
    
    print(f"\n最終結果:")
    print(f"  自己強度: {exp_b['final_self_strength']:.3f}")
    print(f"  意識持続率（全体）: {exp_b['consciousness_rate']:.1%}")
    print(f"  意識持続率（閾値後）: {exp_b['consciousness_rate_after_threshold']:.1%}")
    print(f"  閾値突破: t={exp_b['threshold_crossed_at']}")
    print(f"  行動回数: {exp_b['action_count']}")
    
    print("\n" + "=" * 70)
    print()
    
    # 比較
    print("【比較結果】")
    print("-" * 70)
    print()
    
    print("環境A（通常）:")
    print(f"  刺激構成: avoid={exp_a['action_count']['avoid']}, "
          f"approach={exp_a['action_count']['approach']}, "
          f"neutral={exp_a['action_count']['neutral']}")
    print(f"  意識持続率（閾値後）: {exp_a['consciousness_rate_after_threshold']:.1%}")
    print()
    
    print("環境B（集中）:")
    print(f"  刺激構成: avoid={exp_b['action_count']['avoid']}, "
          f"approach={exp_b['action_count']['approach']}, "
          f"neutral={exp_b['action_count']['neutral']}")
    print(f"  意識持続率（閾値後）: {exp_b['consciousness_rate_after_threshold']:.1%}")
    print()
    
    # 差
    diff = exp_b['consciousness_rate_after_threshold'] - exp_a['consciousness_rate_after_threshold']
    print(f"差: {diff:+.1%}")
    print()
    
    # グラフ的比較
    print("意識持続率の視覚的比較（閾値後）:")
    print("-" * 70)
    
    bar_a_length = int(exp_a['consciousness_rate_after_threshold'] * 50)
    bar_b_length = int(exp_b['consciousness_rate_after_threshold'] * 50)
    
    bar_a = "█" * bar_a_length
    bar_b = "█" * bar_b_length
    
    print(f"環境A: |{bar_a} {exp_a['consciousness_rate_after_threshold']:.1%}")
    print(f"環境B: |{bar_b} {exp_b['consciousness_rate_after_threshold']:.1%}")
    print()
    
    # 予測との照合
    print("【予測との照合】")
    print("-" * 70)
    
    print("理論の予測:")
    print(f"  1. 環境A: 意識持続率 < 10% → ", end="")
    if exp_a['consciousness_rate_after_threshold'] < 0.10:
        print(f"✓ 成立（実測: {exp_a['consciousness_rate_after_threshold']:.1%}）")
    else:
        print(f"✗ 不成立（実測: {exp_a['consciousness_rate_after_threshold']:.1%}）")
    
    print(f"  2. 環境B: 意識持続率 > 80% → ", end="")
    if exp_b['consciousness_rate_after_threshold'] > 0.80:
        print(f"✓ 成立（実測: {exp_b['consciousness_rate_after_threshold']:.1%}）")
    else:
        print(f"✗ 不成立（実測: {exp_b['consciousness_rate_after_threshold']:.1%}）")
    
    print(f"  3. B > A → ", end="")
    if exp_b['consciousness_rate_after_threshold'] > exp_a['consciousness_rate_after_threshold']:
        print(f"✓ 成立（差: {diff:+.1%}）")
    else:
        print(f"✗ 不成立")
    
    print()
    
    # 結論
    print("【結論】")
    print("-" * 70)
    
    both_predictions_met = (
        exp_a['consciousness_rate_after_threshold'] < 0.10 and
        exp_b['consciousness_rate_after_threshold'] > 0.80
    )
    
    if both_predictions_met:
        print("**予測9は成立した**")
        print()
        print("刺激が一定（集中環境）では意識が持続する。")
        print("刺激が多様（通常環境）では意識が途切れる。")
        print()
        print("これは集中/ゾーン状態の理論的説明になる。")
    else:
        print("予測9は部分的に成立、または不成立。")
        print()
        print(f"環境A（通常）: {exp_a['consciousness_rate_after_threshold']:.1%}")
        print(f"環境B（集中）: {exp_b['consciousness_rate_after_threshold']:.1%}")
        print()
        if exp_b['consciousness_rate_after_threshold'] > exp_a['consciousness_rate_after_threshold']:
            print("方向性は正しい（B > A）が、予測値とずれがある。")
    
    print()
    print("=" * 70)
    
    # 詳細データ（閾値後の推移）
    print()
    print("【詳細：閾値後のself_strength推移】")
    print("-" * 70)
    
    print("\n環境A（通常）:")
    for r in exp_a['results']:
        if r['self_strength'] >= 0.3:
            marker = "←意識" if r['conscious'] else ""
            print(f"  t={r['time']:4d}: self={r['self_strength']:.3f}, "
                  f"sync={r['sync_score']:.3f} {marker}")
    
    print("\n環境B（集中）:")
    for r in exp_b['results']:
        if r['self_strength'] >= 0.3:
            marker = "←意識" if r['conscious'] else ""
            print(f"  t={r['time']:4d}: self={r['self_strength']:.3f}, "
                  f"sync={r['sync_score']:.3f} {marker}")
    
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()