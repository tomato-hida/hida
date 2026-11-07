"""
hida.py
HIDA - 内部世界モデルを持つエージェント
"""

import random

class Hida:
    def __init__(self, start_pos=None):
        # 内部マップ（最初は空）
        self.internal_map = {}
        
        # 自分の位置と向き（これは知ってる）
        self.pos = start_pos if start_pos else [2, 2]
        self.direction = 'N'
        
        # 行動の記憶
        self.action_memory = []
    
    def see_and_remember(self, world):
        """見て覚える（前方だけ）"""
        # 今いる場所を記録
        self.internal_map[tuple(self.pos)] = 'empty'
        
        # 前方を見る
        front_cell = world.see_front()
        front_pos = world.get_front_pos()
        
        # 記憶する
        if front_pos[0] >= 0 and front_pos[0] < world.size and \
           front_pos[1] >= 0 and front_pos[1] < world.size:
            self.internal_map[tuple(front_pos)] = front_cell
        
        return front_cell
    
    def look_around_and_remember(self, world):
        """首を回して4方向見て覚える"""
        # 今いる場所を記録
        self.internal_map[tuple(self.pos)] = 'empty'
        
        # 4方向を見る
        around = world.look_around()
        
        seen = {}
        for direction, info in around.items():
            pos = info['pos']
            cell = info['cell']
            
            # マップ外も記憶（境界として）
            self.internal_map[tuple(pos)] = cell
            
            seen[direction] = cell
        
        return seen
    
    def choose_action(self, front_cell):
        """行動を選ぶ（未知優先 + 確率）"""
        
        # 4方向チェック：未知で、かつ通れる方向
        dirs = ['N', 'E', 'S', 'W']
        deltas = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        
        # 進める未知の方向を探す
        good_unknown_dirs = []
        for d in dirs:
            dx, dy = deltas[d]
            next_pos = (self.pos[0] + dx, self.pos[1] + dy)
            
            # 次のマスが未知、または空
            if next_pos not in self.internal_map:
                good_unknown_dirs.append(d)
            elif self.internal_map.get(next_pos) == 'empty':
                # 空だけど、その先が未知かチェック
                dx2, dy2 = deltas[d]
                far_pos = (next_pos[0] + dx2, next_pos[1] + dy2)
                if far_pos not in self.internal_map:
                    good_unknown_dirs.append(d)
        
        # 今の向きで前が空いてるなら前進優先
        if front_cell == 'empty':
            if self.direction in good_unknown_dirs:
                return 'forward'
            # それ以外でも確率で前進
            if random.random() < 0.5:
                return 'forward'
        
        # 未知の方向があれば、そっちに向く
        if good_unknown_dirs:
            target_dir = random.choice(good_unknown_dirs)
            if self.direction == target_dir:
                if front_cell == 'empty':
                    return 'forward'
            return self._get_turn_to(target_dir)
        
        # 未知がなければランダム
        if front_cell == 'empty':
            return random.choice(['forward', 'left', 'right'])
        else:
            return random.choice(['left', 'right'])
    
    def _get_turn_to(self, target_dir):
        """目標方向に向くための回転"""
        dirs = ['N', 'E', 'S', 'W']
        current_idx = dirs.index(self.direction)
        target_idx = dirs.index(target_dir)
        diff = (target_idx - current_idx) % 4
        
        if diff == 1:
            return 'right'
        elif diff == 3:
            return 'left'
        elif diff == 2:
            return random.choice(['left', 'right'])
        else:
            return 'forward'
    
    def record_action(self, action, found_new):
        """行動結果を記憶"""
        self.action_memory.append({
            'pos': tuple(self.pos),
            'dir': self.direction,
            'action': action,
            'found_new': found_new
        })
    
    def update_pos(self, world):
        """位置を同期"""
        self.pos = world.hida_pos.copy()
        self.direction = world.hida_dir
    
    def known_cells(self):
        """知ってるマスの数"""
        return len(self.internal_map)
    
    def has_unknown_reachable(self):
        """行ける未知の場所があるか（マップ外は除外）"""
        dirs = ['N', 'E', 'S', 'W']
        deltas = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        
        # 既知の空きマスから、隣接する未知があるか
        for known_pos, cell in self.internal_map.items():
            if cell != 'empty':
                continue
            
            for d in dirs:
                dx, dy = deltas[d]
                neighbor = (known_pos[0] + dx, known_pos[1] + dy)
                
                # マップ外と判明してる場所は除外
                if neighbor in self.internal_map and self.internal_map[neighbor] == 'out':
                    continue
                
                # 隣が未知なら、まだ行ける場所がある
                if neighbor not in self.internal_map:
                    return True
        
        return False
    
    def find_path(self, goal):
        """内部マップだけで経路を探す（BFS）"""
        from collections import deque
        
        start = tuple(self.pos)
        goal = tuple(goal)
        
        if start == goal:
            return [start]
        
        # BFS
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            # 4方向
            for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                next_pos = (pos[0] + dx, pos[1] + dy)
                
                if next_pos in visited:
                    continue
                
                # 内部マップで確認
                if next_pos not in self.internal_map:
                    continue  # 知らない場所は行けない
                
                if self.internal_map[next_pos] == 'wall':
                    continue  # 壁は通れない
                
                if next_pos == goal:
                    return path + [next_pos]
                
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
        
        return None  # 経路なし
    
    def show_map(self, size=None):
        """内部マップを表示（サイズは自動検出）"""
        if not self.internal_map:
            print("\n内部マップ: 空")
            return
        
        # マップの範囲を自動検出
        xs = [p[0] for p in self.internal_map.keys()]
        ys = [p[1] for p in self.internal_map.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # 壁とout以外をカウント
        real_cells = sum(1 for c in self.internal_map.values() if c not in ['out'])
        
        arrows = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        
        print(f"\n内部マップ（{real_cells}マス）:")
        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                key = (x, y)
                if [x, y] == self.pos:
                    row += f"[{arrows[self.direction]}]"
                elif key in self.internal_map:
                    cell = self.internal_map[key]
                    if cell == 'wall':
                        row += "[#]"
                    elif cell == 'out':
                        row += "[X]"
                    else:
                        row += "[.]"
                else:
                    row += "[?]"
            print(row)
