"""
world.py
5x5グリッド - 神は全部見える、HIDAは前方1マスだけ
"""

class World:
    def __init__(self, size=5):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.hida_pos = [2, 2]
        self.hida_dir = 'N'
    
    def add_wall(self, x, y):
        """壁を配置"""
        self.grid[y][x] = 'wall'
    
    def get_front_pos(self):
        """前方の座標"""
        x, y = self.hida_pos
        if self.hida_dir == 'N': return [x, y-1]
        if self.hida_dir == 'S': return [x, y+1]
        if self.hida_dir == 'E': return [x+1, y]
        if self.hida_dir == 'W': return [x-1, y]
    
    def get_pos_in_dir(self, direction):
        """指定方向の座標"""
        x, y = self.hida_pos
        if direction == 'N': return [x, y-1]
        if direction == 'S': return [x, y+1]
        if direction == 'E': return [x+1, y]
        if direction == 'W': return [x-1, y]
    
    def see_cell(self, pos):
        """指定座標を見る"""
        x, y = pos
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return 'out'
        if self.grid[y][x] == 'wall':
            return 'wall'
        return 'empty'
    
    def see_front(self):
        """前方1マスだけ見る（HIDAの視点）"""
        front = self.get_front_pos()
        return self.see_cell(front)
    
    def look_around(self):
        """首を回して4方向を見渡す"""
        result = {}
        for direction in ['N', 'E', 'S', 'W']:
            pos = self.get_pos_in_dir(direction)
            result[direction] = {
                'pos': pos,
                'cell': self.see_cell(pos)
            }
        return result
    
    def move_forward(self):
        """前進"""
        front = self.get_front_pos()
        fx, fy = front
        
        if fx < 0 or fx >= self.size or fy < 0 or fy >= self.size:
            return False, "マップ外"
        
        if self.grid[fy][fx] == 'wall':
            return False, "壁"
        
        self.hida_pos = front
        return True, "移動した"
    
    def turn_left(self):
        turns = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"{self.hida_dir}向き"
    
    def turn_right(self):
        turns = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.hida_dir = turns[self.hida_dir]
        return True, f"{self.hida_dir}向き"
    
    def display(self, internal_map=None):
        """表示（神視点）"""
        arrows = {'N': '^', 'S': 'v', 'E': '>', 'W': '<'}
        
        print("\n=== 神視点 ===")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if [x, y] == self.hida_pos:
                    row += f"[{arrows[self.hida_dir]}]"
                elif self.grid[y][x] == 'wall':
                    row += "[#]"
                else:
                    row += "[ ]"
            print(row)
        
        if internal_map:
            print("\n=== HIDA内部マップ ===")
            for y in range(self.size):
                row = ""
                for x in range(self.size):
                    key = (x, y)
                    if [x, y] == self.hida_pos:
                        row += f"[{arrows[self.hida_dir]}]"
                    elif key in internal_map:
                        cell = internal_map[key]
                        if cell == 'wall':
                            row += "[#]"
                        elif cell == 'empty':
                            row += "[.]"
                        else:
                            row += "[?]"
                    else:
                        row += "[?]"  # 未知
                print(row)
