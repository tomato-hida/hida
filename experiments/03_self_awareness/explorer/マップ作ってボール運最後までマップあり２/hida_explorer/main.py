"""
main.py
Step 1: マップを覚える
Step 2: 指定マスに移動する
"""

import time
import random
from world import World
from hida import Hida
from narrator import narrate


def explore(world, hida, max_steps=50):
    """探索してマップを覚える"""
    print("=== 探索開始 ===")
    print(f"  💭 「{narrate('start')}」")
    
    no_new_count = 0  # 新しい発見がない連続回数
    
    for step in range(max_steps):
        # 首を回して4方向見る
        before_known = hida.known_cells()
        seen = hida.look_around_and_remember(world)
        after_known = hida.known_cells()
        found_new = after_known > before_known
        
        # 予測誤差も「新しい発見」としてカウント
        prediction_errors = getattr(hida, 'last_prediction_errors', 0)
        if prediction_errors > 0:
            found_new = True
        
        # 何か見つけた？
        for direction, info in seen.items():
            if info == 'object':
                # found_objectsをチェック
                pass
        
        # 新しいオブジェクト発見の作話
        for pos, obj in list(hida.found_objects.items()):
            if not hasattr(hida, '_narrated_objects'):
                hida._narrated_objects = set()
            if pos not in hida._narrated_objects:
                hida._narrated_objects.add(pos)
                if obj.get('color') == 'red':
                    print(f"  💭 「{narrate('found_ball')}」")
                elif obj.get('name') == 'goal':
                    print(f"  💭 「{narrate('found_goal')}」")
        
        # 前方の状態
        front = seen[hida.direction]
        
        # 行動を選ぶ（確率 + 記憶）
        action = hida.choose_action(front)
        
        print(f"\nStep {step+1}: pos={hida.pos}, dir={hida.direction}")
        print(f"  見えた: N={seen['N']}, E={seen['E']}, S={seen['S']}, W={seen['W']}")
        print(f"  選択: {action}")
        
        # 行動実行
        front_passable = (front == 'empty')
        
        if action == 'forward' and front_passable:
            success, msg = world.move_forward()
            hida.update_pos(world)
            print(f"  → 前進 {msg}")
            print(f"  💭 「{narrate('forward')}」")
        elif action == 'left':
            world.turn_left()
            hida.update_pos(world)
            print(f"  → 左回転")
            print(f"  💭 「{narrate('turn_left')}」")
        elif action == 'right':
            world.turn_right()
            hida.update_pos(world)
            print(f"  → 右回転")
            print(f"  💭 「{narrate('turn_right')}」")
        elif action == 'forward' and not front_passable:
            # 前が塞がってるのに前進選んだ → 左右どちらか
            print(f"  💭 「{narrate('blocked')}」")
            action = random.choice(['left', 'right'])
            if action == 'left':
                world.turn_left()
            else:
                world.turn_right()
            hida.update_pos(world)
            print(f"  → 前が塞がってる、{action}")
        
        # 結果を記憶
        after_known2 = hida.known_cells()
        found_new_after = after_known2 > before_known
        hida.record_action(action, found_new_after)
        
        hida.show_map()
        
        # 新しい発見があったかチェック
        if found_new_after:
            no_new_count = 0
        else:
            no_new_count += 1
        
        # 行ける未知の場所がなくなったら終了
        if not hida.has_unknown_reachable():
            print(f"\n🎉 行ける未知の場所がなくなった！ {step+1}ステップ、{hida.known_cells()}マス発見")
            print(f"  💭 「{narrate('explore_done')}」")
            return True
        
        # 長時間新しい発見がなければ終了
        if no_new_count >= 20:
            print(f"\n⏰ 新しい発見がない。{step+1}ステップ、{hida.known_cells()}マス発見")
            print(f"  💭 「{narrate('explore_done')}」")
            return False
        
        time.sleep(0.1)
    
    print(f"\n⏰ {max_steps}ステップで終了。{hida.known_cells()}マス発見")
    return False


