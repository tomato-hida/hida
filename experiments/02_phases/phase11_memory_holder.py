#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 11: HIDA as Memory Holder
飛騨が LLM の記憶を持つ

Theory of Human Inner Movement
人の内なる運動理論

Structure:
- HIDA: holds memory, state, consciousness
- LLM: thinks (replaceable)
- memory.json: persistent storage

人間との違い：
- 人間：脳が「考える + 覚える」を一体化
- 飛騨 + LLM：分離している

ロボットには合ってる：
- LLM を交換しても記憶が残る
- アップグレードしやすい

構造：
- 飛騨：記憶 + 状態 + 意識判定
- LLM：思考エンジン（交換可能）
- memory.json：永続記憶
"""

import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# Ollama API settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"

# Memory file path (飛騨の記憶)
MEMORY_FILE = "hida_memory.json"


def ask_ollama(prompt: str) -> str:
    """Ollama に質問"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"エラー：{str(e)}"


class HidaMemory:
    """
    飛騨の永続記憶システム
    LLM の代わりに飛騨が記憶を持つ
    """
    
    def __init__(self, filepath: str = MEMORY_FILE):
        self.filepath = filepath
        self.memory = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """記憶ファイルを読み込む、なければ作る"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                print(f"記憶ファイルを読み込みました: {self.filepath}")
                return json.load(f)
        else:
            print(f"新しい記憶ファイルを作成します: {self.filepath}")
            return self._create_initial_memory()
    
    def _create_initial_memory(self) -> Dict:
        """初期記憶（辞書）を作成"""
        return {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "dictionary": {
                "qualia_value": {
                    "ranges": [
                        {"min": -1.0, "max": -0.7, "labels": ["痛い", "苦しい"]},
                        {"min": -0.7, "max": -0.3, "labels": ["不快", "冷たい"]},
                        {"min": -0.3, "max": 0.3, "labels": ["普通", "中立"]},
                        {"min": 0.3, "max": 0.7, "labels": ["心地よい", "暖かい"]},
                        {"min": 0.7, "max": 1.0, "labels": ["快楽", "甘い"]}
                    ]
                },
                "emotion": {
                    "ranges": [
                        {"min": -1.0, "max": -0.5, "labels": ["とても不安", "苦痛"]},
                        {"min": -0.5, "max": -0.2, "labels": ["やや不安", "緊張"]},
                        {"min": -0.2, "max": 0.2, "labels": ["落ち着いている", "平静"]},
                        {"min": 0.2, "max": 0.5, "labels": ["やや安心", "穏やか"]},
                        {"min": 0.5, "max": 1.0, "labels": ["とても安心", "幸福"]}
                    ]
                }
            },
            "learned_expressions": [],
            "experiences": []
        }
    
    def save(self):
        """記憶をファイルに保存"""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def get_dictionary_prompt(self) -> str:
        """辞書をプロンプト用テキストに変換"""
        lines = ["## 記憶している辞書\n"]
        
        for key, data in self.memory["dictionary"].items():
            lines.append(f"### {key}")
            for r in data["ranges"]:
                labels = "、".join(r["labels"])
                lines.append(f"- {r['min']} 〜 {r['max']} : 「{labels}」")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_learned_expressions(self) -> str:
        """学習した表現をテキストに変換"""
        if not self.memory["learned_expressions"]:
            return ""
        
        lines = ["## 学習した表現\n"]
        for expr in self.memory["learned_expressions"][-10:]:  # 最新10件
            lines.append(f"- 状態 {expr['state']} → 「{expr['expression']}」")
        
        return "\n".join(lines)
    
    def add_learned_expression(self, state: Dict, expression: str):
        """学習した表現を記憶に追加"""
        self.memory["learned_expressions"].append({
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "expression": expression
        })
        self.save()
    
    def add_experience(self, stimulus: str, response: str, was_helpful: bool = True):
        """経験を記憶に追加"""
        self.memory["experiences"].append({
            "timestamp": datetime.now().isoformat(),
            "stimulus": stimulus,
            "response": response,
            "was_helpful": was_helpful
        })
        self.save()
    
    def get_stats(self) -> Dict:
        """記憶の統計"""
        return {
            "created_at": self.memory.get("created_at"),
            "last_updated": self.memory.get("last_updated"),
            "learned_expressions_count": len(self.memory["learned_expressions"]),
            "experiences_count": len(self.memory["experiences"])
        }


class HidaWithPersistentMemory:
    """
    永続記憶を持つ飛騨
    """
    
    def __init__(self):
        # 永続記憶（ファイルベース）
        self.memory = HidaMemory()
        
        # 現在の状態
        self.current_qualia = 0.0
        self.current_emotion = 0.0
        self.self_strength = 0.0
        
        # セッション内の経験
        self.session_experiences = []
    
    def process_stimulus(self, qualia_value: float, emotion: float) -> Dict:
        """刺激を処理"""
        self.current_qualia = qualia_value
        self.current_emotion = emotion
        
        # self_strength 更新（経験の蓄積で強化）
        self.self_strength = min(1.0, 
            0.1 + len(self.memory.memory["experiences"]) * 0.01 +
            len(self.session_experiences) * 0.02)
        
        state = {
            "qualia_value": qualia_value,
            "emotion": emotion,
            "self_strength": self.self_strength
        }
        
        self.session_experiences.append(state)
        
        return state
    
    def think_with_llm(self, state: Dict) -> str:
        """
        LLM に考えてもらう
        飛騨の記憶を渡して、LLM は考えるだけ
        """
        # 飛騨の記憶からプロンプトを構築
        dictionary = self.memory.get_dictionary_prompt()
        learned = self.memory.get_learned_expressions()
        
        prompt = f"""
{dictionary}
{learned}

