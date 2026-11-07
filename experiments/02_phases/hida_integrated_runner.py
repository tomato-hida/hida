#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HIDA Integrated Runner
飛騨 統合ランナー

言語コマンド → 行動コード → シミュレーション
Phase 12 + Phase 13 の一気通貫

使い方：
  python hida_integrated_runner.py

例：
  「ボールを拾って」→ pick_up → ロボットがボールを拾う
"""

import json
import os
from typing import Optional, Tuple

# Phase 13 のシミュレーション
import pybullet as p
import pybullet_data
import time
import math


# ============================================================
# Phase 12: 言語 → 行動コード（簡易版）
# ============================================================

class LanguageToAction:
    """
    言語コマンドを行動コードに変換
    Phase 12 の簡易版（メモリファイル不要）
    未知コマンドは人間に聞いて学習
    """
    
    def __init__(self):
        # 基本的な言語 → 行動マッピング
        self.mappings = [
            (["運んで", "運べ", "持っていって"], "carry"),
            (["持ってて", "持っていて", "ホールド"], "hold"),
            (["ついてきて", "ついてこい", "フォロー"], "follow"),
            (["止まれ", "止まって", "ストップ", "停止"], "stop"),
            (["取って", "取れ", "拾って", "拾え"], "pick_up"),
            (["置いて", "置け", "下ろして"], "put_down"),
            (["来て", "こっち", "おいで"], "come"),
            (["待って", "待て", "ウェイト"], "wait"),
            (["探して", "探せ", "見つけて"], "search"),
            (["見て", "見ろ", "確認して"], "look"),
            (["持ってきて", "取ってきて", "フェッチ"], "fetch"),
        ]
        
        # 行動の説明
        self.action_names = {
            "carry": "運ぶ",
            "hold": "保持する",
            "follow": "追従する",
            "stop": "停止する",
            "pick_up": "拾う",
            "put_down": "置く",
            "come": "来る",
            "wait": "待機する",
            "search": "探す",
            "look": "見る",
            "fetch": "取ってくる",
        }
        
        # 利用可能な行動コード
        self.available_actions = list(self.action_names.keys())
    
    def understand(self, command: str) -> Tuple[str, str]:
        """
        コマンドを理解して行動コードを返す
        Returns: (action_code, action_name)
        """
        command_lower = command.lower()
        
        for keywords, action in self.mappings:
            for keyword in keywords:
                if keyword in command_lower:
                    return action, self.action_names.get(action, action)
        
        return "unknown", "不明"
    
    def learn(self, keyword: str, action: str):
        """新しいキーワードを学習"""
        # 既存の action にキーワード追加を試みる
        for mapping in self.mappings:
            if mapping[1] == action:
                mapping[0].append(keyword)
                print(f"  → 学習: 「{keyword}」 → {action}")
                return
        
        # なければ新規追加
        self.mappings.append(([keyword], action))
        print(f"  → 学習: 「{keyword}」 → {action}")


# ============================================================
# Phase 13: シミュレーション（修正版）
# ============================================================

class HidaRobotSimulation:
    """
    飛騨のロボットシミュレーション
    """
    
    def __init__(self):
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)
        
        self.plane_id = p.loadURDF("plane.urdf")
        self.robot_id = self._create_simple_robot()
        self.ball_id = self._create_ball([2, 0, 0.5])
        
        self.is_holding = False
        
        print("シミュレーション開始")
    
    def _create_simple_robot(self):
        collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1])
        visual_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1], 
                                           rgbaColor=[0.2, 0.4, 0.8, 1])
        robot_id = p.createMultiBody(
            baseMass=1,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=[0, 0, 0.2]
        )
        return robot_id
    
    def _create_ball(self, position):
        collision_shape = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        visual_shape = p.createVisualShape(p.GEOM_SPHERE, radius=0.2,
                                           rgbaColor=[0.9, 0.2, 0.2, 1])
        ball_id = p.createMultiBody(
            baseMass=0.5,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=position
        )
        return ball_id
    
    def get_robot_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        return pos
    
    def get_ball_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.ball_id)
        return pos
    
    def execute_action(self, action: str) -> str:
        """行動コードを実行（テーブル駆動）"""
        action_handlers = {
            "search": self._action_search,
            "pick_up": self._action_pick_up,
            "carry": self._action_carry,
            "put_down": self._action_put_down,
            "stop": self._action_stop,
            "come": self._action_come,
            "wait": self._action_wait,
            "follow": self._action_follow,
            "fetch": self._action_fetch,
            "hold": self._action_hold,
            "look": self._action_look,
        }
        
        handler = action_handlers.get(action)
        if handler:
            return handler()
        else:
            return f"未対応の行動: {action}"
    
    def _move_robot_to(self, target_x, target_y, steps=100):
        for i in range(steps):
            current_pos = self.get_robot_position()
            dx = target_x - current_pos[0]
            dy = target_y - current_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.1:
                break
            
            speed = 0.05
            new_x = current_pos[0] + (dx / distance) * speed
            new_y = current_pos[1] + (dy / distance) * speed
            
            p.resetBasePositionAndOrientation(
                self.robot_id, [new_x, new_y, 0.2], [0, 0, 0, 1]
            )
            
            if self.is_holding:
                p.resetBasePositionAndOrientation(
                    self.ball_id, [new_x, new_y, 0.5], [0, 0, 0, 1]
                )
            
            p.stepSimulation()
            time.sleep(0.02)
    
    def _action_search(self):
        print("周囲を探索中...")
        ball_pos = self.get_ball_position()
        self._move_robot_to(ball_pos[0] * 0.3, ball_pos[1] * 0.3, steps=50)
        robot_pos = self.get_robot_position()
        distance = math.sqrt(
            (ball_pos[0] - robot_pos[0])**2 + 
            (ball_pos[1] - robot_pos[1])**2
        )
        return f"ボールを発見！距離: {distance:.1f}m"
    
    def _action_pick_up(self):
        print("ボールを拾いに行きます...")
        ball_pos = self.get_ball_position()
        self._move_robot_to(ball_pos[0], ball_pos[1], steps=100)
        self.is_holding = True
        p.resetBasePositionAndOrientation(
            self.ball_id, [ball_pos[0], ball_pos[1], 0.5], [0, 0, 0, 1]
        )
        return "ボールを拾いました"
    
    def _action_carry(self):
        if not self.is_holding:
            return "何も持っていません"
        print("運搬中...")
        self._move_robot_to(0, 0, steps=100)
        return "運搬完了"
    
    def _action_put_down(self):
        if not self.is_holding:
            return "何も持っていません"
        print("ボールを置きます...")
        robot_pos = self.get_robot_position()
        p.resetBasePositionAndOrientation(
            self.ball_id, [robot_pos[0] + 0.5, robot_pos[1], 0.2], [0, 0, 0, 1]
        )
        self.is_holding = False
        return "ボールを置きました"
    
    def _action_stop(self):
        print("停止")
        time.sleep(0.5)
        return "停止しました"
    
    def _action_come(self):
        print("原点に向かいます...")
        self._move_robot_to(0, 0, steps=100)
        return "到着しました"
    
    def _action_wait(self):
        print("待機中...")
        for _ in range(50):
            p.stepSimulation()
            time.sleep(0.02)
        return "待機しています"
    
    def _action_follow(self):
        print("追従中...")
        for _ in range(3):
            ball_pos = self.get_ball_position()
            self._move_robot_to(ball_pos[0], ball_pos[1], steps=30)
        return "追従完了"
    
    def _action_fetch(self):
        """取ってくる：拾って戻る"""
        print("取りに行きます...")
        self._action_pick_up()
        print("戻ります...")
        self._move_robot_to(0, 0, steps=100)
        return "持ってきました"
    
    def _action_hold(self):
        """保持する：現在の状態を維持"""
        if self.is_holding:
            print("ボールを保持中...")
            for _ in range(50):
                p.stepSimulation()
                time.sleep(0.02)
            return "ボールを保持しています"
        else:
            return "何も持っていません"
    
    def _action_look(self):
        """見る：状態を確認"""
        print("確認中...")
        robot_pos = self.get_robot_position()
        ball_pos = self.get_ball_position()
        distance = math.sqrt(
            (ball_pos[0] - robot_pos[0])**2 + 
            (ball_pos[1] - robot_pos[1])**2
        )
        holding = "持っている" if self.is_holding else "持っていない"
        return f"ロボット位置: ({robot_pos[0]:.1f}, {robot_pos[1]:.1f}), ボール距離: {distance:.1f}m, 状態: {holding}"
    
    def close(self):
        p.disconnect()
        print("シミュレーション終了")


# ============================================================
# 統合ランナー
# ============================================================

class HidaIntegratedRunner:
    """
    飛騨 統合ランナー
    言語 → 行動コード → シミュレーション
    """
    
    def __init__(self):
        print("=" * 60)
        print("HIDA Integrated Runner")
        print("飛騨 統合ランナー")
        print("=" * 60)
        print()
        print("言語コマンド → 行動コード → シミュレーション")
        print()
        
        # Phase 12: 言語理解
        self.language = LanguageToAction()
        
        # Phase 13: シミュレーション
        self.simulation = HidaRobotSimulation()
    
    def run_command(self, command: str) -> str:
        """
        言語コマンドを受け取って実行
        """
        print(f"\n【入力】「{command}」")
        
        # Phase 12: 言語 → 行動コード
        action, action_name = self.language.understand(command)
        
        if action == "unknown":
            # 未知のコマンド → 人間に聞く
            print(f"【理解】わかりません。教えてください。")
            print(f"  選択肢: {', '.join(self.language.available_actions)}")
            
            user_action = input("  どの行動？: ").strip().lower()
            
            if user_action in self.language.available_actions:
                self.language.learn(command, user_action)
                action = user_action
                action_name = self.language.action_names.get(action, action)
            else:
                return "学習をスキップしました"
        
        print(f"【理解】{action} ({action_name})")
        
        # Phase 13: 行動コード → シミュレーション
        print(f"【実行】")
        result = self.simulation.execute_action(action)
        
        return result
    
    def run_interactive(self):
        """対話モード"""
        print("\n" + "-" * 60)
        print("日本語でコマンドを入力してください")
        print("例: 「ボールを探して」「拾って」「運んで」「置いて」")
        print("'q' で終了")
        print("-" * 60)
        
        while True:
            try:
                command = input("\nコマンド: ").strip()
                
                if command.lower() == 'q':
                    break
                
                if command:
                    result = self.run_command(command)
                    print(f"【結果】{result}")
                
            except KeyboardInterrupt:
                break
        
        self.close()
    
    def close(self):
        self.simulation.close()


def demo():
    """デモ実行"""
    runner = HidaIntegratedRunner()
    
    print("\n【デモ開始】")
    print("日本語コマンドでロボットを動かします")
    time.sleep(3)
    
    commands = [
        "ボールを探して",
        "拾って",
        "運んで",
        "置いて",
        "こっちに来て",
    ]
    
    for cmd in commands:
        result = runner.run_command(cmd)
        print(f"【結果】{result}")
        time.sleep(1)
    
    print("\n【デモ終了】")
    time.sleep(5)
    runner.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        runner = HidaIntegratedRunner()
        runner.run_interactive()
