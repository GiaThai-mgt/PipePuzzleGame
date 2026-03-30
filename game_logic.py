import random

class PipeGameLogic:
    # --- Định nghĩa loại ống ---
    PIPE_EMPTY = 0
    PIPE_STRAIGHT = 1
    PIPE_L_SHAPE = 2
    PIPE_T_SHAPE = 3
    PIPE_CROSS = 4
    PIPE_ONE_WAY = 5
    
    # --- Định nghĩa hướng ---
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    
    # --- Ánh xạ kết nối ---
    PIPE_CONNECTIONS = {
        PIPE_STRAIGHT: {
            0: (TOP, BOTTOM), 1: (LEFT, RIGHT),
            2: (TOP, BOTTOM), 3: (LEFT, RIGHT)
        },
        PIPE_L_SHAPE: {
            0: (TOP, RIGHT), 1: (RIGHT, BOTTOM),
            2: (BOTTOM, LEFT), 3: (LEFT, TOP)
        },
        PIPE_T_SHAPE: {
            0: (LEFT, TOP, RIGHT), 1: (TOP, RIGHT, BOTTOM),
            2: (RIGHT, BOTTOM, LEFT), 3: (BOTTOM, LEFT, TOP)
        },
        PIPE_CROSS: {
            0: (TOP, RIGHT, BOTTOM, LEFT), 1: (TOP, RIGHT, BOTTOM, LEFT),
            2: (TOP, RIGHT, BOTTOM, LEFT), 3: (TOP, RIGHT, BOTTOM, LEFT)
        },
        # Ống một chiều cố định
        PIPE_ONE_WAY: {
            0: (TOP, BOTTOM), # Đầu ra: TOP, Đầu vào: BOTTOM
            1: (LEFT, RIGHT), # Đầu ra: RIGHT, Đầu vào: LEFT
            2: (BOTTOM, TOP), # Đầu ra: BOTTOM, Đầu vào: TOP
            3: (RIGHT, LEFT)  # Đầu ra: LEFT, Đầu vào: RIGHT
        }
    }
    
    def __init__(self):
        self.current_level = 1
        self.max_level = 4
        self.load_level(self.current_level)
    
    def load_level(self, level):
        self.current_level = level
        # Khởi tạo bản đồ thiết kế rối dần từ rễ đến khó
        if level == 1:
            # Level 1: 5x5 Nhẹ nhàng, dễ thở, một số lượng ống rác (noise) nhỏ
            self.size = 5
            self.grid_type = [
                [1, 2, 0, 2, 1],
                [2, 1, 0, 1, 0],
                [0, 2, 1, 2, 1],
                [1, 0, 2, 1, 0],
                [0, 1, 0, 2, 1]
            ]
            self.start_pos = (0, 0)
            self.end_pos = (4, 4)
            self.source_direction = self.LEFT
            
        elif level == 2:
            # Level 2: 6x6 Bắt đầu có T-shape và Cross đánh lừa hướng đi lưới nhện
            self.size = 6
            self.grid_type = [
                [2, 2, 1, 0, 2, 1],
                [1, 1, 0, 2, 1, 0],
                [2, 3, 1, 2, 0, 2],
                [0, 2, 2, 4, 2, 1],
                [1, 0, 1, 1, 1, 0],
                [0, 2, 1, 2, 2, 1] 
            ]
            self.start_pos = (0, 0)
            self.end_pos = (5, 5)
            self.source_direction = self.LEFT
            
        elif level == 3:
            # Level 3: 7x7 Có ống đường một chiều (One Way - số 5) mấu chốt, đánh lừa xoay
            self.size = 7
            self.grid_type = [
                [2, 1, 2, 0, 2, 1, 2],
                [1, 5, 3, 1, 2, 0, 1],
                [0, 2, 1, 2, 1, 2, 0],
                [1, 2, 2, 4, 5, 2, 1],
                [2, 5, 1, 1, 0, 1, 2],
                [0, 2, 1, 4, 2, 2, 2],
                [1, 0, 2, 1, 1, 2, 1]
            ]
            self.start_pos = (1, 0)
            self.end_pos = (6, 6)
            self.source_direction = self.LEFT
            
        elif level == 4:
            # Level 4: 8x8 Mê Cung Ác Mộng (Nightmare), dồn toàn bộ ống T, Cross, 1 chiều chi chít.
            self.size = 8
            self.grid_type = [
                [2, 2, 1, 2, 4, 2, 1, 2],
                [3, 1, 4, 1, 2, 5, 2, 1],
                [2, 1, 5, 4, 1, 2, 2, 4],
                [1, 2, 1, 2, 2, 1, 3, 2],
                [2, 4, 2, 5, 1, 2, 1, 1],
                [1, 1, 3, 2, 1, 4, 2, 2],
                [2, 2, 2, 1, 4, 1, 2, 2],
                [1, 2, 2, 1, 3, 1, 2, 1]
            ]
            self.start_pos = (0, 0)
            self.end_pos = (7, 7)
            self.source_direction = self.LEFT

        # Quay ngẫu nhiên ban đầu để người chơi tự giải
        self.grid_rotation = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                if self.grid_type[r][c] == self.PIPE_ONE_WAY:
                    # Thiết lập góc quay cứng bắt buộc cho ống một chiều theo map thiết kế
                    if self.current_level == 3:
                        if (r, c) == (1, 1): self.grid_rotation[r][c] = 1 # Trái -> Phải
                        elif (r, c) == (4, 1): self.grid_rotation[r][c] = 0 # Trên -> Dưới
                        elif (r, c) == (3, 4): self.grid_rotation[r][c] = 1 # Trái -> Phải
                        else: self.grid_rotation[r][c] = 0
                    elif self.current_level == 4:
                        if (r, c) == (2, 2): self.grid_rotation[r][c] = 1 # Trái -> Phải
                        elif (r, c) == (1, 5): self.grid_rotation[r][c] = 0 # Trên -> Dưới
                        elif (r, c) == (4, 3): self.grid_rotation[r][c] = 2 # Dưới -> Trên
                        else: self.grid_rotation[r][c] = 0
                elif self.grid_type[r][c] != self.PIPE_EMPTY:
                    self.grid_rotation[r][c] = random.randint(0, 3)
        
    def rotate_pipe(self, r, c):
        # ỐNG ĐỊNH HƯỚNG BỊ CỐ ĐỊNH, KHÔNG THỂ XOAY!
        if self.grid_type[r][c] != self.PIPE_EMPTY and self.grid_type[r][c] != self.PIPE_ONE_WAY:
            self.grid_rotation[r][c] = (self.grid_rotation[r][c] + 1) % 4
            
    def check_connection(self, r1, c1, r2, c2):
        if not (0 <= r1 < self.size and 0 <= c1 < self.size and 0 <= r2 < self.size and 0 <= c2 < self.size):
            return False
            
        if self.grid_type[r1][c1] == self.PIPE_EMPTY or self.grid_type[r2][c2] == self.PIPE_EMPTY:
            return False

        dir_1_to_2 = -1
        dir_2_to_1 = -1
        
        if r1 == r2:
            if c2 > c1:
                dir_1_to_2, dir_2_to_1 = self.RIGHT, self.LEFT
            elif c2 < c1:
                dir_1_to_2, dir_2_to_1 = self.LEFT, self.RIGHT
        elif c1 == c2:
            if r2 > r1:
                dir_1_to_2, dir_2_to_1 = self.BOTTOM, self.TOP
            elif r2 < r1:
                dir_1_to_2, dir_2_to_1 = self.TOP, self.BOTTOM
                
        if dir_1_to_2 == -1: return False
        
        opens_1 = self.PIPE_CONNECTIONS[self.grid_type[r1][c1]][self.grid_rotation[r1][c1]]
        opens_2 = self.PIPE_CONNECTIONS[self.grid_type[r2][c2]][self.grid_rotation[r2][c2]]
        
        return (dir_1_to_2 in opens_1) and (dir_2_to_1 in opens_2)

    def check_flow(self):
        """Trả về (True/False nếu Win, Tập hợp các ô có nước chảy tới (r, c))"""
        start_r, start_c = self.start_pos
        if self.grid_type[start_r][start_c] == self.PIPE_EMPTY:
            return False, set()
            
        # Kiểm tra ống bắt đầu có khớp nguồn nước không
        start_opens = self.PIPE_CONNECTIONS[self.grid_type[start_r][start_c]][self.grid_rotation[start_r][start_c]]
        if self.source_direction not in start_opens:
            return False, set()
            
        visited = set([(start_r, start_c)])
        stack = [(start_r, start_c, self.source_direction)]
        reached_end = False
        
        while stack:
            r, c, entry_dir = stack.pop()
            if (r, c) == self.end_pos:
                reached_end = True
                
            cur_type = self.grid_type[r][c]
            cur_rot = self.grid_rotation[r][c]
            cur_opens = self.PIPE_CONNECTIONS[cur_type][cur_rot]
            
            for outgoing_dir in cur_opens:
                if outgoing_dir == entry_dir:
                    continue
                    
                if cur_type == self.PIPE_ONE_WAY:
                    allowed_entry = None
                    if cur_rot == 0: allowed_entry = self.BOTTOM
                    elif cur_rot == 1: allowed_entry = self.LEFT
                    elif cur_rot == 2: allowed_entry = self.TOP
                    elif cur_rot == 3: allowed_entry = self.RIGHT
                    
                    if entry_dir != allowed_entry:
                        continue
                        
                dr, dc = 0, 0
                if outgoing_dir == self.TOP: dr = -1
                elif outgoing_dir == self.BOTTOM: dr = 1
                elif outgoing_dir == self.LEFT: dc = -1
                elif outgoing_dir == self.RIGHT: dc = 1
                
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.size and 0 <= nc < self.size):
                    continue
                if (nr, nc) in visited:
                    continue
                    
                next_entry_dir = -1
                if outgoing_dir == self.TOP: next_entry_dir = self.BOTTOM
                elif outgoing_dir == self.BOTTOM: next_entry_dir = self.TOP
                elif outgoing_dir == self.LEFT: next_entry_dir = self.RIGHT
                elif outgoing_dir == self.RIGHT: next_entry_dir = self.LEFT
                
                if self.check_connection(r, c, nr, nc):
                    next_pipe_type = self.grid_type[nr][nc]
                    next_pipe_rot = self.grid_rotation[nr][nc]
                    if next_pipe_type == self.PIPE_ONE_WAY:
                        allowed_next = None
                        if next_pipe_rot == 0: allowed_next = self.BOTTOM
                        elif next_pipe_rot == 1: allowed_next = self.LEFT
                        elif next_pipe_rot == 2: allowed_next = self.TOP
                        elif next_pipe_rot == 3: allowed_next = self.RIGHT
                        if next_entry_dir != allowed_next:
                            continue 
                            
                    visited.add((nr, nc))
                    stack.append((nr, nc, next_entry_dir))
                    
        return reached_end, visited
