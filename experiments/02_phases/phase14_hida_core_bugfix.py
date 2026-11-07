#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 14: HIDA Core Architecture
飛騨アーキテクチャ本体

L1〜L5 が常時ループ
予測誤差で意識が ON/OFF
行動は「決める」んじゃなく「生まれる」

これが本物の飛騨
"""

import time
import math
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# シミュレーション用
import pybullet as p
import pybullet_data


class ConsciousnessState(Enum):
    """意識状態"""
    IDLE = "待機"          # 予測誤差なし、暇
    ALERT = "注意"         # 名前呼ばれた
    ACTIVE = "活動"        # 行動中
    SEARCHING = "探索"     # 何か探してる
    HOLDING = "保持"       # 何か持ってる


@dataclass
class Qualia:
    """第2層：クオリア（感覚）"""
    visual: Dict = None      # 視覚情報
    auditory: str = ""       # 聴覚情報（言葉）
    touch: float = 0.0       # 触覚（-1〜+1）
    
    def __post_init__(self):
        if self.visual is None:
            self.visual = {}


@dataclass 
class Memory:
    """第4層：記憶"""
    objects: Dict = None     # 物体の記憶 {"赤いボール": {"color": "red", "shape": "sphere"}}
    experiences: List = None # 経験の記録
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = {
                "赤いボール": {"color": "red", "shape": "sphere", "size": 0.2},
                "青い箱": {"color": "blue", "shape": "box", "size": 0.3},
            }
        if self.experiences is None:
            self.experiences = []


class HidaCore:
    """
    飛騨アーキテクチャ本体
    L1〜L5 が常時ループ
    """
    
    def __init__(self):
        # ===== 5層構造 =====
        # L1: 身体層（センサー/モーター）
        self.body_state = {
            "position": [0, 0, 0],
            "holding": None,
            "energy": 1.0,
        }
        
        # L2: クオリア層（感覚）
        self.qualia = Qualia()
        
        # L3: 構造化層（予測と誤差）
        self.prediction = {
            "expected_state": None,
            "current_goal": None,
        }
        self.prediction_error = 0.0
        
        # L4: 記憶層
        self.memory = Memory()
        
        # L5: 意識層
        self.consciousness = ConsciousnessState.IDLE
        self.self_strength = 0.1
        self.attention_target = None
        
        # ===== システム =====
        self.name = "飛騨"
        self.running = False
        self.loop_interval = 0.1  # 100ms
        
        # シミュレーション
        self.sim = None
        
        # 行動キュー
        self.pending_action = None
        
        print("飛騨アーキテクチャ 起動")
    
    # ==========================================
    # メインループ（常時回る）
    # ==========================================
    
    def start_loop(self):
        """L1〜L5 ループ開始"""
        self.running = True
        print("ループ開始...")
        
        while self.running:
            self._loop_cycle()
            time.sleep(self.loop_interval)
    
    def stop_loop(self):
        """ループ停止"""
        self.running = False
        print("ループ停止")
    
    def _loop_cycle(self):
        """1サイクル：L1→L2→L3→L4→L5→行動"""
        
        # L1: 身体からの入力
        self._layer1_body_input()
        
        # L2: クオリアに変換
        self._layer2_qualia()
        
        # L3: 構造化・予測誤差
        self._layer3_structure()
        
        # L4: 記憶参照
        self._layer4_memory()
        
        # L5: 意識・統合
        self._layer5_consciousness()
        
        # 行動出力
        self._action_output()
    
    # ==========================================
    # 各層の処理
    # ==========================================
    
    def _layer1_body_input(self):
        """L1: 身体層 - センサー入力"""
        if self.sim:
            # シミュレーションから位置取得
            pos = self.sim.get_robot_position()
            self.body_state["position"] = list(pos)
            
            # 視覚情報取得
            self.qualia.visual = self.sim.get_visual_info()
    
    def _layer2_qualia(self):
        """L2: クオリア層 - 感覚を生成"""
        # 聴覚入力があれば処理
        if self.qualia.auditory:
            # 名前が呼ばれたか？
            if self.name in self.qualia.auditory:
                self.prediction_error += 0.5  # 誤差増大
                self.attention_target = "caller"
            # 聴覚入力は1回で消費（次サイクルでの誤差二重加算を防ぐ）
            self.qualia.auditory = ""
    
    def _layer3_structure(self):
        """L3: 構造化層 - 予測と誤差"""
        
        # 目標がある場合、現状との差を計算
        if self.prediction["current_goal"]:
            goal = self.prediction["current_goal"]
            
            if goal["type"] == "find_object":
                # 物体を探す目標
                target_name = goal["target"]
                found = self._search_in_visual(target_name)
                
                if found:
                    self.prediction_error = 0.1  # 見つかった、誤差小
                    goal["found"] = True
                    goal["position"] = found
                else:
                    self.prediction_error = 0.6  # 見つからない、誤差大
            
            elif goal["type"] == "reach_object":
                # 物体に近づく目標
                if goal.get("position"):
                    distance = self._distance_to(goal["position"])
                    self.prediction_error = min(distance / 3.0, 1.0)
            
            elif goal["type"] == "deliver":
                # 届ける目標
                if self.body_state["holding"]:
                    distance = self._distance_to([0, 0, 0])  # 原点に届ける
                    self.prediction_error = min(distance / 3.0, 1.0)
        else:
            # 目標なし → 暇
            self.prediction_error *= 0.9  # 徐々に減衰
    
    def _layer4_memory(self):
        """L4: 記憶層 - 記憶検索"""
        # attention_target があれば記憶を検索
        pass
    
    def _layer5_consciousness(self):
        """L5: 意識層 - 統合と判断"""
        
        # 予測誤差と自己強度で意識状態を決定
        if self.prediction_error > 0.5:
            if self.consciousness == ConsciousnessState.IDLE:
                self.consciousness = ConsciousnessState.ALERT
                print(f"  [意識ON] 予測誤差: {self.prediction_error:.2f}")
        elif self.prediction_error < 0.1:
            if self.consciousness not in [ConsciousnessState.IDLE]:
                self.consciousness = ConsciousnessState.IDLE
                print(f"  [意識OFF] 待機状態")
        
        # 自己強度の更新
        if self.prediction_error > 0.3:
            self.self_strength = min(1.0, self.self_strength + 0.01)
    
    def _action_output(self):
        """行動出力 - 意識状態に応じて行動"""
        
        if not self.pending_action:
            return
        
        action = self.pending_action
        
        if action["type"] == "search":
            self._do_search(action["target"])
        elif action["type"] == "pick_up":
            self._do_pick_up()
        elif action["type"] == "deliver":
            self._do_deliver()
        elif action["type"] == "wait":
            self.pending_action = None
    
    # ==========================================
    # 補助関数
    # ==========================================
    
    def _search_in_visual(self, target_name: str) -> Optional[List[float]]:
        """視覚情報から対象を探す"""
        if not self.qualia.visual:
            return None
        
        # 記憶から対象の特徴を取得
        target_features = self.memory.objects.get(target_name, {})
        if not target_features:
            return None
        
        # 視覚情報と照合
        for obj_id, obj_info in self.qualia.visual.items():
            if obj_info.get("color") == target_features.get("color"):
                return obj_info.get("position")
        
        return None
    
    def _distance_to(self, target: List[float]) -> float:
        """対象までの距離"""
        pos = self.body_state["position"]
        return math.sqrt(
            (target[0] - pos[0])**2 + 
            (target[1] - pos[1])**2
        )
    
    # ==========================================
    # 行動実行
    # ==========================================
    
    def _do_search(self, target_name: str):
        """探索行動"""
        print(f"  [探索中] {target_name}")
        
        found = self._search_in_visual(target_name)
        
        if found:
            print(f"  [発見] 位置: {found}")
            self.prediction["current_goal"] = {
                "type": "reach_object",
                "target": target_name,
                "position": found,
            }
            self.pending_action = {"type": "pick_up"}
        else:
            # まだ見つからない、探し続ける
            if self.sim:
                self.sim.move_randomly()
    
    def _do_pick_up(self):
        """拾う行動"""
        goal = self.prediction["current_goal"]
        if not goal or not goal.get("position"):
            return
        
        pos = goal["position"]
        distance = self._distance_to(pos)
        
        if distance < 0.5:
            # 近い、拾える
            print(f"  [拾う] {goal['target']}")
            if self.sim:
                self.sim.pick_up()
            self.body_state["holding"] = goal["target"]
            
            # 次の目標：届ける
            self.prediction["current_goal"] = {"type": "deliver"}
            self.pending_action = {"type": "deliver"}
        else:
            # まだ遠い、近づく
            print(f"  [接近中] 距離: {distance:.2f}")
            if self.sim:
                self.sim.move_toward(pos)
    
    def _do_deliver(self):
        """届ける行動"""
        if not self.body_state["holding"]:
            self.pending_action = None
            return
        
        distance = self._distance_to([0, 0, 0])
        
        if distance < 0.5:
            # 到着、置く
            print(f"  [完了] {self.body_state['holding']} を届けました")
            if self.sim:
                self.sim.put_down()
            self.body_state["holding"] = None
            self.prediction["current_goal"] = None
            self.pending_action = {"type": "wait"}
            self.consciousness = ConsciousnessState.IDLE
        else:
            # まだ遠い、運ぶ
            print(f"  [運搬中] 距離: {distance:.2f}")
            if self.sim:
                self.sim.move_toward([0, 0, 0])
    
    # ==========================================
    # 外部入力
    # ==========================================
    
    def hear(self, text: str):
        """聴覚入力（人間からの言葉）"""
        print(f"\n【聞こえた】「{text}」")
        self.qualia.auditory = text
        
        # 名前が含まれてるか
        if self.name in text:
            print(f"  → 呼ばれた！")
            self.consciousness = ConsciousnessState.ALERT
            self.prediction_error = 0.6
            
            # コマンド解析
            self._parse_command(text)
            # 入力は消費（常時ループで同じ音声が何度も誤差加算されるのを防ぐ）
            self.qualia.auditory = ""
    
    def _parse_command(self, text: str):
        """コマンドを解析（L3の構造化）"""
        
        # 「〇〇を持ってきて」パターン
        for obj_name in self.memory.objects.keys():
            if obj_name in text and ("持ってきて" in text or "取って" in text):
                print(f"  → 目標設定: {obj_name} を持ってくる")
                self.prediction["current_goal"] = {
                    "type": "find_object",
                    "target": obj_name,
                }
                self.pending_action = {"type": "search", "target": obj_name}
                self.consciousness = ConsciousnessState.SEARCHING
                return
        
        # 「探して」パターン
        for obj_name in self.memory.objects.keys():
            if obj_name in text and "探して" in text:
                print(f"  → 目標設定: {obj_name} を探す")
                self.prediction["current_goal"] = {
                    "type": "find_object",
                    "target": obj_name,
                }
                self.pending_action = {"type": "search", "target": obj_name}
                self.consciousness = ConsciousnessState.SEARCHING
                return
        
        # 「止まれ」パターン
        if "止まれ" in text or "止まって" in text:
            print(f"  → 停止")
            self.pending_action = None
            self.prediction["current_goal"] = None
            self.consciousness = ConsciousnessState.IDLE


# ==========================================
# シミュレーション（簡易版）
# ==========================================

class HidaSimulation:
    """飛騨用シミュレーション"""
    
    def __init__(self):
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)
        
        # 床
        self.plane_id = p.loadURDF("plane.urdf")
        
        # ロボット
        self.robot_id = self._create_robot()
        
        # ボール（赤）
        self.ball_id = self._create_ball([2, 1, 0.3], [0.9, 0.1, 0.1, 1])
        
        self.is_holding = False
        print("シミュレーション起動")
    
    def _create_robot(self):
        col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1])
        vis = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.3, 0.2, 0.1],
                                  rgbaColor=[0.2, 0.4, 0.8, 1])
        return p.createMultiBody(baseMass=1, baseCollisionShapeIndex=col,
                                 baseVisualShapeIndex=vis, basePosition=[0, 0, 0.2])
    
    def _create_ball(self, pos, color):
        col = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        vis = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=color)
        return p.createMultiBody(baseMass=0.5, baseCollisionShapeIndex=col,
                                 baseVisualShapeIndex=vis, basePosition=pos)
    
    def get_robot_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        return pos
    
    def get_ball_position(self):
        pos, _ = p.getBasePositionAndOrientation(self.ball_id)
        return pos
    
    def get_visual_info(self) -> Dict:
        """視覚情報を返す"""
        ball_pos = self.get_ball_position()
        return {
            "ball": {
                "color": "red",
                "shape": "sphere",
                "position": list(ball_pos),
            }
        }
    
    def move_toward(self, target):
        """対象に向かって移動"""
        pos = list(self.get_robot_position())
        dx = target[0] - pos[0]
        dy = target[1] - pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0.1:
            speed = 0.1
            pos[0] += (dx / dist) * speed
            pos[1] += (dy / dist) * speed
            p.resetBasePositionAndOrientation(self.robot_id, [pos[0], pos[1], 0.2], [0,0,0,1])
            
            if self.is_holding:
                p.resetBasePositionAndOrientation(self.ball_id, [pos[0], pos[1], 0.5], [0,0,0,1])
        
        p.stepSimulation()
    
    def move_randomly(self):
        """ランダムに動く（探索）"""
        import random
        pos = list(self.get_robot_position())
        pos[0] += random.uniform(-0.1, 0.1)
        pos[1] += random.uniform(-0.1, 0.1)
        p.resetBasePositionAndOrientation(self.robot_id, [pos[0], pos[1], 0.2], [0,0,0,1])
        p.stepSimulation()
    
    def pick_up(self):
        """拾う"""
        self.is_holding = True
        pos = self.get_robot_position()
        p.resetBasePositionAndOrientation(self.ball_id, [pos[0], pos[1], 0.5], [0,0,0,1])
    
    def put_down(self):
        """置く"""
        self.is_holding = False
        pos = self.get_robot_position()
        p.resetBasePositionAndOrientation(self.ball_id, [pos[0]+0.5, pos[1], 0.2], [0,0,0,1])
    
    def close(self):
        p.disconnect()


# ==========================================
# 実行
# ==========================================

def main():
    print("=" * 60)
    print("Phase 14: HIDA Core Architecture")
    print("飛騨アーキテクチャ本体")
    print("=" * 60)
    print()
    print("L1〜L5 が常時ループ")
    print("名前を呼ぶと意識 ON")
    print()
    
    # 飛騨起動
    hida = HidaCore()
    
    # シミュレーション接続
    hida.sim = HidaSimulation()
    
    # ループを別スレッドで開始
    loop_thread = threading.Thread(target=hida.start_loop, daemon=True)
    loop_thread.start()
    
    print("\n" + "-" * 60)
    print("コマンド入力（例: 「飛騨、赤いボールを持ってきて」）")
    print("'q' で終了")
    print("-" * 60)
    
    try:
        while True:
            text = input("\nあなた: ").strip()
            if text.lower() == 'q':
                break
            if text:
                hida.hear(text)
                # 行動が終わるまで待つ
                time.sleep(0.5)
                while hida.pending_action and hida.pending_action.get("type") != "wait":
                    time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    
    hida.stop_loop()
    hida.sim.close()
    print("\n終了")


if __name__ == "__main__":
    main()
