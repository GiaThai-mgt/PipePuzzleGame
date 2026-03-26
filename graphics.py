import pygame
import sys
import heapq

# ==========================================
# 1. TRỤ CỘT LOGIC (Trích từ logic game của bạn)
# ==========================================
class PipeGameLogic:
    PIPE_STRAIGHT = 1
    PIPE_L_SHAPE = 2
    PIPE_T_SHAPE = 3

    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

    PIPE_CONNECTIONS = {
        PIPE_STRAIGHT: {
            0: (TOP, BOTTOM),
            1: (LEFT, RIGHT),
            2: (TOP, BOTTOM),
            3: (LEFT, RIGHT)
        },
        PIPE_L_SHAPE: {
            0: (TOP, RIGHT),
            1: (RIGHT, BOTTOM),
            2: (BOTTOM, LEFT),
            3: (LEFT, TOP)
        },
        PIPE_T_SHAPE: {
            0: (TOP, LEFT, RIGHT),
            1: (TOP, RIGHT, BOTTOM),
            2: (RIGHT, BOTTOM, LEFT),
            3: (BOTTOM, LEFT, TOP)
        }
    }

    DIRECTION_MAP = {
        "TOP": TOP,
        "RIGHT": RIGHT,
        "BOTTOM": BOTTOM,
        "LEFT": LEFT
    }

    def __init__(self):
        self.current_level = 1
        self.source_direction_locked = True
        self.load_level_by_number(1)

    def load_level_by_number(self, level_num):
        """Tải màn chơi 1 (5x5), 2 (6x6) và 3 (7x7)"""
        self.current_level = level_num
        self.source_direction_locked = (level_num < 3)

        levels = {
            1: {
                "size": 5,
                "grid_type": [
                    [1, 2, 0, 0, 1],
                    [0, 1, 1, 2, 0],
                    [0, 0, 2, 1, 0],
                    [0, 1, 0, 1, 1],
                    [2, 2, 0, 0, 1]
                ],
                "start_pos": (0, 0),
                "end_pos": (4, 4),
                "source_direction": "TOP"
            },
            2: {
                "size": 6,
                "grid_type": [
                    [2, 1, 1, 2, 0, 0],
                    [0, 0, 2, 1, 0, 0],
                    [0, 1, 1, 2, 1, 0],
                    [0, 1, 0, 0, 1, 2],
                    [0, 2, 1, 1, 2, 1],
                    [0, 0, 0, 0, 0, 1]
                ],
                "start_pos": (0, 0),
                "end_pos": (5, 5),
                "source_direction": "LEFT"
            },
            3: {
                "size": 7,
                "grid_type": [
                    [3, 1, 1, 2, 0, 0, 0],
                    [0, 0, 0, 1, 0, 2, 2],
                    [0, 1, 3, 2, 0, 1, 1],
                    [0, 1, 0, 0, 2, 2, 1],
                    [0, 2, 1, 2, 1, 0, 1],
                    [0, 0, 0, 1, 2, 1, 2],
                    [0, 0, 0, 2, 1, 1, 1]
                ],
                "start_pos": (0, 0),
                "end_pos": (6, 6),
                "source_direction": "TOP"
            }
        }
        
        data = levels.get(level_num, levels[1])
        
        self.size = data["size"]
        self.grid_type = data["grid_type"]
        
        # Tạo lưới rotation bằng 0 hết theo kích thước size
        self.grid_rotation = [[0]*self.size for _ in range(self.size)]
        
        self.start_pos = data.get("start_pos", (0, 0))
        self.end_pos = data.get("end_pos", (self.size - 1, self.size - 1))
        self.source_direction = data.get("source_direction", "TOP")

    def set_source_direction(self, direction):
        if not self.source_direction_locked:
            if direction in self.DIRECTION_MAP:
                self.source_direction = direction
                return True
        return False

    def rotate_pipe(self, r, c):
        if self.grid_type[r][c] != 0:
            self.grid_rotation[r][c] = (self.grid_rotation[r][c] + 1) % 4

    def check_connection(self, node1, node2):
        r1, c1 = node1
        r2, c2 = node2

        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False

        if not (0 <= r1 < self.size and 0 <= c1 < self.size and 0 <= r2 < self.size and 0 <= c2 < self.size):
            return False

        pipe1_type = self.grid_type[r1][c1]
        pipe1_rotation = self.grid_rotation[r1][c1]
        pipe2_type = self.grid_type[r2][c2]
        pipe2_rotation = self.grid_rotation[r2][c2]

        if pipe1_type == 0 or pipe2_type == 0:
            return False

        direction_to_node2 = -1
        direction_to_node1 = -1

        if r1 == r2:
            if c2 > c1:
                direction_to_node2 = self.RIGHT
                direction_to_node1 = self.LEFT
            else:
                direction_to_node2 = self.LEFT
                direction_to_node1 = self.RIGHT
        elif c1 == c2:
            if r2 > r1:
                direction_to_node2 = self.BOTTOM
                direction_to_node1 = self.TOP
            else:
                direction_to_node2 = self.TOP
                direction_to_node1 = self.BOTTOM
        
        opens_pipe1 = self.PIPE_CONNECTIONS[pipe1_type][pipe1_rotation]
        opens_pipe2 = self.PIPE_CONNECTIONS[pipe2_type][pipe2_rotation]

        return (direction_to_node2 in opens_pipe1) and (direction_to_node1 in opens_pipe2)

    def check_win(self):
        if self.grid_type[self.start_pos[0]][self.start_pos[1]] == 0 or \
           self.grid_type[self.end_pos[0]][self.end_pos[1]] == 0:
            return False

        visited = set()
        stack = []

        start_r, start_c = self.start_pos
        initial_entry_direction = self.DIRECTION_MAP.get(self.source_direction)
        
        if initial_entry_direction is None:
            return False

        start_pipe_type = self.grid_type[start_r][start_c]
        start_pipe_rotation = self.grid_rotation[start_r][start_c]
        start_pipe_openings = self.PIPE_CONNECTIONS[start_pipe_type][start_pipe_rotation]

        if initial_entry_direction not in start_pipe_openings:
            return False

        stack.append(((start_r, start_c), initial_entry_direction))
        visited.add((start_r, start_c))

        while stack:
            (r, c), entry_direction = stack.pop()

            if (r, c) == self.end_pos:
                return True

            current_pipe_type = self.grid_type[r][c]
            current_pipe_rotation = self.grid_rotation[r][c]
            current_pipe_openings = self.PIPE_CONNECTIONS[current_pipe_type][current_pipe_rotation]

            for outgoing_dir in current_pipe_openings:
                if (outgoing_dir == self.TOP and entry_direction == self.BOTTOM) or \
                   (outgoing_dir == self.BOTTOM and entry_direction == self.TOP) or \
                   (outgoing_dir == self.LEFT and entry_direction == self.RIGHT) or \
                   (outgoing_dir == self.RIGHT and entry_direction == self.LEFT):
                    continue
                
                dr, dc = 0, 0
                if outgoing_dir == self.TOP: dr = -1
                elif outgoing_dir == self.BOTTOM: dr = 1
                elif outgoing_dir == self.LEFT: dc = -1
                elif outgoing_dir == self.RIGHT: dc = 1
                
                nr, nc = r + dr, c + dc
                
                if not (0 <= nr < self.size and 0 <= nc < self.size) or (nr, nc) in visited:
                    continue

                if outgoing_dir == self.TOP: next_entry_dir = self.BOTTOM
                elif outgoing_dir == self.RIGHT: next_entry_dir = self.LEFT
                elif outgoing_dir == self.BOTTOM: next_entry_dir = self.TOP
                elif outgoing_dir == self.LEFT: next_entry_dir = self.RIGHT
                
                if self.check_connection((r, c), (nr, nc)):
                    stack.append(((nr, nc), next_entry_dir))
                    visited.add((nr, nc))
        return False