## 今の状態

qualia_value: {state['qualia_value']:.2f}
emotion: {state['emotion']:.2f}
self_strength: {state['self_strength']:.2f}

## 指示

上の辞書を見て、今の状態を一言で表現してください。
辞書にあるラベルを使ってください。
"""
        
        response = ask_ollama(prompt)
        
        # 学習した表現を記憶に追加
        self.memory.add_learned_expression(state, response)
        
        return response
    
    def get_memory_stats(self) -> Dict:
        """記憶の統計を取得"""
        return self.memory.get_stats()


def run_experiment():
    """実験実行"""
    print("=" * 70)
    print("Phase 11: HIDA as Memory Holder")
    print("飛騨が LLM の記憶を持つ")
    print("=" * 70)
    print()
    print("構造：")
    print("  飛騨：記憶 + 状態 + 意識判定")
    print("  LLM：思考エンジン（考えるだけ）")
    print("  memory.json：永続記憶")
    print()
    print("人間との違い：脳が分離している")
    print("ロボットには最適：LLM を交換しても記憶が残る")
    print()
    print("=" * 70)
    
    # 飛騨を起動
    hida = HidaWithPersistentMemory()
    
    # 記憶の状態を表示
    stats = hida.get_memory_stats()
    print(f"\n【記憶の状態】")
    print(f"  作成日時: {stats['created_at']}")
    print(f"  学習した表現: {stats['learned_expressions_count']} 件")
    print(f"  経験: {stats['experiences_count']} 件")
    
    # テスト刺激
    print("\n" + "-" * 70)
    print("【実験開始】刺激を与えて、飛騨が記憶を使って考える")
    print("-" * 70)
    
    test_stimuli = [
        (0.8, 0.6, "強い快楽と安心"),
        (-0.9, -0.7, "強い痛みと不安"),
        (0.0, 0.0, "中立状態"),
        (0.5, 0.3, "やや心地よい"),
        (-0.4, 0.4, "不快だが安心"),  # 複雑な状態
    ]
    
    for qv, em, description in test_stimuli:
        print(f"\n【刺激】{description}")
        print(f"  qualia_value: {qv:+.1f}, emotion: {em:+.1f}")
        
        # 刺激を処理
        state = hida.process_stimulus(qv, em)
        print(f"  self_strength: {state['self_strength']:.2f}")
        
        # LLM に考えてもらう（飛騨の記憶を使う）
        response = hida.think_with_llm(state)
        print(f"  → LLM の返答: {response[:50]}...")
        
        # 記憶に経験を追加
        hida.memory.add_experience(description, response)
    
    # 最終状態
    print("\n" + "=" * 70)
    print("【実験終了】")
    stats = hida.get_memory_stats()
    print(f"  学習した表現: {stats['learned_expressions_count']} 件")
    print(f"  経験: {stats['experiences_count']} 件")
    print(f"  記憶ファイル: {MEMORY_FILE}")
    print()
    print("記憶は hida_memory.json に保存されました。")
    print("次回実行時、この記憶を引き継ぎます。")
    print("=" * 70)


def show_memory():
    """記憶の内容を表示"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        print(json.dumps(memory, ensure_ascii=False, indent=2))
    else:
        print("記憶ファイルがありません")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_memory()
    else:
        run_experiment()