def move_to(world, hida, goal):
    """指定マスに移動"""
    print(f"\n=== [{goal[0]},{goal[1]}]に移動 ===")
    
    path = hida.find_path(goal)
    
    if not path:
        print("❌ 経路が見つからない（未知の場所？）")
        return False
    
    print(f"経路: {path}")
    
    for i, next_pos in enumerate(path[1:], 1):  # 最初は現在地
        # 目標方向を決定
        dx = next_pos[0] - hida.pos[0]
        dy = next_pos[1] - hida.pos[1]
        
        if dx == 1: target_dir = 'E'
        elif dx == -1: target_dir = 'W'
        elif dy == 1: target_dir = 'S'
        elif dy == -1: target_dir = 'N'
        
        # 向きを合わせる
        while hida.direction != target_dir:
            world.turn_right()
            hida.update_pos(world)
        
        # 前進
        success, msg = world.move_forward()
        hida.update_pos(world)
        
        # 移動後に周りを見る（予測誤差検出）
        hida.look_around_and_remember(world)
        
        print(f"Step {i}: → {next_pos} ({msg})")
        print(f"  💭 「{narrate('forward')}」")
        hida.show_map()
        
        if not success:
            print("❌ 移動失敗")
            return False
    
    print(f"🎉 到着！ pos={hida.pos}")
    return True


