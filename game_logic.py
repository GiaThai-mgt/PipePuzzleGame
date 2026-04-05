import random

class PipeGameLogic:
    # --- Định nghĩa loại ống ---
    PIPE_EMPTY = 0
    PIPE_STRAIGHT = 1
    PIPE_L_SHAPE = 2
    PIPE_T_SHAPE = 3
    PIPE_CROSS = 4
    PIPE_ONE_WAY = 5
    PIPE_LOCKED = 6  # Ống bị khóa, không thể xoay
    
    # --- Định nghĩa hướng ---
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    
    # --- Ánh xạ kết nối ---
    PIPE_CONNECTIONS = {
        PIPE_STRAIGHT: {0: (TOP, BOTTOM), 1: (LEFT, RIGHT), 2: (TOP, BOTTOM), 3: (LEFT, RIGHT)},
        PIPE_L_SHAPE: {0: (TOP, RIGHT), 1: (RIGHT, BOTTOM), 2: (BOTTOM, LEFT), 3: (LEFT, TOP)},
        PIPE_T_SHAPE: {0: (LEFT, TOP, RIGHT), 1: (TOP, RIGHT, BOTTOM), 2: (RIGHT, BOTTOM, LEFT), 3: (BOTTOM, LEFT, TOP)},
        PIPE_CROSS: {0: (TOP, RIGHT, BOTTOM, LEFT), 1: (TOP, RIGHT, BOTTOM, LEFT), 2: (TOP, RIGHT, BOTTOM, LEFT), 3: (TOP, RIGHT, BOTTOM, LEFT)},
        PIPE_ONE_WAY: {0: (TOP, BOTTOM), 1: (LEFT, RIGHT), 2: (BOTTOM, TOP), 3: (RIGHT, LEFT)},
        PIPE_LOCKED: {0: (TOP, BOTTOM), 1: (LEFT, RIGHT), 2: (TOP, BOTTOM), 3: (LEFT, RIGHT)} # Giả định PIPE_LOCKED là STRAIGHT bị khóa
    }
    
    def __init__(self):
        self.current_level = 1
        self.max_level = 9
        self.rotation_count = 0
        self.time_limit = 0
        self.max_rotations = 999
        self.locked_cells = set() # (r, c)
        self.load_level(self.current_level)
    
    def load_level(self, level):
        self.current_level = level
        self.rotation_count = 0
        self.locked_cells = set()

        if level <= 3:
            self.size = 5
            if level == 1:
                self.time_limit = 120
                self.max_rotations = 999
                self.grid_type = [[1, 2, 0, 2, 1], [0, 1, 0, 1, 0], [0, 2, 1, 2, 0], [0, 0, 0, 1, 0], [0, 0, 0, 2, 1]]
                self.start_pos = (0, 0)
                self.end_pos = (4, 4)
            elif level == 2:
                self.time_limit = 110
                self.max_rotations = 20
                self.grid_type = [[2, 1, 2, 0, 0], [1, 0, 1, 2, 1], [2, 1, 2, 1, 2], [0, 2, 1, 0, 1], [0, 1, 2, 1, 2]]
                self.start_pos = (0, 0)
                self.end_pos = (4, 4)
            elif level == 3:
                self.time_limit = 120  # Yêu cầu dài hơn
                self.max_rotations = 15
                self.grid_type = [[2, 2, 2, 2, 2], [2, 1, 1, 1, 2], [2, 1, 0, 1, 2], [2, 1, 1, 1, 2], [2, 2, 2, 2, 2]]
                self.start_pos = (0, 0)
                self.end_pos = (4, 4)
            self.source_direction = self.LEFT

        elif level <= 6:
            self.size = 6
            if level == 4:
                self.time_limit = 130
                self.max_rotations = 18
                self.grid_type = [[2, 1, 3, 0, 2, 2], [6, 1, 2, 1, 0, 1], [2, 3, 1, 2, 3, 2], [0, 2, 6, 2, 1, 0], [1, 0, 2, 3, 1, 1], [0, 2, 1, 2, 3, 1]]
                self.locked_cells = {(1, 0), (3, 2)}
                self.start_pos = (0, 0)
                self.end_pos = (5, 5)
            elif level == 5:
                self.time_limit = 140
                self.max_rotations = 14
                self.grid_type = [[2, 3, 2, 1, 0, 1], [1, 6, 1, 3, 2, 0], [3, 2, 3, 2, 6, 2], [0, 3, 0, 1, 3, 1], [1, 2, 3, 6, 1, 2], [0, 1, 2, 2, 3, 1]]
                self.locked_cells = {(1, 1), (2, 4), (4, 3)}
                self.start_pos = (0, 0)
                self.end_pos = (5, 5)
            elif level == 6:
                self.time_limit = 150
                self.max_rotations = 12
                self.grid_type = [[2, 3, 4, 1, 2, 1], [3, 6, 1, 2, 3, 2], [1, 2, 3, 6, 4, 1], [4, 3, 6, 1, 2, 3], [1, 2, 3, 2, 6, 2], [1, 3, 2, 4, 1, 1]]
                self.locked_cells = {(1, 1), (2, 3), (3, 2), (4, 4)}
                self.start_pos = (0, 0)
                self.end_pos = (5, 5)
            self.source_direction = self.LEFT

        elif level <= 9:
            self.size = 7
            if level == 7:
                self.time_limit = 160
                self.max_rotations = 10
                self.grid_type = [[2, 5, 2, 1, 3, 2, 1], [3, 1, 4, 2, 5, 1, 3], [2, 3, 1, 5, 2, 4, 2], [0, 5, 3, 1, 5, 2, 0], [1, 2, 5, 2, 1, 4, 1], [3, 5, 1, 3, 2, 5, 3], [2, 1, 3, 0, 2, 1, 2]]
                self.start_pos = (0, 0)
                self.end_pos = (6, 6)
            elif level == 8:
                self.time_limit = 170
                self.max_rotations = 9
                self.grid_type = [[2, 3, 5, 4, 2, 1, 3], [5, 1, 2, 3, 5, 2, 1], [1, 5, 3, 1, 5, 3, 2], [4, 2, 1, 5, 2, 1, 5], [2, 3, 5, 3, 4, 2, 1], [1, 2, 1, 2, 3, 5, 2], [3, 1, 5, 2, 1, 2, 1]]
                self.start_pos = (0, 0)
                self.end_pos = (6, 6)
            elif level == 9:
                self.time_limit = 180
                self.max_rotations = 8
                self.grid_type = [[2, 5, 3, 4, 5, 3, 2], [3, 1, 5, 1, 3, 5, 1], [5, 4, 2, 3, 5, 4, 3], [1, 3, 5, 1, 3, 5, 2], [4, 2, 3, 5, 4, 2, 1], [1, 5, 1, 3, 5, 1, 3], [2, 3, 5, 4, 2, 3, 2]]
                self.start_pos = (0, 0)
                self.end_pos = (6, 6)
            self.source_direction = self.LEFT

        self.grid_rotation = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) in self.locked_cells:
                    self.grid_type[r][c] = self.PIPE_LOCKED
                if self.grid_type[r][c] == self.PIPE_ONE_WAY or self.grid_type[r][c] == self.PIPE_LOCKED:
                    self.grid_rotation[r][c] = random.randint(0, 3) 
                elif self.grid_type[r][c] != self.PIPE_EMPTY:
                    self.grid_rotation[r][c] = random.randint(0, 3)
        
    def rotate_pipe(self, r, c):
        if self.grid_type[r][c] in [self.PIPE_EMPTY, self.PIPE_ONE_WAY, self.PIPE_LOCKED]:
            return
        if self.rotation_count < self.max_rotations:
            self.grid_rotation[r][c] = (self.grid_rotation[r][c] + 1) % 4
            self.rotation_count += 1
            
    def check_connection(self, r1, c1, r2, c2):
        if not (0 <= r1 < self.size and 0 <= c1 < self.size and 0 <= r2 < self.size and 0 <= c2 < self.size):
            return False
        if self.grid_type[r1][c1] == self.PIPE_EMPTY or self.grid_type[r2][c2] == self.PIPE_EMPTY:
            return False
        dir_1_to_2, dir_2_to_1 = -1, -1
        if r1 == r2:
            if c2 > c1: dir_1_to_2, dir_2_to_1 = self.RIGHT, self.LEFT
            elif c2 < c1: dir_1_to_2, dir_2_to_1 = self.LEFT, self.RIGHT
        elif c1 == c2:
            if r2 > r1: dir_1_to_2, dir_2_to_1 = self.BOTTOM, self.TOP
            elif r2 < r1: dir_1_to_2, dir_2_to_1 = self.TOP, self.BOTTOM
                
        if dir_1_to_2 == -1: return False
        opens_1 = self.PIPE_CONNECTIONS.get(self.grid_type[r1][c1], {}).get(self.grid_rotation[r1][c1], [])
        opens_2 = self.PIPE_CONNECTIONS.get(self.grid_type[r2][c2], {}).get(self.grid_rotation[r2][c2], [])
        return (dir_1_to_2 in opens_1) and (dir_2_to_1 in opens_2)

    def check_flow(self):
        start_r, start_c = self.start_pos
        if self.grid_type[start_r][start_c] == self.PIPE_EMPTY: return False, set()
        start_opens = self.PIPE_CONNECTIONS.get(self.grid_type[start_r][start_c], {}).get(self.grid_rotation[start_r][start_c], [])
        if self.source_direction not in start_opens: return False, set()
            
        visited = set([(start_r, start_c)])
        stack = [(start_r, start_c, self.source_direction)]
        reached_end = False
        while stack:
            r, c, entry_dir = stack.pop()
            if (r, c) == self.end_pos: reached_end = True
            cur_type, cur_rot = self.grid_type[r][c], self.grid_rotation[r][c]
            cur_opens = self.PIPE_CONNECTIONS.get(cur_type, {}).get(cur_rot, [])
            for outgoing_dir in cur_opens:
                if outgoing_dir == entry_dir: continue
                if cur_type == self.PIPE_ONE_WAY:
                    allowed_entry = [self.BOTTOM, self.LEFT, self.TOP, self.RIGHT][cur_rot]
                    if entry_dir != allowed_entry: continue
                dr, dc = 0, 0
                if outgoing_dir == self.TOP: dr = -1
                elif outgoing_dir == self.BOTTOM: dr = 1
                elif outgoing_dir == self.LEFT: dc = -1
                elif outgoing_dir == self.RIGHT: dc = 1
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.size and 0 <= nc < self.size) or (nr, nc) in visited: continue
                next_entry_dir = {self.TOP:self.BOTTOM, self.BOTTOM:self.TOP, self.LEFT:self.RIGHT, self.RIGHT:self.LEFT}[outgoing_dir]
                if self.check_connection(r, c, nr, nc):
                    if self.grid_type[nr][nc] == self.PIPE_ONE_WAY:
                        if next_entry_dir != [self.BOTTOM, self.LEFT, self.TOP, self.RIGHT][self.grid_rotation[nr][nc]]: continue
                    visited.add((nr, nc))
                    stack.append((nr, nc, next_entry_dir))
        return reached_end, visited
