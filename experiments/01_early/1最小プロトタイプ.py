"""
人の内なる運動理論：最小プロトタイプ（Gemini版）

Phase 1: 反応システム + 記憶 + 意識判定
- 3つのクオリア（pain, warm, sweet）
- 簡易的な同期判定
- self_strengthの計算
- 閉じた回路
"""

import random
from typing import Dict, List, Tuple


class SimpleEnvironment:
    """簡易環境：ランダムな刺激を生成"""
    
    def __init__(self):
        self.time = 0
        
    def get_input(self) -> Dict:
        """センサー入力を返す"""
        self.time += 1
        
        # ランダムに刺激を生成
        stimulus_type = random.choice(['temperature', 'taste', 'neutral'])
        
        if stimulus_type == 'temperature':
            # 温度刺激（高温 or 低温）
            value = random.uniform(20, 60)
            return {'type': 'temperature', 'value': value}
        elif stimulus_type == 'taste':
            # 味覚刺激
            return {'type': 'taste', 'value': 1.0}
        else:
            # 中立的刺激
            return {'type': 'neutral', 'value': 0.0}
    
    def apply(self, action: str):
        """行動を環境に適用（今は何もしない）"""
        pass


class MinimalConsciousness:
    """最小意識システム"""
    
    def __init__(self):
        # DNA初期値（-1.0 ~ +1.0）
        self.qualia_dna = {
            'pain': -0.9,    # 痛み：強烈に避ける
            'warm': -0.2,    # 暖かい：やや避ける
            'sweet': +0.7    # 甘い：近づく
        }
        
        # 記憶（過去のパターン）
        self.memory: List[Tuple[str, float]] = []
        
        # 自己強度
        self.self_strength = 0.0
        
        # 各層の活動度（同期判定用）
        self.activity = [0.0, 0.0, 0.0, 0.0]  # [第1層, 第2層, 第3層, 第4層]
    
    def step(self, sensor_input: Dict) -> Dict:
        """1ステップの処理"""
        
        # 第1層：身体（センサー入力）
        self.activity[0] = 1.0 if sensor_input['value'] > 0 else 0.0
        
        # 第2層：クオリア（分類 + 価値）
        quale_name = self.classify(sensor_input)
        value = self.qualia_dna.get(quale_name, 0.0)
        self.activity[1] = abs(value)
        
        # 第3層：構造化（判断）
        if value < -0.5:
            decision_value = -1.0  # 回避
            action = 'avoid'
        elif value > 0.5:
            decision_value = +1.0  # 接近
            action = 'approach'
        else:
            decision_value = 0.0   # 中立
            action = 'neutral'
        self.activity[2] = abs(decision_value)
        
        # 第4層：記憶（過去との照合）
        current = (quale_name, value)
        similarity = self.compare(current)
        
        # 類似度が高ければself_strengthを増加
        if similarity > 0.5:
            self.self_strength += 0.01 * similarity
            self.self_strength = min(1.0, self.self_strength)  # 上限1.0
        
        # 記憶に保存
        self.memory.append(current)
        self.activity[3] = 1.0 if len(self.memory) > 0 else 0.0
        
        # 同期スコア（簡易版）
        # 1. 活動度の同期（幾何平均）
        activity_sync = (self.activity[0] * self.activity[1] * 
                        self.activity[2] * self.activity[3]) ** 0.25
        
        # 2. 方向の一致
        direction_match = 1.0 if self._same_sign(value, decision_value) else 0.5
        
        # 3. 記憶の関与
        memory_engagement = similarity
        
        # 総合同期スコア
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
            'conscious': conscious
        }
    
    def classify(self, signal: Dict) -> str:
        """信号をクオリアに分類"""
        if signal['type'] == 'temperature':
            if signal['value'] > 45:
                return 'pain'  # 高温 → 痛み
            else:
                return 'warm'  # 低温 → 暖かい
        elif signal['type'] == 'taste':
            return 'sweet'  # 味覚 → 甘い
        else:
            return 'neutral'
    
    def compare(self, current: Tuple[str, float]) -> float:
        """過去との類似度を計算"""
        if len(self.memory) == 0:
            return 0.0
        
        # 最近10個のパターンと比較
        recent = self.memory[-10:] if len(self.memory) >= 10 else self.memory
        
        # 同じクオリア名のパターン数をカウント
        matches = sum(1 for p in recent if p[0] == current[0])
        
        return matches / len(recent)
    
    def _same_sign(self, a: float, b: float) -> bool:
        """同符号かどうか"""
        if a == 0 or b == 0:
            return True
        return (a > 0) == (b > 0)


def main():
    """メイン実行"""
    print("=" * 60)
    print("人の内なる運動理論：最小プロトタイプ")
    print("=" * 60)
    print()
    
    # システム初期化
    system = MinimalConsciousness()
    environment = SimpleEnvironment()
    
    # 実行
    print("実行中...")
    print()
    
    for t in range(1000):
        # 1ステップ実行
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 100ステップごとに状態を表示
        if t % 100 == 0:
            print(f"時刻 t={result['time']:4d}:")
            print(f"  クオリア: {result['quale']:8s}  価値: {result['value']:+.2f}")
            print(f"  行動: {result['action']:8s}")
            print(f"  類似度: {result['similarity']:.3f}")
            print(f"  自己強度: {result['self_strength']:.3f}")
            print(f"  活動度: [{', '.join(f'{a:.2f}' for a in result['activity'])}]")
            print(f"  同期スコア: {result['sync_score']:.3f}")
            print(f"  意識: {'**YES**' if result['conscious'] else 'no'}")
            print()
    
    # 最終結果
    print("=" * 60)
    print("最終状態:")
    print(f"  総ステップ数: {len(system.memory)}")
    print(f"  自己強度: {system.self_strength:.3f}")
    print(f"  記憶パターン数: {len(system.memory)}")
    print(f"  意識の有無: {'**意識あり**' if system.self_strength >= 0.3 else '意識なし'}")
    print("=" * 60)


if __name__ == '__main__':
    main()