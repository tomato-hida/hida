"""
予測1の検証実験：記憶を封じると意識が消える

比較実験：
- システムA：正常（記憶あり）
- システムB：記憶封鎖（第4層を無効化）

予測：
- A: self_strength増加 → 意識あり
- B: self_strength増加せず → 意識なし
- 両方とも行動は続く
"""

import random
from typing import Dict, List, Tuple


class SimpleEnvironment:
    """簡易環境：ランダムな刺激を生成（seed固定で再現可能）"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.time = 0
        
    def get_input(self) -> Dict:
        """センサー入力を返す"""
        self.time += 1
        stimulus_type = random.choice(['temperature', 'taste', 'neutral'])
        
        if stimulus_type == 'temperature':
            value = random.uniform(20, 60)
            return {'type': 'temperature', 'value': value}
        elif stimulus_type == 'taste':
            return {'type': 'taste', 'value': 1.0}
        else:
            return {'type': 'neutral', 'value': 0.0}
    
    def apply(self, action: str):
        """行動を環境に適用"""
        pass


class MinimalConsciousness:
    """最小意識システム（記憶封鎖オプション付き）"""
    
    def __init__(self, memory_disabled: bool = False):
        # DNA初期値
        self.qualia_dna = {
            'pain': -0.9,
            'warm': -0.2,
            'sweet': +0.7
        }
        
        # 記憶
        self.memory: List[Tuple[str, float]] = []
        self.memory_disabled = memory_disabled  # 記憶封鎖フラグ
        
        # 自己強度
        self.self_strength = 0.0
        
        # 各層の活動度
        self.activity = [0.0, 0.0, 0.0, 0.0]
        
        # 統計
        self.action_count = {'avoid': 0, 'approach': 0, 'neutral': 0}
    
    def step(self, sensor_input: Dict) -> Dict:
        """1ステップの処理"""
        
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
        
        if self.memory_disabled:
            # **記憶封鎖：照合をスキップ**
            similarity = 0.0
            self.activity[3] = 0.0  # 第4層が動いていない
        else:
            # 正常：記憶照合
            similarity = self.compare(current)
            
            if similarity > 0.5:
                self.self_strength += 0.01 * similarity
                self.self_strength = min(1.0, self.self_strength)
            
            self.activity[3] = 1.0 if len(self.memory) > 0 else 0.0
        
        # 記憶に保存（封鎖してても蓄積はする、でも使わない）
        self.memory.append(current)
        
        # 同期スコア
        activity_sync = (self.activity[0] * self.activity[1] * 
                        self.activity[2] * self.activity[3]) ** 0.25
        direction_match = 1.0 if self._same_sign(value, decision_value) else 0.5
        memory_engagement = similarity
        
        sync_score = activity_sync * direction_match * memory_engagement
        
        # 意識判定
        conscious = (sync_score >= 0.3 and self.self_strength >= 0.3)
        
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


def run_experiment(memory_disabled: bool, steps: int = 1000) -> Dict:
    """実験を実行"""
    system = MinimalConsciousness(memory_disabled=memory_disabled)
    environment = SimpleEnvironment(seed=42)  # 同じseedで再現性
    
    results = []
    
    for t in range(steps):
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 100ステップごとに記録
        if t % 100 == 0:
            results.append(result.copy())
    
    return {
        'system': system,
        'results': results,
        'final_self_strength': system.self_strength,
        'final_conscious': system.self_strength >= 0.3,
        'action_count': system.action_count.copy()
    }


def main():
    """メイン実行"""
    print("=" * 70)
    print("予測1の検証実験：記憶を封じると意識が消える")
    print("=" * 70)
    print()
    
    # 実験A：正常（記憶あり）
    print("【実験A：正常システム（記憶あり）】")
    print("-" * 70)
    exp_a = run_experiment(memory_disabled=False, steps=1000)
    
    print("\n経過観察:")
    for r in exp_a['results']:
        print(f"t={r['time']:4d}: self={r['self_strength']:.3f}, "
              f"sync={r['sync_score']:.3f}, conscious={'YES' if r['conscious'] else 'no '}")
    
    print(f"\n最終結果:")
    print(f"  自己強度: {exp_a['final_self_strength']:.3f}")
    print(f"  意識: {'**あり**' if exp_a['final_conscious'] else 'なし'}")
    print(f"  行動回数: {exp_a['action_count']}")
    
    print("\n" + "=" * 70)
    print()
    
    # 実験B：記憶封鎖
    print("【実験B：記憶封鎖システム（記憶なし）】")
    print("-" * 70)
    exp_b = run_experiment(memory_disabled=True, steps=1000)
    
    print("\n経過観察:")
    for r in exp_b['results']:
        print(f"t={r['time']:4d}: self={r['self_strength']:.3f}, "
              f"sync={r['sync_score']:.3f}, conscious={'YES' if r['conscious'] else 'no '}")
    
    print(f"\n最終結果:")
    print(f"  自己強度: {exp_b['final_self_strength']:.3f}")
    print(f"  意識: {'**あり**' if exp_b['final_conscious'] else 'なし'}")
    print(f"  行動回数: {exp_b['action_count']}")
    
    print("\n" + "=" * 70)
    print()
    
    # 比較
    print("【比較結果】")
    print("-" * 70)
    print(f"システムA（正常）:")
    print(f"  - 自己強度: {exp_a['final_self_strength']:.3f}")
    print(f"  - 意識: {'あり' if exp_a['final_conscious'] else 'なし'}")
    print(f"  - 第4層活動: あり")
    print()
    print(f"システムB（記憶封鎖）:")
    print(f"  - 自己強度: {exp_b['final_self_strength']:.3f}")
    print(f"  - 意識: {'あり' if exp_b['final_conscious'] else 'なし'}")
    print(f"  - 第4層活動: なし")
    print()
    print(f"行動回数の比較:")
    print(f"  A: {exp_a['action_count']}")
    print(f"  B: {exp_b['action_count']}")
    print()
    
    # 予測との照合
    print("【予測との照合】")
    print("-" * 70)
    print("理論の予測:")
    print("  1. 両方とも行動は続く → ", end="")
    if exp_a['action_count'] != {'avoid': 0, 'approach': 0, 'neutral': 0} and \
       exp_b['action_count'] != {'avoid': 0, 'approach': 0, 'neutral': 0}:
        print("✓ 成立")
    else:
        print("✗ 不成立")
    
    print("  2. Aは意識あり → ", end="")
    if exp_a['final_conscious']:
        print("✓ 成立")
    else:
        print("✗ 不成立")
    
    print("  3. Bは意識なし → ", end="")
    if not exp_b['final_conscious']:
        print("✓ 成立")
    else:
        print("✗ 不成立")
    
    print("  4. Bのself_strengthは増えない → ", end="")
    if exp_b['final_self_strength'] == 0.0:
        print("✓ 成立")
    else:
        print("✗ 不成立")
    
    print()
    print("=" * 70)
    
    # 結論
    all_predictions_met = (
        exp_a['final_conscious'] and 
        not exp_b['final_conscious'] and
        exp_b['final_self_strength'] == 0.0
    )
    
    if all_predictions_met:
        print("結論: **予測1は成立した**")
        print("記憶を封じると意識が消える。理論と一致。")
    else:
        print("結論: 予測1は成立しなかった")
        print("理論の修正が必要。")
    
    print("=" * 70)


if __name__ == '__main__':
    main()
