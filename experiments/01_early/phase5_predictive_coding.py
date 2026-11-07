"""
Phase 5: 予測符号化（Predictive Coding）

目標：
1. 第3層の高度化 - 予測と誤差計算
2. 世界モデルの構築 - 次に何が起こるかを予測
3. 予測誤差に基づく注意と学習
4. より人間らしい認知の実現

予測符号化とは：
- 脳は常に「次に何が起こるか」を予測
- 実際の入力と予測の誤差を計算
- 誤差が大きい → 注意、驚き、学習
- 誤差が小さい → 予測成功、安心
"""

import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class PredictiveEnvironment:
    """パターンを持つ環境（予測可能性あり）"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.time = 0
        self.pattern_mode = 'random'
        self.pattern_counter = 0
        
        # パターン定義
        self.patterns = {
            'morning_routine': [
                {'type': 'temperature', 'value': 20},  # 快適
                {'type': 'taste', 'subtype': 'sweet', 'intensity': 0.7},  # 朝食
                {'type': 'visual', 'brightness': 8, 'color': 'neutral'},  # 明るい
            ],
            'work_stress': [
                {'type': 'sound', 'volume': 10, 'pitch': 'high'},  # うるさい
                {'type': 'pressure', 'value': 8},  # プレッシャー
                {'type': 'body_state', 'subtype': 'tired', 'intensity': 0.8},  # 疲れ
            ],
            'relaxation': [
                {'type': 'temperature', 'value': 25},  # 暖かい
                {'type': 'texture', 'subtype': 'soft', 'intensity': 0.8},  # 柔らかい
                {'type': 'sound', 'volume': 2, 'pitch': 'low'},  # 静か
            ],
            'danger': [
                {'type': 'pain', 'intensity': 12},  # 痛み
                {'type': 'temperature', 'value': 50},  # 熱い
                {'type': 'sound', 'volume': 11, 'pitch': 'high'},  # 大音量
            ]
        }
        
    def get_input(self) -> Dict:
        """環境からの入力（パターンあり）"""
        self.time += 1
        
        # 100ステップごとにモード切替
        if self.time % 100 == 0:
            self.pattern_mode = random.choice(list(self.patterns.keys()) + ['random'])
            self.pattern_counter = 0
        
        # パターンモードの場合
        if self.pattern_mode != 'random':
            pattern = self.patterns[self.pattern_mode]
            stimulus = pattern[self.pattern_counter % len(pattern)]
            self.pattern_counter += 1
            return stimulus
        
        # ランダムモード（予測不可能）
        return self._random_stimulus()
    
    def _random_stimulus(self) -> Dict:
        """ランダムな刺激"""
        stimulus_type = random.choice([
            'temperature', 'taste', 'pressure', 'texture',
            'sound', 'visual', 'smell', 'body_state', 'pain', 'neutral'
        ])
        
        if stimulus_type == 'temperature':
            return {'type': 'temperature', 'value': random.uniform(-10, 60)}
        elif stimulus_type == 'taste':
            return {
                'type': 'taste',
                'subtype': random.choice(['sweet', 'bitter', 'sour', 'spicy', 'salty', 'umami']),
                'intensity': random.uniform(0.3, 1.0)
            }
        elif stimulus_type == 'pressure':
            return {'type': 'pressure', 'value': random.uniform(0, 15)}
        elif stimulus_type == 'texture':
            return {
                'type': 'texture',
                'subtype': random.choice(['smooth', 'rough', 'soft', 'hard', 'wet', 'dry']),
                'intensity': random.uniform(0.5, 1.0)
            }
        elif stimulus_type == 'sound':
            return {
                'type': 'sound',
                'volume': random.uniform(0, 12),
                'pitch': random.choice(['high', 'low', 'moderate'])
            }
        elif stimulus_type == 'visual':
            return {
                'type': 'visual',
                'brightness': random.uniform(0, 12),
                'color': random.choice(['red', 'blue', 'green', 'yellow', 'neutral'])
            }
        elif stimulus_type == 'smell':
            return {
                'type': 'smell',
                'subtype': random.choice(['pleasant', 'unpleasant', 'neutral', 'pungent']),
                'intensity': random.uniform(0.3, 1.0)
            }
        elif stimulus_type == 'body_state':
            return {
                'type': 'body_state',
                'subtype': random.choice(['tired', 'energetic', 'hungry', 'full', 'thirsty']),
                'intensity': random.uniform(0.5, 1.0)
            }
        elif stimulus_type == 'pain':
            return {'type': 'pain', 'intensity': random.uniform(5, 15)}
        else:
            return {'type': 'neutral', 'value': 0.0}
    
    def apply(self, action: str):
        pass


class PredictiveCoding:
    """予測符号化システム（第3層の高度化）"""
    
    def __init__(self):
        # 予測モデル（簡易版：マルコフ連鎖）
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.total_counts = defaultdict(int)
        
        # 予測精度の追跡
        self.prediction_errors = []
        self.prediction_accuracy = 0.0
        
        # 注意メカニズム
        self.attention_threshold = 0.5  # 誤差がこれ以上で注意
        self.attention_state = False
        
    def predict_next(self, current_state: str) -> Dict[str, float]:
        """次の状態を予測（確率分布）"""
        if self.total_counts[current_state] == 0:
            # 未知の状態 → 一様分布
            return {}
        
        predictions = {}
        total = self.total_counts[current_state]
        
        for next_state, count in self.transition_counts[current_state].items():
            predictions[next_state] = count / total
        
        return predictions
    
    def calculate_error(self, predicted: Dict[str, float], actual: str) -> float:
        """予測誤差の計算"""
        if not predicted:
            return 1.0  # 完全な不確実性
        
        # 実際の状態が予測分布にあるか
        if actual in predicted:
            # 予測確率が高いほど誤差は小さい
            return 1.0 - predicted[actual]
        else:
            # 予測していなかった → 最大誤差
            return 1.0
    
    def update_model(self, prev_state: str, current_state: str):
        """遷移モデルの更新（学習）"""
        self.transition_counts[prev_state][current_state] += 1
        self.total_counts[prev_state] += 1
    
    def update_attention(self, error: float):
        """注意状態の更新"""
        self.attention_state = error > self.attention_threshold
        self.prediction_errors.append(error)
        
        # 最近100ステップの精度
        if len(self.prediction_errors) > 100:
            self.prediction_errors.pop(0)
        
        recent_errors = self.prediction_errors[-100:]
        self.prediction_accuracy = 1.0 - (sum(recent_errors) / len(recent_errors))


class PredictiveConsciousness:
    """予測符号化を持つ意識システム"""
    
    def __init__(self):
        # 基本クオリア（Phase 4から継承）
        self.physical_qualia = {
            'freezing': 'DNA', 'cold': 'DNA', 'warm': 'DNA', 'hot': 'DNA', 'burning': 'DNA',
            'sweet': 'DNA', 'bitter': 'DNA', 'sour': 'DNA', 'spicy': 'DNA', 'salty': 'DNA', 'umami': 'DNA',
            'pressure': 'DNA', 'pain': 'DNA', 'sharp_pain': 'DNA',
            'smooth': 'learning', 'rough': 'learning', 'soft': 'learning',
            'hard': 'learning', 'wet': 'learning', 'dry': 'learning',
            'loud': 'learning', 'quiet': 'learning', 'high_pitch': 'learning',
            'bright': 'learning', 'dark': 'learning',
            'red': 'learning', 'blue': 'learning', 'green': 'learning',
            'pleasant_smell': 'learning', 'unpleasant_smell': 'learning',
        }
        
        self.emotional_qualia = {
            'fear': 'DNA', 'joy': 'DNA', 'anger': 'DNA', 'sadness': 'DNA',
            'disgust': 'DNA', 'surprise': 'DNA', 'comfort': 'DNA', 'discomfort': 'DNA',
            'anxiety': 'learning', 'relief': 'learning', 'frustration': 'learning',
            'satisfaction': 'learning', 'curiosity': 'learning', 'boredom': 'learning',
            'excitement': 'learning', 'calm': 'learning', 'irritation': 'learning',
            'contentment': 'learning', 'confusion': 'learning', 'confidence': 'learning',
        }
        
        # 予測関連の新クオリア
        self.predictive_qualia = {
            'expected': 'learning',      # 予想通り
            'unexpected': 'learning',    # 予想外
            'familiar': 'learning',      # 馴染みがある
            'novel': 'learning',         # 新奇
        }
        
        # 言語マッピング
        self.word_mappings = {
            # 物理
            'freezing': '凍える', 'cold': '冷たい', 'warm': '暖かい', 'hot': '熱い', 'burning': '焼ける',
            'sweet': '甘い', 'bitter': '苦い', 'sour': '酸っぱい', 'spicy': '辛い', 'salty': '塩辛い', 'umami': '旨い',
            'pressure': '圧迫', 'pain': '痛い', 'sharp_pain': '鋭い痛み',
            'smooth': '滑らか', 'rough': 'ざらざら', 'soft': '柔らかい', 'hard': '硬い',
            'wet': '濡れてる', 'dry': '乾いてる',
            'loud': 'うるさい', 'quiet': '静か', 'high_pitch': '甲高い',
            'bright': '明るい', 'dark': '暗い', 'red': '赤い', 'blue': '青い', 'green': '緑',
            'pleasant_smell': '良い匂い', 'unpleasant_smell': '嫌な匂い',
            
            # 感情
            'fear': '怖い', 'joy': '嬉しい', 'anger': '怒り', 'sadness': '悲しい',
            'disgust': '気持ち悪い', 'surprise': '驚き', 'comfort': '心地よい', 'discomfort': '不快',
            'anxiety': '不安', 'relief': '安心', 'frustration': 'イライラ', 'satisfaction': '満足',
            'curiosity': '好奇心', 'boredom': '退屈', 'excitement': 'わくわく', 'calm': '落ち着く',
            'irritation': 'むかつく', 'contentment': '充実', 'confusion': '困惑', 'confidence': '自信',
            
            # 予測関連
            'expected': '予想通り', 'unexpected': '予想外', 'familiar': '馴染み', 'novel': '新しい',
        }
        
        # システム
        self.predictive_coding = PredictiveCoding()
        self.memory = []
        self.self_strength = 0.0
        self.feeling_reports = []
        
        # 統計
        self.qualia_counts = defaultdict(int)
        self.prediction_events = {
            'high_error': 0,
            'low_error': 0,
            'attention_triggered': 0
        }
        
        # 前回の状態（予測のため）
        self.prev_state = None
    
    def _state_to_string(self, sensor: Dict) -> str:
        """センサー入力を状態文字列に変換"""
        stim_type = sensor.get('type', 'neutral')
        if stim_type == 'neutral':
            return 'neutral'
        elif 'subtype' in sensor:
            return f"{stim_type}_{sensor['subtype']}"
        else:
            return stim_type
    
    def perceive(self, sensor: Dict) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]], List[Tuple[str, float]]]:
        """第2層: 知覚 + 予測クオリア"""
        physical = []
        emotional = []
        predictive = []
        
        # 現在の状態
        current_state = self._state_to_string(sensor)
        
        # 予測符号化の処理
        prediction_error = 0.0
        if self.prev_state is not None:
            # 前回の状態から次を予測
            predicted = self.predictive_coding.predict_next(self.prev_state)
            
            # 予測誤差を計算
            prediction_error = self.predictive_coding.calculate_error(predicted, current_state)
            
            # 注意の更新
            self.predictive_coding.update_attention(prediction_error)
            
            # 予測クオリアの追加
            if prediction_error > 0.7:
                predictive.append(('unexpected', prediction_error))
                predictive.append(('novel', prediction_error * 0.8))
                self.prediction_events['high_error'] += 1
            elif prediction_error < 0.3:
                predictive.append(('expected', 1.0 - prediction_error))
                predictive.append(('familiar', 1.0 - prediction_error))
                self.prediction_events['low_error'] += 1
            
            # 注意が向いた
            if self.predictive_coding.attention_state:
                emotional.append(('surprise', prediction_error))
                emotional.append(('curiosity', prediction_error * 0.7))
                self.prediction_events['attention_triggered'] += 1
            
            # モデルの更新（学習）
            self.predictive_coding.update_model(self.prev_state, current_state)
        
        # 通常のクオリア処理（Phase 4と同様、簡略版）
        stim_type = sensor.get('type', 'neutral')
        
        if stim_type == 'temperature':
            temp = sensor['value']
            if temp < 0:
                physical.append(('freezing', 1.0))
                emotional.append(('discomfort', 0.8))
            elif temp < 10:
                physical.append(('cold', 0.8))
            elif temp < 25:
                physical.append(('warm', 0.6))
                emotional.append(('comfort', 0.6))
            elif temp < 40:
                physical.append(('hot', 0.7))
            else:
                physical.append(('burning', 1.0))
                emotional.append(('fear', 0.9))
        
        elif stim_type == 'taste':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            physical.append((subtype, intensity))
            if subtype == 'sweet':
                emotional.append(('joy', intensity * 0.7))
        
        elif stim_type == 'pain':
            intensity = min(sensor['intensity'] / 15, 1.0)
            physical.append(('pain', intensity))
            emotional.append(('fear', intensity * 0.8))
        
        elif stim_type == 'sound':
            volume = sensor['volume']
            if volume > 8:
                physical.append(('loud', volume / 12))
                emotional.append(('irritation', (volume - 8) / 4))
        
        elif stim_type == 'texture':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            physical.append((subtype, intensity))
            if subtype in ['soft', 'smooth']:
                emotional.append(('comfort', intensity * 0.5))
        
        # カウント更新
        for quale, _ in physical + emotional + predictive:
            self.qualia_counts[quale] += 1
        
        # 次回のために状態を保存
        self.prev_state = current_state
        
        return physical, emotional, predictive
    
    def decide(self, physical: List, emotional: List, predictive: List, 
               prediction_error: float) -> str:
        """第3層: 予測符号化に基づく行動決定"""
        
        # 高誤差 → 探索的行動
        if prediction_error > 0.7:
            return 'explore'
        
        # 危険 → 回避
        for quale, intensity in physical + emotional:
            if quale in ['sharp_pain', 'burning', 'fear'] and intensity > 0.7:
                return 'avoid'
        
        # 快 → 接近
        for quale, intensity in emotional:
            if quale in ['joy', 'comfort', 'satisfaction'] and intensity > 0.6:
                return 'approach'
        
        # 予測通り → 継続
        for quale, intensity in predictive:
            if quale == 'expected' and intensity > 0.7:
                return 'continue'
        
        return 'continue'
    
    def remember(self, physical: List, emotional: List, predictive: List) -> float:
        """第4層: 記憶と自己"""
        current = (physical, emotional, predictive)
        self.memory.append(current)
        if len(self.memory) > 100:
            self.memory.pop(0)
        
        if len(self.memory) < 10:
            return 0.0
        
        similarity = self._compare(current)
        self.self_strength = min(1.0, self.self_strength + similarity * 0.01)
        return self.self_strength
    
    def _compare(self, current: Tuple) -> float:
        """類似度計算"""
        if len(self.memory) < 10:
            return 0.0
        
        recent = self.memory[-10:]
        current_p, current_e, current_pred = current
        
        matches = 0
        for past_p, past_e, past_pred in recent:
            current_set = {q for q, _ in current_p + current_e + current_pred}
            past_set = {q for q, _ in past_p + past_e + past_pred}
            if len(current_set & past_set) > 0:
                matches += 1
        
        return matches / 10
    
    def report_feeling(self, physical: List, emotional: List, predictive: List) -> Optional[str]:
        """感じの報告"""
        all_qualia = physical + emotional + predictive
        if not all_qualia:
            return None
        
        words = []
        for quale, intensity in sorted(all_qualia, key=lambda x: x[1], reverse=True)[:3]:
            if quale in self.word_mappings:
                words.append(self.word_mappings[quale])
        
        if words:
            feeling = 'と'.join(words)
            report = f"私は{feeling}と感じている"
            self.feeling_reports.append({
                'time': len(self.memory),
                'report': report
            })
            return report
        
        return None
    
    def step(self, sensor: Dict) -> Dict:
        """1ステップ実行"""
        # 第2層: 知覚 + 予測
        physical, emotional, predictive = self.perceive(sensor)
        
        # 予測誤差の取得
        prediction_error = self.predictive_coding.prediction_errors[-1] if self.predictive_coding.prediction_errors else 0.0
        
        # 第3層: 予測符号化に基づく行動決定
        action = self.decide(physical, emotional, predictive, prediction_error)
        
        # 第4層: 記憶
        self.remember(physical, emotional, predictive)
        
        # 感じの報告
        feeling_report = self.report_feeling(physical, emotional, predictive)
        
        return {
            'time': len(self.memory),
            'physical': physical,
            'emotional': emotional,
            'predictive': predictive,
            'prediction_error': prediction_error,
            'prediction_accuracy': self.predictive_coding.prediction_accuracy,
            'attention': self.predictive_coding.attention_state,
            'action': action,
            'self_strength': self.self_strength,
            'feeling_report': feeling_report
        }


def main():
    """メイン実行"""
    print("=" * 70)
    print("Phase 5: 予測符号化（Predictive Coding）")
    print("=" * 70)
    print()
    print("目標:")
    print("  1. 次の状態を予測")
    print("  2. 予測誤差を計算")
    print("  3. 誤差に基づく注意と学習")
    print("  4. より人間らしい認知")
    print()
    
    system = PredictiveConsciousness()
    environment = PredictiveEnvironment(seed=42)
    
    print("実行中（5000ステップ）...")
    print()
    
    # 報告を間引いて表示
    report_count = 0
    for t in range(5000):
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 予測関連の感じ（最初の30個）
        if result['feeling_report'] and report_count < 30:
            if result['predictive']:  # 予測クオリアがある場合のみ
                print(f"  t={result['time']:4d}: {result['feeling_report']} "
                      f"[誤差={result['prediction_error']:.2f}, 精度={result['prediction_accuracy']:.2f}]")
                report_count += 1
    
    # 結果
    print("\n" + "=" * 70)
    print("実験結果")
    print("=" * 70)
    print()
    
    print(f"最終状態:")
    print(f"  自己強度: {system.self_strength:.3f}")
    print(f"  予測精度: {system.predictive_coding.prediction_accuracy:.3f}")
    print(f"  感じの報告回数: {len(system.feeling_reports)}")
    print()
    
    print("予測イベント:")
    print(f"  高誤差イベント: {system.prediction_events['high_error']}回")
    print(f"  低誤差イベント: {system.prediction_events['low_error']}回")
    print(f"  注意発動: {system.prediction_events['attention_triggered']}回")
    print()
    
    print("クオリア出現（トップ20）:")
    for quale, count in sorted(system.qualia_counts.items(), 
                               key=lambda x: x[1], reverse=True)[:20]:
        quale_type = "予測" if quale in system.predictive_qualia else \
                     "感情" if quale in system.emotional_qualia else "物理"
        print(f"  {quale:20s} ({quale_type}): {count:4d}回")
    
    print()
    print("=" * 70)
    print("完了")
    print("=" * 70)


if __name__ == '__main__':
    main()