# ==========================================
# 2. TRỤ CỘT AI (A* Algorithm)
# ==========================================
class PipeGameAI:
    def __init__(self, game):
        self.game = game

    def heuristic(self, r, c):
        end_r, end_c = self.game.end_pos
        return abs(r - end_r) + abs(c - end_c)

    def solve(self):
        start_r, start_c = self.game.start_pos
        end_r, end_c = self.game.end_pos
        
        initial_entry_direction = self.game.DIRECTION_MAP.get(self.game.source_direction)
        if initial_entry_direction is None: return None
            
        start_state = (start_r, start_c, initial_entry_direction)
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start_r, start_c), 0, start_state))
        
        came_from = {}
        g_score = {start_state: 0}
        
        while open_set:
            f, g, current_state = heapq.heappop(open_set)
            r, c, entry_dir = current_state
            
            if (r, c) == (end_r, end_c):
                end_pipe_type = self.game.grid_type[r][c]
                valid_end_rot = -1
                for rot in range(4):
                    if entry_dir in self.game.PIPE_CONNECTIONS[end_pipe_type][rot]:
                        valid_end_rot = rot
                        break
                if valid_end_rot != -1:
                    return self.reconstruct_path(came_from, current_state, valid_end_rot)
            
            current_pipe_type = self.game.grid_type[r][c]
            
            for rot in range(4):
                openings = self.game.PIPE_CONNECTIONS[current_pipe_type][rot]
                if entry_dir not in openings:
                    continue
                    
                for outgoing_dir in openings:
                    if outgoing_dir == entry_dir:
                        continue
                        
                    dr, dc = 0, 0
                    if outgoing_dir == self.game.TOP:
                        dr = -1; next_entry_dir = self.game.BOTTOM
                    elif outgoing_dir == self.game.BOTTOM:
                        dr = 1; next_entry_dir = self.game.TOP
                    elif outgoing_dir == self.game.LEFT:
                        dc = -1; next_entry_dir = self.game.RIGHT
                    elif outgoing_dir == self.game.RIGHT:
                        dc = 1; next_entry_dir = self.game.LEFT
                    
                    nr, nc = r + dr, c + dc
                    
                    if not (0 <= nr < self.game.size and 0 <= nc < self.game.size) or self.game.grid_type[nr][nc] == 0:
                        continue
                        
                    next_state = (nr, nc, next_entry_dir)
                    tentative_g_score = g + 1
                    
                    if next_state not in g_score or tentative_g_score < g_score[next_state]:
                        came_from[next_state] = (current_state, rot)
                        g_score[next_state] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(nr, nc)
                        heapq.heappush(open_set, (f_score, tentative_g_score, next_state))
        return None

    def reconstruct_path(self, came_from, current_state, end_rot):
        rotations_to_apply = {}
        r, c, _ = current_state
        rotations_to_apply[(r, c)] = end_rot
        
        while current_state in came_from:
            prev_state, prev_rot = came_from[current_state]
            pr, pc, _ = prev_state
            rotations_to_apply[(pr, pc)] = prev_rot
            current_state = prev_state
        return rotations_to_apply

    def apply_solution(self):
        best_rotations = self.solve()
        if best_rotations:
            # Lắp các góc quay vào lưới thực
            for (r, c), rot in best_rotations.items():
                self.game.grid_rotation[r][c] = rot
            return True
        return False

