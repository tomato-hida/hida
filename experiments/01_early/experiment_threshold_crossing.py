"""
閾値0.3突破の観察実験

目的：
1. self_strengthが0.3を超える瞬間を観察
2. 超える前と後で何が変わるか
3. 意識判定が切り替わる瞬間を見る

実行：3000ステップ
詳細ログ：10ステップごと
"""

import random
from typing import Dict, List, Tuple


class SimpleEnvironment:
    """簡易環境"""
    
    def __init__(self, seed: int = 123):
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
        self.threshold_crossed_at = None  # 閾値突破タイミング
    
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
        similarity = self.compare(current)
        
        # 閾値突破前のself_strength
        old_strength = self.self_strength
        
        if similarity > 0.5:
            self.self_strength += 0.01 * similarity
            self.self_strength = min(1.0, self.self_strength)
        
        self.memory.append(current)
        self.activity[3] = 1.0 if len(self.memory) > 0 else 0.0
        
        # 閾値突破を検出
        if old_strength < 0.3 and self.self_strength >= 0.3:
            self.threshold_crossed_at = len(self.memory)
        
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
            'sensor': sensor_input,
            'quale': quale_name,
            'value': value,
            'action': action,
            'similarity': similarity,
            'self_strength': self.self_strength,
            'activity': self.activity.copy(),
            'sync_score': sync_score,
            'conscious': conscious,
            'just_crossed': (old_strength < 0.3 and self.self_strength >= 0.3)
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


def main():
    """メイン実行"""
    print("=" * 70)
    print("閾値0.3突破の観察実験")
    print("=" * 70)
    print()
    
    # システム初期化
    system = MinimalConsciousness()
    environment = SimpleEnvironment(seed=123)
    
    # 結果記録
    results = []
    
    print("実行中（3000ステップ）...")
    print()
    
    # 実行
    for t in range(3000):
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 全結果を記録
        results.append(result.copy())
        
        # 閾値突破の瞬間を詳細表示
        if result['just_crossed']:
            print("!" * 70)
            print(f"★★★ 閾値突破！ t={result['time']} ★★★")
            print("!" * 70)
            print(f"  self_strength: {result['self_strength']:.4f}")
            print(f"  sync_score: {result['sync_score']:.3f}")
            print(f"  conscious: {result['conscious']}")
            print(f"  クオリア: {result['quale']}")
            print(f"  類似度: {result['similarity']:.3f}")
            print("!" * 70)
            print()
    
    # 分析
    print("\n" + "=" * 70)
    print("分析結果")
    print("=" * 70)
    print()
    
    # 閾値突破タイミング
    if system.threshold_crossed_at:
        print(f"閾値突破タイミング: t={system.threshold_crossed_at}")
        print()
    else:
        print("閾値突破なし（self_strength < 0.3）")
        print()
    
    # self_strengthの推移（100ステップごと）
    print("self_strengthの推移（100ステップごと）:")
    print("-" * 70)
    for i in range(0, 3000, 100):
        if i < len(results):
            r = results[i]
            marker = " ← 意識あり" if r['conscious'] else ""
            print(f"t={r['time']:4d}: {r['self_strength']:.4f}{marker}")
    
    print()
    
    # 最終状態
    final = results[-1]
    print("最終状態:")
    print("-" * 70)
    print(f"  時刻: {final['time']}")
    print(f"  自己強度: {final['self_strength']:.4f}")
    print(f"  意識: {'**あり**' if final['conscious'] else 'なし'}")
    print(f"  行動回数: {system.action_count}")
    print()
    
    # 閾値前後の比較
    if system.threshold_crossed_at:
        cross_idx = system.threshold_crossed_at - 1
        
        print("閾値前後の詳細比較:")
        print("-" * 70)
        
        # 前50ステップの平均
        before_start = max(0, cross_idx - 50)
        before_results = results[before_start:cross_idx]
        
        if before_results:
            avg_sync_before = sum(r['sync_score'] for r in before_results) / len(before_results)
            conscious_count_before = sum(1 for r in before_results if r['conscious'])
            
            print(f"閾値前（50ステップ）:")
            print(f"  平均sync_score: {avg_sync_before:.3f}")
            print(f"  意識あり回数: {conscious_count_before}/{len(before_results)}")
        
        # 後50ステップの平均
        after_end = min(len(results), cross_idx + 51)
        after_results = results[cross_idx+1:after_end]
        
        if after_results:
            avg_sync_after = sum(r['sync_score'] for r in after_results) / len(after_results)
            conscious_count_after = sum(1 for r in after_results if r['conscious'])
            
            print(f"閾値後（50ステップ）:")
            print(f"  平均sync_score: {avg_sync_after:.3f}")
            print(f"  意識あり回数: {conscious_count_after}/{len(after_results)}")
        
        print()
    
    # グラフ的表示（簡易版）
    print("self_strengthの推移グラフ:")
    print("-" * 70)
    
    for i in range(0, 3000, 200):
        if i < len(results):
            strength = results[i]['self_strength']
            bar_length = int(strength * 50)  # 0.0-1.0 を 0-50文字に
            bar = "█" * bar_length
            
            if strength >= 0.3:
                marker = f" {strength:.3f} ← 意識"
            else:
                marker = f" {strength:.3f}"
            
            print(f"t={i:4d} |{bar}{marker}")
    
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
