"""
main.py
Step 1: マップを覚える
Step 2: 指定マスに移動する
"""

import time
import random
from world import World
from hida import Hida


def explore(world, hida, max_steps=50):
    """探索してマップを覚える"""
    print("=== 探索開始 ===")
    
    no_new_count = 0  # 新しい発見がない連続回数
    
    for step in range(max_steps):
        # 首を回して4方向見る
        before_known = hida.known_cells()
        seen = hida.look_around_and_remember(world)
        after_known = hida.known_cells()
        found_new = after_known > before_known
        
        # 前方の状態
        front = seen[hida.direction]
        
        # 行動を選ぶ（確率 + 記憶）
        action = hida.choose_action(front)
        
        print(f"\nStep {step+1}: pos={hida.pos}, dir={hida.direction}")
        print(f"  見えた: N={seen['N']}, E={seen['E']}, S={seen['S']}, W={seen['W']}")
        print(f"  選択: {action}")
        
        # 行動実行
        if action == 'forward' and front == 'empty':
            success, msg = world.move_forward()
            hida.update_pos(world)
            print(f"  → 前進 {msg}")
        elif action == 'left':
            world.turn_left()
            hida.update_pos(world)
            print(f"  → 左回転")
        elif action == 'right':
            world.turn_right()
            hida.update_pos(world)
            print(f"  → 右回転")
        elif action == 'forward' and front != 'empty':
            # 前が塞がってるのに前進選んだ → 左右どちらか
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
            return True
        
        # 長時間新しい発見がなければ終了
        if no_new_count >= 10:
            print(f"\n⏰ 新しい発見がない。{step+1}ステップ、{hida.known_cells()}マス発見")
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
        
        print(f"Step {i}: → {next_pos} ({msg})")
        
        if not success:
            print("❌ 移動失敗")
            return False
    
    print(f"🎉 到着！ pos={hida.pos}")
    return True


def main():
    # 7x7ワールド（外周は壁）
    world = World(size=7)
    
    # 外周を壁で囲む
    for i in range(7):
        world.add_wall(i, 0)  # 上
        world.add_wall(i, 6)  # 下
        world.add_wall(0, i)  # 左
        world.add_wall(6, i)  # 右
    
    # 内側に壁を配置
    world.add_wall(3, 2)
    world.add_wall(4, 4)
    
    # HIDA（中央からスタート）
    world.hida_pos = [3, 3]
    hida = Hida()
    hida.pos = [3, 3]
    hida.update_pos(world)
    
    print("=== 初期状態（神視点）===")
    world.display()
    
    # Step 1: 探索
    explore(world, hida, max_steps=100)
    
    # Step 2: 移動
    print("\n" + "="*30)
    move_to(world, hida, [5, 5])
    
    print("\n=== 最終状態 ===")
    world.display(hida.internal_map)


if __name__ == "__main__":
    main()
