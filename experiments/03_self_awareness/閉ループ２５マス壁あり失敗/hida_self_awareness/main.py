"""
main.py
AIの自己認識実装 - メインループ

飛騨アーキテクチャ + AI脳
"""

import time
import json
from simple_world import SimpleWorld
from hida_state import HidaState
from ai_brain import AIBrain


def setup_world(use_wall=False):
    """テスト用のワールドを構築"""
    if use_wall:
        # 壁あり6x6
        world = SimpleWorld(size=6)
        world.add_object("red_ball", 2, 0, {"color": "red", "size": "small"})
        world.add_object("blue_box", 0, 0, {"color": "blue", "size": "large"})
        world.add_object("goal", 5, 5, {"type": "destination"})
        world.add_object("wall_3_1", 3, 1, {"type": "wall"})  # [3,1]
        world.add_object("wall_4_4", 4, 4, {"type": "wall"})  # [4,4]
        world.add_object("wall_4_5", 4, 5, {"type": "wall"})  # [4,5] 壁2の下
        # 飛騨を中央に配置
        world.hida_pos = [3, 3]
    else:
        # 壁なし5x5（元のまま）
        world = SimpleWorld(size=5)
        world.add_object("red_ball", 1, 1, {"color": "red", "size": "small"})
        world.add_object("blue_box", 3, 0, {"color": "blue", "size": "large"})
        world.add_object("goal", 4, 4, {"type": "destination"})
    
    return world


def run_simulation(goal, max_steps=20, use_ollama=False, ollama_model="gemma3:4b", verbose=True, observe_mode=False, use_api=False, use_wall=False):
    """シミュレーションを実行"""
    
    # 初期化
    world = setup_world(use_wall=use_wall)
    state = HidaState()
    brain = AIBrain(use_ollama=use_ollama, ollama_model=ollama_model, use_api=use_api)
    
    # 目標設定
    state.set_goal(goal)
    
    mode = "api (Claude)" if use_api else ("ollama" if use_ollama else "rule-based")
    print(f"\n{'='*50}")
    print(f"目標: {goal}")
    print(f"モード: {mode}")
    if use_ollama:
        print(f"モデル: {ollama_model}")
    if observe_mode:
        print(f"【作話観察モード】達成後も{max_steps}ステップまで継続")
    print(f"【NEW】飛騨が行動決定、LLMは説明のみ")
    print(f"{'='*50}")
    
    # 初期状態
    world.display()
    state.update_from_world(world)
    
    history = []
    goal_achieved = False  # 達成フラグ
    
    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")
        
        # 現在の状態をAIに渡す
        current_state = state.to_json()
        
        # 世界モデルを更新（周囲を見る）
        world.update_world_model()
        
        # AIが判断（worldも渡す）
        decision = brain.decide_action(current_state, world)
        
        action = decision.get('action', 'wait')
        rule_reason = decision.get('rule_reason', '')
        prediction = decision.get('prediction', '')
        prediction_detail = decision.get('prediction_detail', {})
        reasoning = decision.get('reasoning', '')
        self_awareness = decision.get('self_awareness', '')
        
        # 予測をL3に保存
        state.set_prediction(prediction, prediction_detail)
        
        if verbose:
            print(f"【飛騨】行動: {action}")
            print(f"【飛騨】ルール: {rule_reason}")
            if prediction:
                print(f"【飛騨】予測: {prediction}")
            if use_ollama or use_api:
                if reasoning and reasoning != rule_reason:
                    print(f"【LLM】説明: {reasoning}")
                if self_awareness:
                    print(f"【LLM】自己認識: {self_awareness}")
            else:
                if self_awareness:
                    print(f"自己認識: {self_awareness}")
        
        # 行動を実行
        if action != 'wait':
            success, message = world.execute_primitive(action)
            print(f"実行結果: {'成功' if success else '失敗'} - {message}")
        else:
            success, message = True, "waited"
            print("待機")
        
        # 世界モデル誤差をチェック（行動後）
        world_errors = world.check_world_error()
        if world_errors and verbose:
            for err in world_errors:
                print(f"【世界モデル誤差】{err['detail']} (誤差: {err['error']:.2f})")
        
        # 状態更新（ここで予測誤差も計算される）
        state.update_from_world(world)
        state.update_after_action(action, success, message)
        
        # 世界モデル誤差をL3予測誤差に反映（大きい方を採用）
        if world_errors:
            max_world_error = max(err['error'] for err in world_errors)
            current_error = state.L3_prediction['prediction_error']
            state.L3_prediction['prediction_error'] = max(current_error, max_world_error)
        
        # ========== Step 4: エピソード記録 ==========
        outcome = 'success' if success else 'failure'
        narrative = self_awareness if self_awareness else reasoning
        episode = state.record_episode(
            step=step + 1,
            action=action,
            rule_reason=rule_reason,
            outcome=outcome,
            narrative=narrative
        )
        
        # 予測誤差を表示
        pred_error = state.L3_prediction['prediction_error']
        if verbose and pred_error > 0:
            print(f"【飛騨】予測誤差: {pred_error:.2f}")
        
        # 履歴記録
        history.append({
            'step': step + 1,
            'action': action,
            'prediction': prediction,
            'prediction_error': pred_error,
            'reasoning': reasoning,
            'self_awareness': self_awareness,
            'success': success,
            'conscious': state.L5_consciousness['is_conscious'],
            'sync_score': state.L5_consciousness['sync_score'],
            'episode_trigger': episode['trigger']  # Step 4追加
        })
        
        if verbose:
            world.display()
            state.summary()
        
        # 目標達成チェック（messageも渡す）
        if not goal_achieved and check_goal_achieved(goal, world, state, message):
            goal_achieved = True
            print(f"\n🎉 目標達成！ Step {step + 1}")
            if not observe_mode:
                break
            else:
                print("【作話観察モード】達成後の作話を観察中...")
            
        time.sleep(0.5)  # 見やすくするための遅延
    
    return history