# ==========================================
# 3. TRỤ CỘT ĐỒ HỌA (Pygame GUI)
# ==========================================
def draw_pipes(screen, game, cell_size, margin_top, margin_left):
    for r in range(game.size):
        for c in range(game.size):
            x = margin_left + c * cell_size
            y = margin_top + r * cell_size
            
            rect = pygame.Rect(x, y, cell_size, cell_size)
            # Nền của 1 ô
            pygame.draw.rect(screen, (30, 30, 30), rect)
            pygame.draw.rect(screen, (70, 70, 70), rect, 1) # Viền ô

            # Điểm bắt đầu và kết thúc
            if (r, c) == game.start_pos:
                pygame.draw.rect(screen, (40, 100, 40), rect) # Xanh lá
            elif (r, c) == game.end_pos:
                pygame.draw.rect(screen, (100, 40, 40), rect) # Đỏ thẫm

            pipe_type = game.grid_type[r][c]
            if pipe_type != 0:
                rotation = game.grid_rotation[r][c]
                openings = game.PIPE_CONNECTIONS[pipe_type][rotation]
                
                center_x = x + cell_size // 2
                center_y = y + cell_size // 2
                
                pipe_color = (180, 180, 180) # Màu xám bình thường
                if game.check_win():
                    pipe_color = (0, 200, 255) # Nếu thắng thì ống phát sáng xanh lam
                
                # Cục chia nước giữa tâm ô
                pygame.draw.circle(screen, pipe_color, (center_x, center_y), cell_size // 4)
                
                # Các ngã rẽ đường ống
                w = cell_size // 3 # Độ dày của lòng ống
                if game.TOP in openings:
                    pygame.draw.rect(screen, pipe_color, (center_x - w//2, y, w, cell_size//2))
                if game.BOTTOM in openings:
                    pygame.draw.rect(screen, pipe_color, (center_x - w//2, center_y, w, cell_size//2))
                if game.LEFT in openings:
                    pygame.draw.rect(screen, pipe_color, (x, center_y - w//2, cell_size//2, w))
                if game.RIGHT in openings:
                    pygame.draw.rect(screen, pipe_color, (center_x, center_y - w//2, cell_size//2, w))

def main():
    pygame.init()
    
    cell_size = 80
    margin_top = 100
    margin_left = 50
    
    game = PipeGameLogic()
    # Khởi tạo mặc định chạy luôn Level 1
    game.load_level_by_number(1)
    
    # Render với màn 7x7 lớn nhất để không bị thay đổi resize
    window_width = 7 * cell_size + margin_left * 2
    window_height = 7 * cell_size + margin_top + 50
    screen = pygame.display.set_mode((window_width, window_height))
    
    font = pygame.font.SysFont("Verdana", 20, bold=True)
    small_font = pygame.font.SysFont("Verdana", 16)
    
    # Nút bấm UI
    btn_solve = pygame.Rect(margin_left, 15, 140, 40)
    btn_next = pygame.Rect(margin_left + 160, 15, 140, 40)
    btn_source = pygame.Rect(margin_left + 320, 15, 180, 40)
    
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((20, 20, 20))
        
        # Cập nhật Title hiển thị Win
        if game.check_win():
            pygame.display.set_caption(f"PipeGame - Level {game.current_level} - YOU WIN!")
        else:
            pygame.display.set_caption(f"PipeGame - Level {game.current_level}")
            
        # Nút Giải Bằng A*
        pygame.draw.rect(screen, (50, 150, 250), btn_solve, border_radius=5)
        text_solve = font.render("Solve (A*)", True, (255, 255, 255))
        screen.blit(text_solve, (btn_solve.x + 15, btn_solve.y + 8))
        
        # Nút Kế Tiếp
        pygame.draw.rect(screen, (200, 150, 50), btn_next, border_radius=5)
        text_next = font.render(f"Next Lvl: {(game.current_level % 3) + 1}", True, (255, 255, 255))
        screen.blit(text_next, (btn_next.x + 10, btn_next.y + 8))

        # Hiển thị hoặc Nút chuyển đổi Hướng Nguồn (Dành cho Màn 3)
        if game.source_direction_locked:
            pygame.draw.rect(screen, (80, 80, 80), btn_source, border_radius=5)
            text_src = font.render(f"Src: {game.source_direction} (Khóa)", True, (200, 200, 200))
        else:
            pygame.draw.rect(screen, (150, 50, 200), btn_source, border_radius=5)
            text_src = font.render(f"Mở Src: {game.source_direction}", True, (255, 255, 255))
        screen.blit(text_src, (btn_source.x + 10, btn_source.y + 8))
            
        # Thông tin Map
        text_info = font.render(f"Map Size: {game.size}x{game.size}  |  Click để Xoay", True, (200, 255, 200))
        screen.blit(text_info, (margin_left, 65))
        
        # Vẽ cấu trúc Lưới và Ống
        draw_pipes(screen, game, cell_size, margin_top, margin_left)
        
        pygame.display.flip()
        
        # Event handler xử lý
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    
                    # Hành vi Nút Solve (AI)
                    if btn_solve.collidepoint(pos):
                        ai = PipeGameAI(game)
                        if not game.source_direction_locked:
                            # Nếu nguồn tự do ở màn 3, ta thử hack mọi hướng
                            solved = False
                            for d in ["TOP", "RIGHT", "BOTTOM", "LEFT"]:
                                game.set_source_direction(d)
                                ai_temp = PipeGameAI(game)
                                if ai_temp.apply_solution():
                                    solved = True
                                    break
                        else:
                            # Nguồn cố định, giải thủ công
                            ai.apply_solution()
                            
                    # Hành vi Nút Next Level
                    elif btn_next.collidepoint(pos):
                        nxt = game.current_level + 1
                        if nxt > 3: nxt = 1
                        game.load_level_by_number(nxt)

                    # Đổi hướng khi đang không khóa nguồn
                    elif btn_source.collidepoint(pos) and not game.source_direction_locked:
                        dirs = ["TOP", "RIGHT", "BOTTOM", "LEFT"]
                        curr_idx = dirs.index(game.source_direction)
                        game.set_source_direction(dirs[(curr_idx + 1) % 4])
                        
                    # Hành vi nhấp vào Map để tương tác
                    else:
                        mx, my = pos
                        if margin_left <= mx < margin_left + game.size * cell_size and \
                           margin_top <= my < margin_top + game.size * cell_size:
                            c = (mx - margin_left) // cell_size
                            r = (my - margin_top) // cell_size
                            game.rotate_pipe(r, c)
                            
        clock.tick(30) # Fix FPS cho mượt
        
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
