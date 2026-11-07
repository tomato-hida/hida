#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 11b: HIDA Learns from Human
飛騨が人間から学ぶ

Theory of Human Inner Movement
人の内なる運動理論

改良点：
- 知ってる状態 → 記憶から直接答える（LLM 使わない）
- 知らない状態 → 「わかりません」と言う → 人間が教える
- 人間が教えたことを記憶に保存
- 次からは自分で答えられる

これが本当の「言語継承」
- LLM = 思考の補助（推測するだけ）
- 人間 = 本当の先生（新しい言葉を教える）
"""

import json
import os
from typing import Dict, Optional, Tuple
from datetime import datetime

# Memory file path
MEMORY_FILE = "hida_memory_v2.json"


class HidaMemoryV2:
    """
    飛騨の永続記憶システム v2
    人間から学ぶ版
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
        """初期記憶（DNA的な基本クオリア）"""
        return {
            "created_at": datetime.now().isoformat(),
            "version": "2.0",
            "learned_from_human": [
                # DNA的な初期値（生まれつき知ってること）
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": 0.9, "emotion": 0.8},
                    "label": "とても気持ちよくて幸せ",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": -0.9, "emotion": -0.8},
                    "label": "痛くて怖い",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": 0.0, "emotion": 0.0},
                    "label": "普通",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": 0.5, "emotion": 0.4},
                    "label": "心地よくて安心",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": -0.5, "emotion": -0.4},
                    "label": "不快で不安",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": 0.6, "emotion": -0.3},
                    "label": "気持ちいいけど緊張",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": -0.4, "emotion": 0.5},
                    "label": "不快だけど安心",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": 0.3, "emotion": 0.0},
                    "label": "ちょっと心地よい",
                    "taught_by": "DNA"
                },
                {
                    "timestamp": "initial",
                    "state": {"qualia_value": -0.3, "emotion": 0.0},
                    "label": "ちょっと不快",
                    "taught_by": "DNA"
                },
            ],
            "query_count": 0,
            "answer_from_memory_count": 0,
            "asked_human_count": 0
        }
    
    def save(self):
        """記憶をファイルに保存"""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def find_similar_state(self, qv: float, em: float, threshold: float = 0.15) -> Optional[Dict]:
        """
        似た状態を記憶から探す
        threshold: この範囲内なら「同じ状態」とみなす
        """
        for item in self.memory["learned_from_human"]:
            stored_qv = item["state"]["qualia_value"]
            stored_em = item["state"]["emotion"]
            
            if abs(stored_qv - qv) <= threshold and abs(stored_em - em) <= threshold:
                return item
        
        return None
    
    def learn_from_human(self, qv: float, em: float, label: str):
        """人間から教わったことを記憶に追加"""
        self.memory["learned_from_human"].append({
            "timestamp": datetime.now().isoformat(),
            "state": {
                "qualia_value": qv,
                "emotion": em
            },
            "label": label,
            "taught_by": "human"
        })
        self.memory["asked_human_count"] += 1
        self.save()
    
    def get_stats(self) -> Dict:
        """統計"""
        total = self.memory["query_count"]
        from_memory = self.memory["answer_from_memory_count"]
        from_human = self.memory["asked_human_count"]
        
        independence = (from_memory / total * 100) if total > 0 else 0
        
        return {
            "learned_count": len(self.memory["learned_from_human"]),
            "query_count": total,
            "answer_from_memory": from_memory,
            "asked_human": from_human,
            "independence_rate": independence
        }


