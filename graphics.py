import pygame
import math

class PipeGameGraphics:
    # --- Colors ---
    BG_COLOR = (20, 20, 30)
    GRID_COLOR = (40, 40, 50)
    GREY = (100, 100, 100)
    CYAN = (0, 255, 255)
    SOURCE_COLOR = (0, 150, 255)
    SINK_COLOR = (255, 100, 100)
    BTN_COLOR = (50, 50, 80)
    BTN_HOVER = (70, 70, 100)
    BTN_TEXT = (255, 255, 255)
    
    def __init__(self, w=800, h=800):
        pygame.init()
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Pipe Puzzle - Pygame")
        
        # Cấu hình vùng lưới: căn giữa màn hình
        self.grid_area_size = 600
        self.font = pygame.font.SysFont("Courier New", 24, bold=True)
        
        # Kích thước khung lưới tuỳ thuộc vào Level
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def update_grid_params(self, grid_size):
        self.cell_size = self.grid_area_size // grid_size
        self.offset_x = (self.width - self.grid_area_size) // 2
        self.offset_y = (self.height - self.grid_area_size) // 2 - 50 # Chừa chỗ cho UI bên dưới
        self.pipe_width = self.cell_size // 3
        
    def draw(self, logic, flow_visited):
        self.screen.fill(self.BG_COLOR)
        self.update_grid_params(logic.size)
        
        # Vẽ Lưới
        for r in range(logic.size):
            for c in range(logic.size):
                cx = self.offset_x + c * self.cell_size
                cy = self.offset_y + r * self.cell_size
                rect = (cx, cy, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)
                
                # Vẽ điểm Start / End đánh dấu nguồn gốc màu nền
                if (r, c) == logic.start_pos:
                    pygame.draw.rect(self.screen, self.SOURCE_COLOR, rect, 3)
                if (r, c) == logic.end_pos:
                    pygame.draw.rect(self.screen, self.SINK_COLOR, rect, 3)
                    
                pipe_type = logic.grid_type[r][c]
                pipe_rot = logic.grid_rotation[r][c]
                
                if pipe_type != 0:
                    is_flow = (r, c) in flow_visited
                    color = self.CYAN if is_flow else self.GREY
                    self.draw_pipe(pipe_type, pipe_rot, rect, color, logic)
                    
        # Vẽ nút UI
        self.draw_buttons()
        pygame.display.flip()

    def draw_pipe(self, p_type, rot, rect, color, logic):
        # rect = (x, y, w, h)
        x, y, w, h = rect
        cx = x + w // 2
        cy = y + h // 2
        pw = self.pipe_width
        
        # Các đoạn nối từ tâm ra (0: TOP, 1: RIGHT, 2: BOTTOM, 3: LEFT)
        arms = []
        if p_type == logic.PIPE_STRAIGHT:
            if rot == 0 or rot == 2: arms = [0, 2]
            else: arms = [1, 3]
        elif p_type == logic.PIPE_L_SHAPE:
            if rot == 0: arms = [0, 1]
            elif rot == 1: arms = [1, 2]
            elif rot == 2: arms = [2, 3]
            elif rot == 3: arms = [3, 0]
        elif p_type == logic.PIPE_T_SHAPE:
            if rot == 0: arms = [0, 1, 3] # Left, Top, Right
            elif rot == 1: arms = [0, 1, 2]
            elif rot == 2: arms = [1, 2, 3]
            elif rot == 3: arms = [2, 3, 0]
        elif p_type == logic.PIPE_CROSS:
            arms = [0, 1, 2, 3]
        elif p_type == logic.PIPE_ONE_WAY:
            if rot == 0 or rot == 2: arms = [0, 2]
            else: arms = [1, 3]

        # Khối tròn trung tâm (nơi các nhánh ống giao nhau)
        pygame.draw.rect(self.screen, color, (cx - pw//2, cy - pw//2, pw, pw))

        # Vẽ từng nhánh (arm)
        for arm in arms:
            if arm == 0: pygame.draw.rect(self.screen, color, (cx - pw//2, y, pw, h//2))
            elif arm == 1: pygame.draw.rect(self.screen, color, (cx, cy - pw//2, w//2, pw))
            elif arm == 2: pygame.draw.rect(self.screen, color, (cx - pw//2, cy, pw, h//2))
            elif arm == 3: pygame.draw.rect(self.screen, color, (x, cy - pw//2, w//2, pw))
            
        # Vẽ thêm mũi tên cho ống 1 chiều
        if p_type == logic.PIPE_ONE_WAY:
            self.draw_arrow(cx, cy, pw, rot)

    def draw_arrow(self, cx, cy, pw, rot):
        # Mũi tên tam giác chỉ hướng cố định
        arrow_color = (255, 50, 50) # Màu đỏ tươi đánh dấu ống cố định
        sz = pw * 0.5 # Kích thước mũi tên to hơn xíu

        pts = []
        
        # rot định nghĩa hướng mũi tên đang cắm tới
        if rot == 0: # LÊN
            pts = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
        elif rot == 1: # PHẢI
            pts = [(cx + sz, cy), (cx - sz, cy - sz), (cx - sz, cy + sz)]
        elif rot == 2: # XUỐNG
            pts = [(cx, cy + sz), (cx - sz, cy - sz), (cx + sz, cy - sz)]
        elif rot == 3: # TRÁI
            pts = [(cx - sz, cy), (cx + sz, cy - sz), (cx + sz, cy + sz)]
            
        pygame.draw.polygon(self.screen, arrow_color, pts)

    def draw_buttons(self):
        # Nút Next Level và Reset
        self.btn_next = pygame.Rect(self.width//2 - 150, self.height - 80, 130, 40)
        self.btn_reset = pygame.Rect(self.width//2 + 20, self.height - 80, 130, 40)
        self.btn_ai = pygame.Rect(self.width//2 - 65, self.height - 130, 130, 40)
        
        mouse_pos = pygame.mouse.get_pos()
        
        c_next = self.BTN_HOVER if self.btn_next.collidepoint(mouse_pos) else self.BTN_COLOR
        c_reset = self.BTN_HOVER if self.btn_reset.collidepoint(mouse_pos) else self.BTN_COLOR
        c_ai = self.BTN_HOVER if self.btn_ai.collidepoint(mouse_pos) else self.BTN_COLOR
        
        pygame.draw.rect(self.screen, c_next, self.btn_next, border_radius=5)
        pygame.draw.rect(self.screen, c_reset, self.btn_reset, border_radius=5)
        pygame.draw.rect(self.screen, c_ai, self.btn_ai, border_radius=5)
        
        txt_next = self.font.render("Next Lvl", True, self.BTN_TEXT)
        txt_reset = self.font.render("Reset", True, self.BTN_TEXT)
        txt_ai = self.font.render("Auto AI", True, (255, 200, 50))
        
        self.screen.blit(txt_next, (self.btn_next.x + 10, self.btn_next.y + 8))
        self.screen.blit(txt_reset, (self.btn_reset.x + 25, self.btn_reset.y + 8))
        self.screen.blit(txt_ai, (self.btn_ai.x + 10, self.btn_ai.y + 8))

    def get_grid_pos(self, mouse_pos):
        mx, my = mouse_pos
        if self.offset_x <= mx <= self.offset_x + self.grid_area_size and \
           self.offset_y <= my <= self.offset_y + self.grid_area_size:
            c = (mx - self.offset_x) // self.cell_size
            r = (my - self.offset_y) // self.cell_size
            return r, c
        return None
