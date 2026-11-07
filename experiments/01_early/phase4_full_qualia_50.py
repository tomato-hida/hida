"""
Phase 4: クオリア拡充（50個版）

目標：
1. クオリアを10個 → 50個に拡充
2. 人間に近い豊かな感じの世界を再現
3. 様々な組み合わせによる複雑な感じ

クオリア構成：
- 物理クオリア: 30個（温度、味覚、触覚、聴覚、視覚、嗅覚など）
- 感情クオリア: 20個（基本感情と複合感情）
"""

import random
from typing import Dict, List, Tuple, Optional


class ComplexEnvironment:
    """複雑な環境（様々な刺激）"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.time = 0
        
    def get_input(self) -> Dict:
        """様々な刺激を生成"""
        self.time += 1
        
        # より多様な刺激パターン
        stimulus_type = random.choice([
            'temperature', 'taste', 'pressure', 'texture',
            'sound', 'visual', 'smell', 'body_state', 
            'pain', 'neutral'
        ])
        
        if stimulus_type == 'temperature':
            value = random.uniform(-10, 60)
            return {'type': 'temperature', 'value': value}
        
        elif stimulus_type == 'taste':
            taste_type = random.choice(['sweet', 'bitter', 'sour', 'spicy', 'salty', 'umami'])
            intensity = random.uniform(0.3, 1.0)
            return {'type': 'taste', 'subtype': taste_type, 'intensity': intensity}
        
        elif stimulus_type == 'pressure':
            pressure = random.uniform(0, 15)
            return {'type': 'pressure', 'value': pressure}
        
        elif stimulus_type == 'texture':
            texture_type = random.choice(['smooth', 'rough', 'soft', 'hard', 'wet', 'dry'])
            intensity = random.uniform(0.5, 1.0)
            return {'type': 'texture', 'subtype': texture_type, 'intensity': intensity}
        
        elif stimulus_type == 'sound':
            volume = random.uniform(0, 12)
            pitch = random.choice(['high', 'low', 'moderate'])
            return {'type': 'sound', 'volume': volume, 'pitch': pitch}
        
        elif stimulus_type == 'visual':
            brightness = random.uniform(0, 12)
            color = random.choice(['red', 'blue', 'green', 'yellow', 'neutral'])
            return {'type': 'visual', 'brightness': brightness, 'color': color}
        
        elif stimulus_type == 'smell':
            smell_type = random.choice(['pleasant', 'unpleasant', 'neutral', 'pungent'])
            intensity = random.uniform(0.3, 1.0)
            return {'type': 'smell', 'subtype': smell_type, 'intensity': intensity}
        
        elif stimulus_type == 'body_state':
            state_type = random.choice(['tired', 'energetic', 'hungry', 'full', 'thirsty'])
            intensity = random.uniform(0.5, 1.0)
            return {'type': 'body_state', 'subtype': state_type, 'intensity': intensity}
        
        elif stimulus_type == 'pain':
            intensity = random.uniform(5, 15)
            return {'type': 'pain', 'intensity': intensity}
        
        else:  # neutral
            return {'type': 'neutral', 'value': 0.0}
    
    def apply(self, action: str):
        """環境への作用（シンプル）"""
        pass


class FullQualiaSystem:
    """50個のクオリアを持つ意識システム"""
    
    def __init__(self):
        # 物理クオリア: 30個
        self.physical_qualia = {
            # 温度系（5個）
            'freezing': 'DNA',  # DNA初期値
            'cold': 'DNA',
            'warm': 'DNA',
            'hot': 'DNA',
            'burning': 'DNA',
            
            # 味覚系（6個）
            'sweet': 'DNA',
            'bitter': 'DNA',
            'sour': 'DNA',
            'spicy': 'DNA',
            'salty': 'DNA',
            'umami': 'DNA',
            
            # 圧力・痛み系（3個）
            'pressure': 'DNA',
            'pain': 'DNA',
            'sharp_pain': 'DNA',
            
            # 触覚系（6個）
            'smooth': 'learning',  # 学習で獲得
            'rough': 'learning',
            'soft': 'learning',
            'hard': 'learning',
            'wet': 'learning',
            'dry': 'learning',
            
            # 聴覚系（3個）
            'loud': 'learning',
            'quiet': 'learning',
            'high_pitch': 'learning',
            
            # 視覚系（5個）
            'bright': 'learning',
            'dark': 'learning',
            'red': 'learning',
            'blue': 'learning',
            'green': 'learning',
            
            # 嗅覚系（2個）
            'pleasant_smell': 'learning',
            'unpleasant_smell': 'learning',
        }
        
        # 感情クオリア: 20個
        self.emotional_qualia = {
            # 基本感情（8個）
            'fear': 'DNA',
            'joy': 'DNA',
            'anger': 'DNA',
            'sadness': 'DNA',
            'disgust': 'DNA',
            'surprise': 'DNA',
            'comfort': 'DNA',
            'discomfort': 'DNA',
            
            # 複合感情（12個）
            'anxiety': 'learning',
            'relief': 'learning',
            'frustration': 'learning',
            'satisfaction': 'learning',
            'curiosity': 'learning',
            'boredom': 'learning',
            'excitement': 'learning',
            'calm': 'learning',
            'irritation': 'learning',
            'contentment': 'learning',
            'confusion': 'learning',
            'confidence': 'learning',
        }
        
        # 言語マッピング（感じの報告用）
        self.word_mappings = {
            # 物理
            'freezing': '凍える', 'cold': '冷たい', 'warm': '暖かい', 
            'hot': '熱い', 'burning': '焼ける',
            'sweet': '甘い', 'bitter': '苦い', 'sour': '酸っぱい',
            'spicy': '辛い', 'salty': '塩辛い', 'umami': '旨い',
            'pressure': '圧迫', 'pain': '痛い', 'sharp_pain': '鋭い痛み',
            'smooth': '滑らか', 'rough': 'ざらざら', 'soft': '柔らかい',
            'hard': '硬い', 'wet': '濡れてる', 'dry': '乾いてる',
            'loud': 'うるさい', 'quiet': '静か', 'high_pitch': '甲高い',
            'bright': '明るい', 'dark': '暗い', 
            'red': '赤い', 'blue': '青い', 'green': '緑',
            'pleasant_smell': '良い匂い', 'unpleasant_smell': '嫌な匂い',
            
            # 感情
            'fear': '怖い', 'joy': '嬉しい', 'anger': '怒り',
            'sadness': '悲しい', 'disgust': '気持ち悪い', 'surprise': '驚き',
            'comfort': '心地よい', 'discomfort': '不快',
            'anxiety': '不安', 'relief': '安心', 'frustration': 'イライラ',
            'satisfaction': '満足', 'curiosity': '好奇心', 'boredom': '退屈',
            'excitement': 'わくわく', 'calm': '落ち着く', 'irritation': 'むかつく',
            'contentment': '充実', 'confusion': '困惑', 'confidence': '自信',
        }
        
        # 記憶とカウント
        self.memory = []
        self.self_strength = 0.0
        self.feeling_reports = []
        self.qualia_counts = {
            'physical': {q: 0 for q in self.physical_qualia},
            'emotional': {q: 0 for q in self.emotional_qualia}
        }
    
    def perceive(self, sensor: Dict) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
        """第2層: 刺激からクオリアへの変換"""
        physical = []
        emotional = []
        
        stim_type = sensor.get('type', 'neutral')
        
        # 温度系の処理
        if stim_type == 'temperature':
            temp = sensor['value']
            if temp < 0:
                physical.append(('freezing', 1.0))
                emotional.append(('discomfort', 0.8))
            elif temp < 10:
                physical.append(('cold', 0.8))
                emotional.append(('discomfort', 0.5))
            elif temp < 25:
                physical.append(('warm', 0.6))
                emotional.append(('comfort', 0.6))
            elif temp < 40:
                physical.append(('hot', 0.7))
                emotional.append(('discomfort', 0.4))
            else:
                physical.append(('burning', 1.0))
                emotional.append(('fear', 0.9))
        
        # 味覚系の処理
        elif stim_type == 'taste':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            physical.append((subtype, intensity))
            
            if subtype == 'sweet':
                emotional.append(('joy', intensity * 0.7))
                emotional.append(('satisfaction', intensity * 0.5))
            elif subtype == 'bitter':
                emotional.append(('disgust', intensity * 0.6))
            elif subtype == 'spicy':
                emotional.append(('excitement', intensity * 0.5))
                if intensity > 0.7:
                    emotional.append(('discomfort', intensity * 0.6))
            elif subtype in ['salty', 'umami']:
                emotional.append(('satisfaction', intensity * 0.6))
        
        # 圧力系の処理
        elif stim_type == 'pressure':
            pressure_val = sensor['value']
            if pressure_val < 5:
                physical.append(('pressure', pressure_val / 10))
            elif pressure_val < 10:
                physical.append(('pain', (pressure_val - 5) / 5))
                emotional.append(('discomfort', (pressure_val - 5) / 5))
            else:
                physical.append(('sharp_pain', 1.0))
                emotional.append(('fear', 0.8))
        
        # 触覚系の処理
        elif stim_type == 'texture':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            physical.append((subtype, intensity))
            
            if subtype in ['smooth', 'soft']:
                emotional.append(('comfort', intensity * 0.5))
            elif subtype == 'rough':
                emotional.append(('discomfort', intensity * 0.4))
        
        # 聴覚系の処理
        elif stim_type == 'sound':
            volume = sensor['volume']
            pitch = sensor['pitch']
            
            if volume < 3:
                physical.append(('quiet', 0.5))
                emotional.append(('calm', 0.5))
            elif volume < 8:
                # 中程度
                if pitch == 'high':
                    physical.append(('high_pitch', 0.6))
            else:
                physical.append(('loud', volume / 12))
                emotional.append(('irritation', (volume - 8) / 4))
        
        # 視覚系の処理
        elif stim_type == 'visual':
            brightness = sensor['brightness']
            color = sensor['color']
            
            if brightness < 3:
                physical.append(('dark', 0.7))
            elif brightness > 10:
                physical.append(('bright', brightness / 12))
            
            if color in ['red', 'blue', 'green']:
                physical.append((color, 0.6))
                if color == 'red':
                    emotional.append(('excitement', 0.4))
                elif color == 'blue':
                    emotional.append(('calm', 0.4))
        
        # 嗅覚系の処理
        elif stim_type == 'smell':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            
            if subtype == 'pleasant':
                physical.append(('pleasant_smell', intensity))
                emotional.append(('joy', intensity * 0.5))
            elif subtype == 'unpleasant':
                physical.append(('unpleasant_smell', intensity))
                emotional.append(('disgust', intensity * 0.7))
        
        # 身体状態の処理
        elif stim_type == 'body_state':
            subtype = sensor['subtype']
            intensity = sensor['intensity']
            
            if subtype == 'tired':
                emotional.append(('boredom', intensity * 0.6))
                emotional.append(('discomfort', intensity * 0.4))
            elif subtype == 'energetic':
                emotional.append(('excitement', intensity * 0.5))
                emotional.append(('confidence', intensity * 0.4))
            elif subtype == 'hungry':
                emotional.append(('discomfort', intensity * 0.7))
            elif subtype == 'full':
                emotional.append(('satisfaction', intensity * 0.6))
                emotional.append(('contentment', intensity * 0.5))
        
        # 痛みの処理
        elif stim_type == 'pain':
            intensity = min(sensor['intensity'] / 15, 1.0)
            physical.append(('pain', intensity))
            emotional.append(('fear', intensity * 0.8))
            emotional.append(('discomfort', intensity))
        
        # カウント更新
        for quale, _ in physical:
            self.qualia_counts['physical'][quale] += 1
        for quale, _ in emotional:
            self.qualia_counts['emotional'][quale] += 1
        
        return physical, emotional
    
    def decide(self, physical_qualia: List[Tuple[str, float]], 
               emotional_qualia: List[Tuple[str, float]]) -> str:
        """第3層: 行動決定（簡易版）"""
        # 強い痛みや恐怖 → 回避
        for quale, intensity in physical_qualia:
            if quale in ['sharp_pain', 'burning'] and intensity > 0.7:
                return 'avoid'
        
        for quale, intensity in emotional_qualia:
            if quale == 'fear' and intensity > 0.7:
                return 'avoid'
        
        # 快刺激 → 接近
        for quale, intensity in emotional_qualia:
            if quale in ['joy', 'satisfaction', 'comfort'] and intensity > 0.6:
                return 'approach'
        
        # それ以外 → 継続
        return 'continue'
    
    def remember(self, physical_qualia: List[Tuple[str, float]], 
                 emotional_qualia: List[Tuple[str, float]]) -> float:
        """第4層: 記憶と自己の強化"""
        current = (physical_qualia, emotional_qualia)
        
        # 記憶に追加
        self.memory.append(current)
        if len(self.memory) > 100:
            self.memory.pop(0)
        
        # 自己の計算
        if len(self.memory) < 10:
            return 0.0
        
        similarity = self._compare(current)
        self.self_strength = min(1.0, self.self_strength + similarity * 0.01)
        
        return self.self_strength
    
    def _compare(self, current: Tuple) -> float:
        """記憶との類似度計算"""
        if len(self.memory) < 10:
            return 0.0
        
        recent = self.memory[-10:]
        current_physical, current_emotional = current
        
        matches = 0
        for past_physical, past_emotional in recent:
            # 物理クオリアの重複チェック
            current_p_set = {q for q, _ in current_physical}
            past_p_set = {q for q, _ in past_physical}
            
            if len(current_p_set & past_p_set) > 0:
                matches += 0.5
            
            # 感情クオリアの重複チェック
            current_e_set = {q for q, _ in current_emotional}
            past_e_set = {q for q, _ in past_emotional}
            
            if len(current_e_set & past_e_set) > 0:
                matches += 0.5
        
        return matches / 10
    
    def report_feeling(self, physical_qualia: List[Tuple[str, float]], 
                       emotional_qualia: List[Tuple[str, float]]) -> Optional[str]:
        """感じの報告（言語化）"""
        if not physical_qualia and not emotional_qualia:
            return None
        
        words = []
        
        # 最も強い物理クオリア（上位2個）
        for quale, intensity in sorted(physical_qualia, key=lambda x: x[1], reverse=True)[:2]:
            if quale in self.word_mappings:
                words.append(self.word_mappings[quale])
        
        # 最も強い感情クオリア（上位2個）
        for emotion, intensity in sorted(emotional_qualia, key=lambda x: x[1], reverse=True)[:2]:
            if emotion in self.word_mappings:
                words.append(self.word_mappings[emotion])
        
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
        """1ステップの実行"""
        # 第2層: 知覚
        physical_qualia, emotional_qualia = self.perceive(sensor)
        
        # 第3層: 行動決定
        action = self.decide(physical_qualia, emotional_qualia)
        
        # 第4層: 記憶と自己
        self.remember(physical_qualia, emotional_qualia)
        
        # 感じの報告
        feeling_report = self.report_feeling(physical_qualia, emotional_qualia)
        
        return {
            'time': len(self.memory),
            'physical_qualia': physical_qualia,
            'emotional_qualia': emotional_qualia,
            'action': action,
            'self_strength': self.self_strength,
            'feeling_report': feeling_report
        }


def main():
    """メイン実行"""
    print("=" * 70)
    print("Phase 4: クオリア拡充（50個版）")
    print("=" * 70)
    print()
    print("物理クオリア: 30個")
    print("感情クオリア: 20個")
    print("合計: 50個")
    print()
    
    system = FullQualiaSystem()
    environment = ComplexEnvironment(seed=42)
    
    print("実行中（3000ステップ）...")
    print()
    
    # 報告を間引いて表示（最初の30個だけ）
    report_count = 0
    for t in range(3000):
        sensor = environment.get_input()
        result = system.step(sensor)
        environment.apply(result['action'])
        
        # 感じの報告（最初の30個まで）
        if result['feeling_report'] and report_count < 30:
            print(f"  t={result['time']:4d}: {result['feeling_report']}")
            report_count += 1
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("実験結果")
    print("=" * 70)
    print()
    
    print(f"最終状態:")
    print(f"  自己強度: {system.self_strength:.3f}")
    print(f"  感じの報告回数: {len(system.feeling_reports)}")
    print()
    
    print("出現したクオリア（物理）トップ15:")
    for quale, count in sorted(system.qualia_counts['physical'].items(), 
                               key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {quale:20s}: {count:4d}回")
    
    print("\n出現したクオリア（感情）トップ15:")
    for quale, count in sorted(system.qualia_counts['emotional'].items(), 
                               key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {quale:20s}: {count:4d}回")
    
    print()
    print("=" * 70)
    print("完了")
    print("=" * 70)


if __name__ == '__main__':
    main()