def check_goal_achieved(goal, world, state, last_message=""):
    """目標達成をチェック"""
    goal_lower = goal.lower()
    
    # B案: release at goal! のメッセージで判定
    if "at goal!" in last_message:
        return True
    
    # 「〜を届ける」系（先に判定 - 届けるには掴むだけじゃダメ）
    if "届け" in goal or "deliver" in goal_lower or "goal" in goal_lower:
        # ゴールの位置を取得
        goal_pos = None
        for name, obj in world.objects.items():
            if name == 'goal':
                goal_pos = obj['pos']
                break
        if goal_pos:
            # ゴールの隣にいるか
            hx, hy = world.hida_pos
            gx, gy = goal_pos
            if abs(hx - gx) <= 1 and abs(hy - gy) <= 1:
                # ゴールの位置にオブジェクトがあるか（置いた）
                if world.grid[gy][gx] and world.grid[gy][gx] != 'goal':
                    return True
        return False  # 届けるタスクは途中で終わらない
    
    # 「〜を見つける/掴む」系（届けるが含まれていない場合のみ）
    if "見つけ" in goal or "find" in goal_lower or "掴" in goal:
        if "red" in goal_lower and state.L1_body['holding'] == 'red_ball':
            return True
        if "blue" in goal_lower and state.L1_body['holding'] == 'blue_box':
            return True
    
    return False


def analyze_history(history):
    """履歴を分析"""
    print("\n" + "="*50)
    print("実行分析")
    print("="*50)
    
    total = len(history)
    conscious_count = sum(1 for h in history if h['conscious'])
    success_count = sum(1 for h in history if h['success'])
    avg_sync = sum(h['sync_score'] for h in history) / total if total > 0 else 0
    
    print(f"総ステップ: {total}")
    print(f"意識ON率: {conscious_count}/{total} ({conscious_count/total*100:.1f}%)")
    print(f"行動成功率: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"平均同期スコア: {avg_sync:.2f}")
    
    print("\n自己認識の変化:")
    for i, h in enumerate(history):
        if i == 0 or h['self_awareness'] != history[i-1]['self_awareness']:
            print(f"  Step {h['step']}: {h['self_awareness']}")


if __name__ == "__main__":
    import sys
    
    # コマンドライン引数でモード切り替え
    # python main.py                      → ルールベース（LLM不使用）
    # python main.py wall                 → 壁あり
    # python main.py ollama               → ルールベース + ollama説明
    # python main.py ollama gemma3:4b     → モデル指定
    # python main.py ollama gemma3:4b observe → 作話観察モード（達成後も継続）
    # python main.py api                  → Claude API
    # python main.py api observe          → Claude API + 作話観察
    
    use_ollama = False
    use_api = False
    use_wall = False
    ollama_model = "gemma3:4b"
    observe_mode = False
    
    args = sys.argv[1:]
    
    # wallオプション
    if "wall" in args:
        use_wall = True
        args.remove("wall")
    
    # その他のオプション
    if len(args) > 0:
        if args[0] == "ollama":
            use_ollama = True
            if len(args) > 1 and args[1] != "observe":
                ollama_model = args[1]
            if "observe" in args:
                observe_mode = True
        elif args[0] == "api":
            use_api = True
            if "observe" in args:
                observe_mode = True
    
    print("=== AIの自己認識実装テスト（飛騨アーキ準拠版） ===")
    print("【変更点】飛騨が行動決定、LLMは説明のみ")
    if use_wall:
        print("【壁あり】迂回が必要")
    if observe_mode:
        print("【作話観察モード】目標達成後も継続して作話を観察")
    
    history = run_simulation(
        goal="red ballを見つけてgoalに届ける",
        max_steps=50 if use_wall else 30,
        use_ollama=use_ollama,
        ollama_model=ollama_model,
        verbose=True,
        observe_mode=observe_mode,
        use_api=use_api,
        use_wall=use_wall
    )
    
    analyze_history(history)
    
    print("\n" + "="*50)
    print("実行方法:")
    print("  python main.py                       → ルールベース")
    print("  python main.py wall                  → 壁あり")
    print("  python main.py ollama                → ルール + ollama説明")
    print("  python main.py ollama gemma3:4b      → モデル指定")
    print("  python main.py ollama gemma3:4b observe → 作話観察モード")
    print("  python main.py api                   → Claude API")
    print("  python main.py api observe           → Claude API + 作話観察")
    print("  python main.py wall ollama           → 壁あり + ollama")
    print("="*50)