class HidaLearnsFromHuman:
    """
    人間から学ぶ飛騨
    """
    
    def __init__(self):
        self.memory = HidaMemoryV2()
        self.current_qv = 0.0
        self.current_em = 0.0
    
    def receive_stimulus(self, qv: float, em: float) -> Tuple[str, str]:
        """
        刺激を受け取る
        
        Returns:
            (答え, ソース)
            ソース: "memory" = 記憶から, "unknown" = わからない
        """
        self.current_qv = qv
        self.current_em = em
        self.memory.memory["query_count"] += 1
        
        # 記憶を検索
        found = self.memory.find_similar_state(qv, em)
        
        if found:
            # 知ってる！記憶から答える
            self.memory.memory["answer_from_memory_count"] += 1
            self.memory.save()
            return found["label"], "memory"
        else:
            # 知らない…人間に聞く
            return "わかりません。教えてください。", "unknown"
    
    def learn(self, label: str):
        """人間から教わる"""
        self.memory.learn_from_human(self.current_qv, self.current_em, label)
        print(f"  → 覚えました: ({self.current_qv:+.1f}, {self.current_em:+.1f}) = 「{label}」")


def interactive_mode():
    """対話モード"""
    print("=" * 70)
    print("Phase 11b: HIDA Learns from Human")
    print("飛騨が人間から学ぶ")
    print("=" * 70)
    print()
    print("使い方：")
    print("  数値を入力 → 飛騨が答えるか「わからない」と言う")
    print("  「わからない」と言ったら → あなたが教える")
    print("  'q' で終了、's' で統計表示、'l' で学習内容一覧")
    print()
    print("=" * 70)
    
    hida = HidaLearnsFromHuman()
    
    # 統計表示
    stats = hida.memory.get_stats()
    print(f"\n【記憶の状態】")
    print(f"  学習済み: {stats['learned_count']} 件")
    print(f"  自立率: {stats['independence_rate']:.1f}%")
    print()
    
    while True:
        print("-" * 40)
        
        # qualia_value 入力
        qv_input = input("qualia_value (-1.0 〜 +1.0): ").strip()
        
        if qv_input.lower() == 'q':
            break
        elif qv_input.lower() == 's':
            stats = hida.memory.get_stats()
            print(f"\n【統計】")
            print(f"  学習済み: {stats['learned_count']} 件")
            print(f"  質問回数: {stats['query_count']} 回")
            print(f"  記憶から回答: {stats['answer_from_memory']} 回")
            print(f"  人間に質問: {stats['asked_human']} 回")
            print(f"  自立率: {stats['independence_rate']:.1f}%")
            continue
        elif qv_input.lower() == 'l':
            print(f"\n【学習内容】")
            for item in hida.memory.memory["learned_from_human"]:
                qv = item["state"]["qualia_value"]
                em = item["state"]["emotion"]
                label = item["label"]
                print(f"  ({qv:+.1f}, {em:+.1f}) → 「{label}」")
            continue
        
        try:
            qv = float(qv_input)
        except ValueError:
            print("数値を入力してください")
            continue
        
        # emotion 入力
        em_input = input("emotion (-1.0 〜 +1.0): ").strip()
        
        try:
            em = float(em_input)
        except ValueError:
            print("数値を入力してください")
            continue
        
        # 刺激を与える
        print(f"\n【刺激】qv={qv:+.1f}, em={em:+.1f}")
        answer, source = hida.receive_stimulus(qv, em)
        
        if source == "memory":
            print(f"  → 飛騨の答え: 「{answer}」 [★記憶から]")
        else:
            print(f"  → 飛騨: {answer}")
            # 人間が教える
            label = input("  → あなたが教える（ラベル）: ").strip()
            if label:
                hida.learn(label)
    
    # 終了時の統計
    print("\n" + "=" * 70)
    print("【終了】")
    stats = hida.memory.get_stats()
    print(f"  学習済み: {stats['learned_count']} 件")
    print(f"  質問回数: {stats['query_count']} 回")
    print(f"  記憶から回答: {stats['answer_from_memory']} 回")
    print(f"  人間に質問: {stats['asked_human']} 回")
    print(f"  自立率: {stats['independence_rate']:.1f}%")
    print(f"\n記憶は {MEMORY_FILE} に保存されました。")
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
        interactive_mode()
