"""
動く世界のテスト
壁が勝手に動く → HIDAは邪魔されるか？
"""

from world import World
from hida import Hida
from narrator import narrate
import random

def main():
    # 10x10の世界
    world = World(size=10)
    
    # 外壁
    for i in range(10):
        world.add_wall(i, 0)
        world.add_wall(i, 9)
        world.add_wall(0, i)
        world.add_wall(9, i)
    
    # 内壁（HIDAの経路上に配置）
    world.add_wall(3, 3)
    world.add_wall(3, 4)
    world.add_wall(4, 4)
    world.add_wall(5, 3)
    world.add_wall(5, 4)
    world.add_wall(6, 5)
    world.add_wall(6, 6)
    
    # ボール（右側、少し遠く）
    world.add_object("ball", 7, 4, color="red")
    
    # ゴール（右下）
    world.add_object("goal", 8, 8, color=None)
    
    # HIDA（左上からスタート）
    world.hida_pos = [2, 2]
    world.hida_dir = 'S'
    
    hida = Hida()
    hida.pos = [2, 2]
    hida.direction = 'S'
    
    print("=== 動く世界テスト ===")
    print("壁が20%の確率で動く")
    print("HIDAは邪魔されるか？\n")
    
    world.display()
    
    # メインループ
    for step in range(50):
        print(f"\n--- Step {step + 1} ---")
        
        # 1. HIDAが周りを見る
        hida.look_around_and_remember(world)
        
        # 2. 世界が動く（壁が動くかも）
        moved = world.tick(move_probability=0.2)
        if moved:
            for m in moved:
                print(f"  🧱 壁が動いた！ {m['from']} → {m['to']}")
                print(f"     （HIDAはまだ知らない...）")
        
        # 3. ボール見つけてる？
        ball_pos = None
        for pos, obj in hida.found_objects.items():
            if obj.get('color') == 'red':
                ball_pos = pos
                break
        
        if ball_pos:
            print(f"  記憶: ボールは {ball_pos} にあるはず")
        else:
            print(f"  記憶: ボール未発見")
        
        # 4. 行動（簡単版：ボールに向かう）
        if ball_pos and not hida.holding:
            # ボールの方向へ
            target = ball_pos
            dx = target[0] - hida.pos[0]
            dy = target[1] - hida.pos[1]
            
            # 方向決定
            if abs(dx) > abs(dy):
                target_dir = 'E' if dx > 0 else 'W'
            else:
                target_dir = 'S' if dy > 0 else 'N'
            
            # 向きを変える or 前進
            if hida.direction != target_dir:
                # 最短回転を計算
                dirs = ['N', 'E', 'S', 'W']
                current_idx = dirs.index(hida.direction)
                target_idx = dirs.index(target_dir)
                diff = (target_idx - current_idx) % 4
                
                if diff == 1 or diff == 2:
                    world.turn_right()
                else:  # diff == 3
                    world.turn_left()
                hida.update_pos(world)
                print(f"  行動: 回転 → {hida.direction}")
            else:
                success, msg = world.move_forward()
                if success:
                    hida.update_pos(world)
                    print(f"  行動: 前進 → {hida.pos}")
                    
                    # 周りを見る（移動後）
                    hida.look_around_and_remember(world)
                else:
                    world.turn_right()
                    hida.update_pos(world)
                    print(f"  行動: 壁！回転 → {hida.direction}")
        else:
            # ランダム探索
            action = random.choice(['forward', 'left', 'right'])
            if action == 'forward':
                success, msg = world.move_forward()
                if success:
                    hida.update_pos(world)
                    print(f"  行動: 探索前進 → {hida.pos}")
                else:
                    world.turn_right()
                    hida.update_pos(world)
            elif action == 'left':
                world.turn_left()
                hida.update_pos(world)
            else:
                world.turn_right()
                hida.update_pos(world)
        
        # 5. 状態表示（10ステップごと）
        if (step + 1) % 10 == 0:
            print(f"\n  === 10ステップ経過 ===")
            print(f"  HIDA位置: {hida.pos}, 向き: {hida.direction}")
            print(f"  記憶してるマス: {hida.known_cells()}")
            world.display()
        
        # 6. ボール到達チェック
        front = world.get_front_pos()
        if tuple(front) in world.objects:
            obj = world.objects[tuple(front)]
            if obj.get('color') == 'red':
                print(f"\n  🎉 ボール発見！目の前にある！")
                success, msg = world.grab()
                if success:
                    hida.holding = world.hida_holding
                    print(f"  {msg}")
                    break

    print("\n=== 終了 ===")
    print(f"最終位置: {hida.pos}")
    print(f"持ってる: {hida.holding}")
    print(f"記憶してるマス: {hida.known_cells()}")
    world.display()

if __name__ == "__main__":
    main()