def main():
    # 10x10ワールド（外周は壁）
    world = World(size=10)
    
    # 外周を壁で囲む
    for i in range(10):
        world.add_wall(i, 0)  # 上
        world.add_wall(i, 9)  # 下
        world.add_wall(0, i)  # 左
        world.add_wall(9, i)  # 右
    
    # 内側に壁を配置（複雑に）
    world.add_wall(2, 2)
    world.add_wall(3, 2)
    world.add_wall(4, 2)
    world.add_wall(6, 3)
    world.add_wall(6, 4)
    world.add_wall(6, 5)
    world.add_wall(2, 5)
    world.add_wall(3, 5)
    world.add_wall(4, 7)
    world.add_wall(5, 7)
    
    # 赤いボールを配置（壁に囲まれてない場所）
    world.add_object("ball", 5, 3, color="red")
    
    # ゴールを配置（右下の方、でも端じゃない）
    world.add_object("goal", 7, 6, color=None)
    
    # HIDA（中央からスタート）
    world.hida_pos = [5, 5]
    hida = Hida()
    hida.pos = [5, 5]
    hida.update_pos(world)
    
    print("=== 初期状態（神視点）===")
    world.display()
    
    # ミッション
    print("\n" + "="*30)
    print("目標: 赤いボールをゴールに運ぶ")
    print("="*30)
    
    # Step 1: 探索してボールとゴールを見つける
    explore(world, hida, max_steps=200)
    
    # Step 2: 赤いボールを見つけたか？
    red_ball_pos = None
    goal_pos = None
    for pos, obj in hida.found_objects.items():
        if obj.get('color') == 'red':
            red_ball_pos = pos
        if obj.get('name') == 'goal':
            goal_pos = pos
    
    print(f"\n記憶: ボール={red_ball_pos}, ゴール={goal_pos}")
    
    if not red_ball_pos:
        print("❌ 赤いボールが見つからなかった")
        return
    
    if not goal_pos:
        print("❌ ゴールが見つからなかった")
        return
    
    # Step 3: ボールの隣に移動
    print(f"\n--- ボールをつかみに行く ---")
    target = find_adjacent_empty(hida, red_ball_pos)
    if target:
        # ボール取りに行く途中で...
        path = hida.find_path(target)
        if path and len(path) > 3:
            # 半分まで移動
            halfway = len(path) // 2
            for i, next_pos in enumerate(path[1:halfway+1], 1):
                dx = next_pos[0] - hida.pos[0]
                dy = next_pos[1] - hida.pos[1]
                
                if dx == 1: target_dir = 'E'
                elif dx == -1: target_dir = 'W'
                elif dy == 1: target_dir = 'S'
                elif dy == -1: target_dir = 'N'
                
                while hida.direction != target_dir:
                    world.turn_right()
                    hida.update_pos(world)
                
                success, msg = world.move_forward()
                hida.update_pos(world)
                print(f"Step {i}: → {next_pos} ({msg})")
            
            # 🔥 神がボールを動かす！
            print("\n" + "="*30)
            print("👁️ 神の介入：ボールを動かす！")
            print("="*30)
            old_pos = red_ball_pos
            new_ball_pos = (4, 6)  # 新しい位置（中央寄り、見つけやすい）
            
            # ワールドからボールを移動
            ball_obj = world.objects[old_pos]
            del world.objects[old_pos]
            world.objects[new_ball_pos] = ball_obj
            
            world.display()
            print("（HIDAはまだ知らない...）\n")
        
        # 残りの経路を移動
        move_to(world, hida, target)
        face_target(world, hida, red_ball_pos)
        
        # つかもうとする
        success, msg = world.grab()
        if success:
            hida.holding = world.hida_holding
            del hida.found_objects[red_ball_pos]
            hida.internal_map[red_ball_pos] = 'empty'
            print(f"🎉 {msg}！")
            print(f"  💭 「{narrate('grab')}」")
        else:
            # 予測誤差発生！！
            print(f"\n❌ {msg}")
            print("="*30)
            print("🚨 予測誤差発生！")
            print(f"  期待: ボールがあるはず @ {red_ball_pos}")
            print(f"  現実: ボールがない！")
            print("="*30)
            print(f"  💭 「{narrate('lost')}」")
            
            # 内部マップを修正
            hida.internal_map[red_ball_pos] = 'empty'
            if red_ball_pos in hida.found_objects:
                del hida.found_objects[red_ball_pos]
            
            # 再探索？（ボールを探すモード - ランダムに動き回る）
            print("\n--- 再探索開始（ボールを探すモード）---")
            print(f"  💭 「もう一度探さないと...」")
            
            # ボールを探しながら探索（見つかるまで続ける）
            found_ball_during_search = False
            for search_step in range(100):  # 最大100ステップ
                # 周りを見る（4方向）
                seen = hida.look_around_and_remember(world)
                
                # ボール見つかった？
                for pos, obj in hida.found_objects.items():
                    if obj.get('color') == 'red':
                        found_ball_during_search = True
                        break
                
                if found_ball_during_search:
                    print(f"  🎯 ボール発見！（{search_step+1}ステップ目）")
                    break
                
                # ランダムに動く（未知優先じゃなく）
                front = seen[hida.direction]
                front_passable = (front == 'empty')
                
                if front_passable and random.random() < 0.6:
                    world.move_forward()
                else:
                    if random.random() < 0.5:
                        world.turn_left()
                    else:
                        world.turn_right()
                hida.update_pos(world)
            
            if not found_ball_during_search:
                print(f"  まだ見つからない...（100ステップ探した）")
            
            # 新しいボール位置
            new_red_ball_pos = None
            for pos, obj in hida.found_objects.items():
                if obj.get('color') == 'red':
                    new_red_ball_pos = pos
                    break
            
            if new_red_ball_pos:
                print(f"\n🎯 ボール再発見！ @ {new_red_ball_pos}")
                target = find_adjacent_empty(hida, new_red_ball_pos)
                if target:
                    move_to(world, hida, target)
                    face_target(world, hida, new_red_ball_pos)
                    success, msg = world.grab()
                    if success:
                        hida.holding = world.hida_holding
                        del hida.found_objects[new_red_ball_pos]
                        hida.internal_map[new_red_ball_pos] = 'empty'
                        print(f"🎉 {msg}！")
                        print(f"  💭 「{narrate('grab')}」")
                        red_ball_pos = new_red_ball_pos  # 更新
            else:
                print("❌ ボールが見つからない...")
                return
    
    # Step 4: ゴールの隣に移動
    print(f"\n--- ゴールに運ぶ ---")
    print(f"  💭 「{narrate('move_to_goal')}」")
    target = find_adjacent_empty(hida, goal_pos)
    if target:
        move_to(world, hida, target)
        face_target(world, hida, goal_pos)
        
        success, msg = world.release()
        if success:
            hida.holding = None
            print(f"🎉 {msg}！")
            print(f"  💭 「{narrate('release')}」")
        else:
            print(f"❌ {msg}")
    
    print("\n=== 最終状態 ===")
    world.display()
    
    # 成功判定
    ball_at_goal = (goal_pos in world.objects and 
                   world.objects[goal_pos].get('name') == 'ball')
    if ball_at_goal:
        print("\n🎊 ミッション成功！ボールをゴールに届けた！")
    else:
        # ゴールの隣にボールがあるか確認
        for pos, obj in world.objects.items():
            if obj.get('name') == 'ball':
                print(f"\nボールの位置: {pos}")


def find_adjacent_empty(hida, target_pos):
    """ターゲットの隣接マスで空いてる場所を探す"""
    deltas = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    for dx, dy in deltas:
        adj = (target_pos[0] + dx, target_pos[1] + dy)
        if adj in hida.internal_map and hida.internal_map[adj] == 'empty':
            return list(adj)
    return None


def face_target(world, hida, target_pos):
    """ターゲットの方を向く"""
    dx = target_pos[0] - hida.pos[0]
    dy = target_pos[1] - hida.pos[1]
    
    if dx == 1: target_dir = 'E'
    elif dx == -1: target_dir = 'W'
    elif dy == 1: target_dir = 'S'
    elif dy == -1: target_dir = 'N'
    else:
        return
    
    while hida.direction != target_dir:
        world.turn_right()
        hida.update_pos(world)
    
    print(f"向き変更: {hida.direction}")


if __name__ == "__main__":
    main()
