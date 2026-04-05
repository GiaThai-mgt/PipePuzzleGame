import pygame
import math

class PipeGameGraphics:
    # --- Colors ---
    BG_COLOR = (8, 12, 22)
    BG_TOP = (5, 10, 20)
    BG_BOTTOM = (12, 20, 35)

    GRID_COLOR = (0, 220, 255)      # Neon blue
    GRID_GLOW = (0, 180, 255, 70)

    # Blue gradient pipe colors (for smooth glossy effect)
    PIPE_BODY_GRAD1 = (60, 110, 180)   # Deep blue
    PIPE_BODY_GRAD2 = (90, 170, 220)   # Lighter blue
    PIPE_BODY_GRAD3 = (120, 200, 255)  # Soft blue
    PIPE_EDGE = (100, 160, 220)
    PIPE_HIGHLIGHT = (255, 255, 255)
    PIPE_SHADOW = (40, 60, 90)

    # Button gradient colors
    BTN_GRAD_TOP = (70, 120, 200)
    BTN_GRAD_BOTTOM = (40, 80, 140)
    BTN_GRAD_HOVER_TOP = (110, 170, 255)
    BTN_GRAD_HOVER_BOTTOM = (60, 120, 200)

    GREY = (140, 140, 160)
    CYAN = (0, 220, 255)

    FLOW_COLOR = (0, 245, 255)
    FLOW_GLOW = (0, 255, 255, 110)

    SOURCE_COLOR = (0, 200, 255)
    SINK_COLOR = (255, 120, 120)

    BTN_COLOR = (60, 70, 120)
    BTN_HOVER = (90, 110, 180)
    BTN_TEXT = (255, 255, 255)
    BTN_SHADOW = (30, 35, 60)

    def __init__(self, w=800, h=800):
        pygame.init()
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Pipe Puzzle - Pygame")

        # Cấu hình vùng lưới: căn giữa màn hình
        self.grid_area_size = 600
        self.font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 20, bold=False)
        self.font_title = pygame.font.SysFont("Segoe UI", 72, bold=True)
        self.font_header = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_star = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_lock = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_go_msg = pygame.font.SysFont("Segoe UI", 64, bold=True)
        self.font_go_sub = pygame.font.SysFont("Segoe UI", 32)

        # Kích thước khung lưới tuỳ thuộc vào Level
        self.cell_size = 0
        self.offset_x = 0
        self.offset_y = 0
        self.pipe_width = 0
        self.active_button = None      # nút đang được bấm
        self.active_until = 0          # thời gian sáng nút

        # NEW: Storage for menu and level select buttons
        self.btn_play = None
        self.btn_home = None
        self.level_btns = []

    def set_active_button(self, button_name):
        self.active_button = button_name
        self.active_until = pygame.time.get_ticks() + 180   # sáng 180ms

    def is_button_active(self, button_name):
        return self.active_button == button_name and pygame.time.get_ticks() < self.active_until

    def update_grid_params(self, grid_size):
        self.cell_size = self.grid_area_size // grid_size
        self.offset_x = (self.width - self.grid_area_size) // 2
        self.offset_y = 40
        self.pipe_width = self.cell_size // 3

    # =========================
    # VẼ NỀN GRADIENT
    # =========================
    def draw_gradient_background(self):
        for y in range(self.height):
            t = y / self.height
            r = int(self.BG_TOP[0] * (1 - t) + self.BG_BOTTOM[0] * t)
            g = int(self.BG_TOP[1] * (1 - t) + self.BG_BOTTOM[1] * t)
            b = int(self.BG_TOP[2] * (1 - t) + self.BG_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))

        # hiệu ứng glow nền nhẹ
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(glow, (0, 180, 255, 18), (self.width // 2, self.height // 2), 320)
        self.screen.blit(glow, (0, 0))

    # =========================
    # VẼ KHUNG + LƯỚI NEON
    # =========================
    def draw_grid_frame(self, logic):
        grid_rect = pygame.Rect(
            self.offset_x - 8,
            self.offset_y - 8,
            self.grid_area_size + 16,
            self.grid_area_size + 16
        )

        # --- Gradient dark border ---
        border_surf = pygame.Surface((grid_rect.width + 40, grid_rect.height + 40), pygame.SRCALPHA)
        for i in range(18, 0, -2):
            t = i / 18
            # Gradient: cyan -> blue -> purple -> black
            if t > 0.7:
                color = (0, int(180 * t), int(255 * t))
            elif t > 0.4:
                color = (40, int(80 * t), int(180 * t))
            else:
                color = (20, 20, 40)
            alpha = int(60 * t)
            pygame.draw.rect(
                border_surf,
                (*color, alpha),
                (20 - i, 20 - i, grid_rect.width + 2 * i, grid_rect.height + 2 * i),
                width=4,
                border_radius=28
            )
        self.screen.blit(border_surf, (grid_rect.x - 20, grid_rect.y - 20))

        # Nền khu vực lưới: gradient dọc xanh đậm -> tím than
        inner = pygame.Surface((self.grid_area_size, self.grid_area_size))
        for y in range(self.grid_area_size):
            t = y / self.grid_area_size
            r = int(18 * (1-t) + 60 * t)
            g = int(28 * (1-t) + 30 * t)
            b = int(38 * (1-t) + 80 * t)
            pygame.draw.line(inner, (r, g, b), (0, y), (self.grid_area_size, y))
        self.screen.blit(inner, (self.offset_x, self.offset_y))

        # Viền ngoài sáng nhẹ
        pygame.draw.rect(self.screen, (60, 120, 180), grid_rect, 3, border_radius=18)

        # Lưới pastel sáng
        grid_line_color = (180, 220, 255)
        for r in range(logic.size + 1):
            y = self.offset_y + r * self.cell_size
            pygame.draw.line(self.screen, grid_line_color, (self.offset_x, y), (self.offset_x + self.grid_area_size, y), 2)
        for c in range(logic.size + 1):
            x = self.offset_x + c * self.cell_size
            pygame.draw.line(self.screen, grid_line_color, (x, self.offset_y), (x, self.offset_y + self.grid_area_size), 2)

    def draw_glow_line(self, start, end, color, width=2):
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(10, 2, -2):
            alpha = max(8, 35 - i * 2)
            pygame.draw.line(glow, (*color, alpha), start, end, width + i)
        self.screen.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.line(self.screen, color, start, end, width)

    # =========================
    # HÀM DRAW CHÍNH
    # =========================
    def draw(self, logic, flow_visited, run_time, hints_left=3, suggestions=None):
        self.draw_gradient_background()
        self.update_grid_params(logic.size)
        self.draw_grid_frame(logic)
        mouse_pos = pygame.mouse.get_pos()
        hover_cell = self.get_grid_pos(mouse_pos, logic)

        # Vẽ từng ô + pipe
        for r in range(logic.size):
            for c in range(logic.size):
                cx = self.offset_x + c * self.cell_size
                cy = self.offset_y + r * self.cell_size
                rect = (cx, cy, self.cell_size, self.cell_size)

                # Hover ô khi rê chuột
                if hover_cell == (r, c):
                    self.draw_hover_cell(rect)

                # Start / End
                if (r, c) == logic.start_pos:
                    self.draw_cell_glow(rect, self.SOURCE_COLOR)
                if (r, c) == logic.end_pos:
                    self.draw_cell_glow(rect, self.SINK_COLOR)

                pipe_type = logic.grid_type[r][c]
                pipe_rot = logic.grid_rotation[r][c]

                if pipe_type != 0:
                    is_flow = (r, c) in flow_visited
                    # Draw suggestion glow if active
                    if isinstance(suggestions, dict) and (r, c) in suggestions:
                        self.draw_cell_glow(rect, (255, 255, 0)) # Yellow glow for hint

                    self.draw_pipe(pipe_type, pipe_rot, rect, logic, highlight=is_flow)

        self.draw_stats(logic, flow_visited, run_time)
        self.draw_buttons(hints_left)
        self.draw_home_button()
        pygame.display.flip()

    def draw_home_button(self):
        # Home button at top left
        self.btn_home = pygame.Rect(20, 20, 50, 50)
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.btn_home.collidepoint(mouse_pos)
        
        # Simple icon: house or "M"
        color = (0, 220, 255) if hovered else (180, 180, 180)
        pygame.draw.rect(self.screen, color, self.btn_home, 2, border_radius=8)
        
        # Draw a simple house shape
        x, y = self.btn_home.centerx, self.btn_home.centery
        pygame.draw.polygon(self.screen, color, [(x, y-12), (x-12, y), (x+12, y)])
        pygame.draw.rect(self.screen, color, (x-8, y, 16, 12), 2)

    def draw_stats(self, logic, flow_visited, run_time):
        """Vẽ thanh thông tin ở phía trên cùng với Time Bar và Rotation Limit"""
        current_level = logic.current_level
        rotations = logic.rotation_count
        max_rots = logic.max_rotations
        
        # --- HUD Area ---
        hud_w, hud_h = 500, 44
        hud_rect = pygame.Rect((self.width - hud_w) // 2, 8, hud_w, hud_h)
        hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (20, 35, 55, 180), (0, 0, hud_w, hud_h), border_radius=15)
        pygame.draw.rect(hud_surf, (0, 200, 255, 80), (0, 0, hud_w, hud_h), 2, border_radius=15)
        self.screen.blit(hud_surf, hud_rect.topleft)

        # --- Time Bar ---
        bar_w = 400
        bar_h = 8
        bar_x = (self.width - bar_w) // 2
        bar_y = hud_rect.bottom + 10
        
        # Background bar
        pygame.draw.rect(self.screen, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        
        # Foreground bar (remaining time)
        time_ratio = run_time / (logic.time_limit * 1000)
        time_ratio = max(0, min(1, time_ratio))
        
        color = (0, 255, 100) if time_ratio > 0.6 else (255, 200, 0) if time_ratio > 0.3 else (255, 50, 50)
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_w * time_ratio), bar_h), border_radius=4)

        # --- Draw Milestones and Stars ---
        t1 = 0.5 if current_level == 1 else 0.7
        t2 = 0.2 if current_level == 1 else 0.4
        
        milestones = [
            (t1, time_ratio >= t1), # Star 3
            (t2, time_ratio >= t2), # Star 2
            (0.02, time_ratio > 0)  # Star 1 (at the very left)
        ]
        
        for i, (t_val, is_active) in enumerate(milestones):
            mx = bar_x + int(bar_w * t_val)
            # Draw notch on the bar
            pygame.draw.line(self.screen, (255, 255, 255), (mx, bar_y - 2), (mx, bar_y + bar_h + 2), 2)
            
            # Draw tiny star above the notch
            sy = bar_y - 12
            sx = mx - 8
            star_color = (255, 215, 0) if is_active else (80, 80, 80)
            
            # Mini star polygon (scaled down from original)
            pygame.draw.polygon(self.screen, star_color, [
                (sx+8, sy-8), (sx+10, sy-3), (sx+16, sy-3), (sx+11, sy+1), 
                (sx+13, sy+7), (sx+8, sy+4), (sx+3, sy+7), (sx+5, sy+1), 
                (sx, sy-3), (sx+6, sy-3)
            ])

        # --- Stats Text ---
        font_stats = pygame.font.SysFont("Segoe UI", 18, bold=True)
        
        # Time string
        remaining_seconds = max(0, int(run_time // 1000))
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        time_str = f"{minutes:02}:{seconds:02}"
        
        # Rotations string
        rot_str = f"🔄 {rotations}/{max_rots}" if max_rots < 900 else f"🔄 {rotations}"
        
        # Lvl string
        lvl_str = f"Level {current_level}"
        
        texts = [lvl_str, rot_str, time_str]
        spacing = hud_w // 4
        
        for i, text in enumerate(texts):
            txt_surf = font_stats.render(text, True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(center=(hud_rect.left + (i + 1) * spacing, hud_rect.centery))
            self.screen.blit(txt_surf, txt_rect)

    def draw_cell_glow(self, rect, color):
        x, y, w, h = rect
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, 30), (0, 0, w, h), border_radius=12)
        self.screen.blit(surf, (x, y))
        pygame.draw.rect(self.screen, color, (x, y, w, h), 3, border_radius=10)

    def draw_hover_cell(self, rect):
        """Hiệu ứng sáng nhẹ khi rê chuột vào ô"""
        x, y, w, h = rect

        # lớp glow mờ bên trong ô
        hover_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(hover_surf, (0, 220, 255, 28), (0, 0, w, h), border_radius=10)
        self.screen.blit(hover_surf, (x, y))

        # viền sáng nhẹ
        pygame.draw.rect(self.screen, (80, 240, 255), (x, y, w, h), 2, border_radius=10)
    # =========================
    # VẼ ỐNG
    # =========================
    def draw_pipe(self, p_type, rot, rect, logic, highlight=False):
        x, y, w, h = rect
        cx = x + w // 2
        cy = y + h // 2
        pw = self.pipe_width

        # Xác định các nhánh nối từ tâm ra (giữ nguyên logic)
        arms = []
        if p_type == logic.PIPE_STRAIGHT:
            if rot == 0 or rot == 2:
                arms = [0, 2]
            else:
                arms = [1, 3]
        elif p_type == logic.PIPE_L_SHAPE:
            if rot == 0:
                arms = [0, 1]
            elif rot == 1:
                arms = [1, 2]
            elif rot == 2:
                arms = [2, 3]
            elif rot == 3:
                arms = [3, 0]
        elif p_type == logic.PIPE_T_SHAPE:
            if rot == 0:
                arms = [0, 1, 3]
            elif rot == 1:
                arms = [0, 1, 2]
            elif rot == 2:
                arms = [1, 2, 3]
            elif rot == 3:
                arms = [2, 3, 0]
        elif p_type == logic.PIPE_CROSS:
            arms = [0, 1, 2, 3]
        elif p_type == logic.PIPE_ONE_WAY:
            if rot == 0 or rot == 2:
                arms = [0, 2]
            else:
                arms = [1, 3]
        elif p_type == logic.PIPE_LOCKED:
            if rot == 0 or rot == 2:
                arms = [0, 2]
            else:
                arms = [1, 3]

        # 1) Bóng đổ pastel
        shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for arm in arms:
            self.draw_pastel_arm(shadow_surf, arm, w, h, pw, self.PIPE_SHADOW, offset=5, alpha=60)
        self.screen.blit(shadow_surf, (x, y))

        # 2) Thân ống gradient
        body_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if p_type == logic.PIPE_LOCKED:
            # Locked pipes have a darker, more industrial look
            locked_color = (100, 100, 110)
            for arm in arms:
                self.draw_pastel_arm(body_surf, arm, w, h, pw, locked_color, alpha=255)
        else:
            for arm in arms:
                self.draw_gradient_arm(body_surf, arm, w, h, pw)
        self.screen.blit(body_surf, (x, y))

        # 3) Viền ngoài pastel
        edge_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        edge_color = (255, 80, 80) if p_type == logic.PIPE_LOCKED else self.PIPE_EDGE
        for arm in arms:
            self.draw_pastel_arm(edge_surf, arm, w, h, pw, edge_color, offset=0, alpha=180, outline=True)
        pygame.draw.ellipse(edge_surf, edge_color, (w//2 - pw//2, h//2 - pw//2, pw, pw), 2)
        self.screen.blit(edge_surf, (x, y))

        # 4) Highlight bóng sáng
        if p_type != logic.PIPE_LOCKED:
            self.draw_pipe_gloss(x, y, w, h, pw, arms)

        # 5) Nước chảy neon (giữ nguyên)
        if highlight:
            self.draw_pipe_flow(x, y, w, h, pw, arms)

        # 6) Mũi tên nếu là ống 1 chiều hoặc Biểu tượng khóa
        if p_type == logic.PIPE_ONE_WAY:
            self.draw_arrow(cx, cy, pw, rot)
        elif p_type == logic.PIPE_LOCKED:
            # Draw a small lock icon
            lock_rect = pygame.Rect(cx - 6, cy - 6, 12, 12)
            pygame.draw.rect(self.screen, (255, 50, 50), lock_rect, border_radius=2)
            pygame.draw.circle(self.screen, (255, 50, 50), (cx, cy - 6), 5, width=2)

    def draw_gradient_arm(self, surf, arm, w, h, pw):
        # Vẽ nhánh ống với gradient xanh đậm mượt (theo hướng arm)
        grad_colors = [self.PIPE_BODY_GRAD1, self.PIPE_BODY_GRAD2, self.PIPE_BODY_GRAD3]
        if arm == 0:
            for i in range(h//2):
                t = i / (h//2)
                color = self._lerp_color(grad_colors[0], grad_colors[1], t)
                pygame.draw.rect(surf, color, (w//2 - pw//2, i, pw, 1), border_radius=6)
        elif arm == 1:
            for i in range(w//2, w):
                t = (i - w//2) / (w//2)
                color = self._lerp_color(grad_colors[1], grad_colors[2], t)
                pygame.draw.rect(surf, color, (i, h//2 - pw//2, 1, pw), border_radius=6)
        elif arm == 2:
            for i in range(h//2, h):
                t = (i - h//2) / (h//2)
                color = self._lerp_color(grad_colors[2], grad_colors[0], t)
                pygame.draw.rect(surf, color, (w//2 - pw//2, i, pw, 1), border_radius=6)
        elif arm == 3:
            for i in range(w//2):
                t = i / (w//2)
                color = self._lerp_color(grad_colors[0], grad_colors[2], t)
                pygame.draw.rect(surf, color, (i, h//2 - pw//2, 1, pw), border_radius=6)

    def draw_pastel_arm(self, surf, arm, w, h, pw, color, offset=0, alpha=120, outline=False):
        c = (*color, alpha)
        line_w = 2 if outline else 0
        if arm == 0:
            pygame.draw.rect(surf, c, (w//2 - pw//2 + offset, 0 + offset, pw, h//2), line_w, border_radius=12)
        elif arm == 1:
            pygame.draw.rect(surf, c, (w//2 + offset, h//2 - pw//2 + offset, w//2, pw), line_w, border_radius=12)
        elif arm == 2:
            pygame.draw.rect(surf, c, (w//2 - pw//2 + offset, h//2 + offset, pw, h//2), line_w, border_radius=12)
        elif arm == 3:
            pygame.draw.rect(surf, c, (0 + offset, h//2 - pw//2 + offset, w//2, pw), line_w, border_radius=12)

    def draw_pipe_gloss(self, x, y, w, h, pw, arms):
        """
        Giữ hiệu ứng sáng nhẹ trên thân ống,
        nhưng bỏ hoàn toàn đốm trắng tròn ở giữa.
        """
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        for arm in arms:
            if arm == 0:  # lên
                pygame.draw.rect(
                    surf,
                    (*self.PIPE_HIGHLIGHT, 22),
                    (w//2 - pw//3, 4, pw//5, h//2 - 8),
                    border_radius=8
                )
            elif arm == 1:  # phải
                pygame.draw.rect(
                    surf,
                    (*self.PIPE_HIGHLIGHT, 22),
                    (w//2 + 4, h//2 - pw//3, w//2 - 8, pw//5),
                    border_radius=8
                )
            elif arm == 2:  # xuống
                pygame.draw.rect(
                    surf,
                    (*self.PIPE_HIGHLIGHT, 14),
                    (w//2 - pw//3, h//2 + 4, pw//5, h//2 - 8),
                    border_radius=8
                )
            elif arm == 3:  # trái
                pygame.draw.rect(
                    surf,
                    (*self.PIPE_HIGHLIGHT, 22),
                    (4, h//2 - pw//3, w//2 - 8, pw//5),
                    border_radius=8
                )

        self.screen.blit(surf, (x, y))

    def _lerp_color(self, c1, c2, t):
        return (
            int(c1[0] * (1-t) + c2[0] * t),
            int(c1[1] * (1-t) + c2[1] * t),
            int(c1[2] * (1-t) + c2[2] * t)
        )

    def draw_arm(self, surf, arm, w, h, pw, color, offset=0, outline=False):
        line_w = 2 if outline else 0
        if arm == 0:
            pygame.draw.rect(surf, color, (w//2 - pw//2 + offset, 0 + offset, pw, h//2), line_w, border_radius=12)
        elif arm == 1:
            pygame.draw.rect(surf, color, (w//2 + offset, h//2 - pw//2 + offset, w//2, pw), line_w, border_radius=12)
        elif arm == 2:
            pygame.draw.rect(surf, color, (w//2 - pw//2 + offset, h//2 + offset, pw, h//2), line_w, border_radius=12)
        elif arm == 3:
            pygame.draw.rect(surf, color, (0 + offset, h//2 - pw//2 + offset, w//2, pw), line_w, border_radius=12)

    def draw_pipe_highlight(self, x, y, w, h, pw, arms):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        for arm in arms:
            if arm == 0:
                pygame.draw.rect(surf, self.PIPE_HIGHLIGHT + (55,), (w//2 - pw//3, 4, pw//4, h//2 - 4), border_radius=8)
            elif arm == 1:
                pygame.draw.rect(surf, self.PIPE_HIGHLIGHT + (55,), (w//2 + 4, h//2 - pw//3, w//2 - 4, pw//4), border_radius=8)
            elif arm == 2:
                pygame.draw.rect(surf, self.PIPE_HIGHLIGHT + (40,), (w//2 - pw//3, h//2 + 4, pw//4, h//2 - 4), border_radius=8)
            elif arm == 3:
                pygame.draw.rect(surf, self.PIPE_HIGHLIGHT + (55,), (4, h//2 - pw//3, w//2 - 4, pw//4), border_radius=8)

        pygame.draw.ellipse(surf, self.PIPE_HIGHLIGHT + (70,), (w//2 - pw//3, h//2 - pw//3, pw//1.5, pw//2.5))
        self.screen.blit(surf, (x, y))

    def draw_pipe_flow(self, x, y, w, h, pw, arms):
        flow_surf = pygame.Surface((w, h), pygame.SRCALPHA)

        for arm in arms:
            if arm == 0:
                pygame.draw.rect(flow_surf, self.FLOW_GLOW, (w//2 - pw//3, 0, int(pw * 0.66), h//2), border_radius=10)
                pygame.draw.rect(flow_surf, self.FLOW_COLOR, (w//2 - pw//5, 0, int(pw * 0.4), h//2), border_radius=8)
            elif arm == 1:
                pygame.draw.rect(flow_surf, self.FLOW_GLOW, (w//2, h//2 - pw//3, w//2, int(pw * 0.66)), border_radius=10)
                pygame.draw.rect(flow_surf, self.FLOW_COLOR, (w//2, h//2 - pw//5, w//2, int(pw * 0.4)), border_radius=8)
            elif arm == 2:
                pygame.draw.rect(flow_surf, self.FLOW_GLOW, (w//2 - pw//3, h//2, int(pw * 0.66), h//2), border_radius=10)
                pygame.draw.rect(flow_surf, self.FLOW_COLOR, (w//2 - pw//5, h//2, int(pw * 0.4), h//2), border_radius=8)
            elif arm == 3:
                pygame.draw.rect(flow_surf, self.FLOW_GLOW, (0, h//2 - pw//3, w//2, int(pw * 0.66)), border_radius=10)
                pygame.draw.rect(flow_surf, self.FLOW_COLOR, (0, h//2 - pw//5, w//2, int(pw * 0.4)), border_radius=8)

        pygame.draw.ellipse(flow_surf, self.FLOW_GLOW, (w//2 - pw//2, h//2 - pw//2, pw, pw))
        pygame.draw.ellipse(flow_surf, self.FLOW_COLOR, (w//2 - pw//4, h//2 - pw//4, pw//2, pw//2))
        self.screen.blit(flow_surf, (x, y))

    def draw_pipe_joints(self, x, y, w, h, pw, arms):
        """Vẽ các vòng nối kim loại như ảnh mẫu"""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        ring_color = (150, 160, 170)
        ring_edge = (220, 225, 230)

        joint_w = max(8, pw // 4)

        for arm in arms:
            if arm == 0:
                jy = h//4
                pygame.draw.rect(surf, ring_color, (w//2 - pw//2, jy - joint_w//2, pw, joint_w), border_radius=5)
                pygame.draw.rect(surf, ring_edge, (w//2 - pw//2, jy - joint_w//2, pw, joint_w), 1, border_radius=5)

            elif arm == 1:
                jx = w * 3 // 4
                pygame.draw.rect(surf, ring_color, (jx - joint_w//2, h//2 - pw//2, joint_w, pw), border_radius=5)
                pygame.draw.rect(surf, ring_edge, (jx - joint_w//2, h//2 - pw//2, joint_w, pw), 1, border_radius=5)

            elif arm == 2:
                jy = h * 3 // 4
                pygame.draw.rect(surf, ring_color, (w//2 - pw//2, jy - joint_w//2, pw, joint_w), border_radius=5)
                pygame.draw.rect(surf, ring_edge, (w//2 - pw//2, jy - joint_w//2, pw, joint_w), 1, border_radius=5)

            elif arm == 3:
                jx = w//4
                pygame.draw.rect(surf, ring_color, (jx - joint_w//2, h//2 - pw//2, joint_w, pw), border_radius=5)
                pygame.draw.rect(surf, ring_edge, (jx - joint_w//2, h//2 - pw//2, joint_w, pw), 1, border_radius=5)

        self.screen.blit(surf, (x, y))

    def draw_arrow(self, cx, cy, pw, rot):
        arrow_color = (255, 60, 60)
        sz = pw * 0.5

        pts = []
        if rot == 0:  # LÊN
            pts = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
        elif rot == 1:  # PHẢI
            pts = [(cx + sz, cy), (cx - sz, cy - sz), (cx - sz, cy + sz)]
        elif rot == 2:  # XUỐNG
            pts = [(cx, cy + sz), (cx - sz, cy - sz), (cx + sz, cy - sz)]
        elif rot == 3:  # TRÁI
            pts = [(cx - sz, cy), (cx + sz, cy - sz), (cx + sz, cy + sz)]

        pygame.draw.polygon(self.screen, arrow_color, pts)

    # =========================
    # BUTTONS
    # =========================
    def draw_buttons(self, hints_left=3):
        btn_w = 140
        btn_h = 52
        spacing = 28
        total_w = btn_w * 4 + spacing * 3
        start_x = (self.width - total_w) // 2
        y = self.offset_y + self.grid_area_size + 40

        # Tạo các nút
        self.btn_ai = pygame.Rect(start_x, y, btn_w, btn_h)
        self.btn_back = pygame.Rect(start_x + (btn_w + spacing), y, btn_w, btn_h)
        self.btn_next = pygame.Rect(start_x + (btn_w + spacing) * 2, y, btn_w, btn_h)
        self.btn_reset = pygame.Rect(start_x + (btn_w + spacing) * 3, y, btn_w, btn_h)

        mouse_pos = pygame.mouse.get_pos()

        btns = [self.btn_ai, self.btn_back, self.btn_next, self.btn_reset]
        btn_names = ["ai", "back", "next", "reset"]
        btn_labels = [f"Gợi ý ({hints_left})", "Back Lvl", "Next Lvl", "Reset"]

        # =========================
        # VẼ TỪNG NÚT
        # =========================
        for btn, name, label in zip(btns, btn_names, btn_labels):
            hovered = btn.collidepoint(mouse_pos)
            active = self.is_button_active(name)

            # --- Màu nút ---
            if active:
                grad_top = (80, 220, 255)      # sáng xanh mạnh khi bấm
                grad_bottom = (20, 150, 220)
                border_color = (0, 255, 255)
                glow_color = (0, 255, 255, 80)
            elif hovered:
                grad_top = self.BTN_GRAD_HOVER_TOP
                grad_bottom = self.BTN_GRAD_HOVER_BOTTOM
                border_color = (80, 220, 255)
                glow_color = (0, 220, 255, 45)
            else:
                grad_top = self.BTN_GRAD_TOP
                grad_bottom = self.BTN_GRAD_BOTTOM
                border_color = self.GRID_COLOR
                glow_color = (0, 180, 255, 25)

            # =========================
            # Glow phía sau nút
            # =========================
            glow = pygame.Surface((btn.width + 20, btn.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, glow_color, (10, 10, btn.width, btn.height), border_radius=20)
            self.screen.blit(glow, (btn.x - 10, btn.y - 10))

            # =========================
            # Bóng đổ nút
            # =========================
            shadow = btn.copy()
            shadow.x += 4
            shadow.y += 5
            shadow_surf = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (20, 25, 45, 130), (0, 0, btn.width, btn.height), border_radius=18)
            self.screen.blit(shadow_surf, shadow.topleft)

            # =========================
            # Gradient nền nút bo tròn
            # =========================
            grad_surf = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            for yb in range(btn.height):
                t = yb / btn.height
                color = self._lerp_color(grad_top, grad_bottom, t)
                pygame.draw.line(grad_surf, color, (0, yb), (btn.width, yb))

            # Mask bo góc
            mask = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, btn.width, btn.height), border_radius=18)
            grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.screen.blit(grad_surf, btn.topleft)

            # =========================
            # Highlight trên nút (bóng kính)
            # =========================
            gloss = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            pygame.draw.ellipse(gloss, (255, 255, 255, 35), (10, 4, btn.width - 20, btn.height // 2))
            self.screen.blit(gloss, btn.topleft)

            # =========================
            # Viền nút
            # =========================
            pygame.draw.rect(self.screen, border_color, btn, 2, border_radius=18)

            # =========================
            # CHỮ TRONG NÚT
            # =========================
            txt_color = (255, 245, 120) if name == "ai" else self.BTN_TEXT
            txt = self.font.render(label, True, txt_color)

            # Căn giữa chuẩn tuyệt đối
            text_rect = txt.get_rect(center=(btn.x + btn.width // 2, btn.y + btn.height // 2))
            self.screen.blit(txt, text_rect)

    # =========================
    # CLICK GRID
    # =========================
    def get_grid_pos(self, mouse_pos, logic):
        mx, my = mouse_pos
        if self.offset_x <= mx <= self.offset_x + self.grid_area_size and \
           self.offset_y <= my <= self.offset_y + self.grid_area_size:
            c = (mx - self.offset_x) // self.cell_size
            r = (my - self.offset_y) // self.cell_size
            if 0 <= r < logic.size and 0 <= c < logic.size:
                return r, c
            return None

    # =========================
    # MENU & LEVEL SELECT
    # =========================
    def draw_menu(self):
        self.draw_gradient_background()
        
        # Title
        title_surf = self.font_title.render("PIPE PUZZLE", True, (0, 220, 255))
        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 3))
        
        # Drawing a glow behind the title
        glow_surf = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (0, 180, 255, 40), (0, 0, title_rect.width + 40, title_rect.height + 40))
        self.screen.blit(glow_surf, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title_surf, title_rect)
        
        # Play Button
        btn_w, btn_h = 240, 80
        self.btn_play = pygame.Rect((self.width - btn_w) // 2, self.height // 2 + 50, btn_w, btn_h)
        
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.btn_play.collidepoint(mouse_pos)
        
        # Draw Play Button
        color = self.BTN_GRAD_HOVER_TOP if hovered else self.BTN_GRAD_TOP
        pygame.draw.rect(self.screen, color, self.btn_play, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), self.btn_play, 3, border_radius=20)
        
        play_txt = self.font.render("PLAY", True, (255, 255, 255))
        txt_rect = play_txt.get_rect(center=self.btn_play.center)
        self.screen.blit(play_txt, txt_rect)
        
        pygame.display.flip()

    def draw_level_select(self, max_level_count=9, unlocked_up_to=1, level_stars=None, total_stars=0):
        if level_stars is None: level_stars = {}
        self.draw_gradient_background()
        
        # Header with Total Stars
        title_surf = self.font_header.render("SELECT LEVEL", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width // 2, 70))
        self.screen.blit(title_surf, title_rect)
        
        total_stars_txt = self.font_star.render(f"⭐ Total Stars: {total_stars}", True, (255, 215, 0))
        self.screen.blit(total_stars_txt, (self.width - 200, 30))

        self.level_btns = []
        btn_size = 110
        padding = 40
        start_x = (self.width - (btn_size * 3 + padding * 2)) // 2
        start_y = 150
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i in range(1, max_level_count + 1):
            row = (i - 1) // 3
            col = (i - 1) % 3
            
            x = start_x + col * (btn_size + padding)
            y = start_y + row * (btn_size + padding + 30) # extra space for stars
            rect = pygame.Rect(x, y, btn_size, btn_size)
            self.level_btns.append((rect, i))
            
            is_unlocked = i <= unlocked_up_to
            hovered = rect.collidepoint(mouse_pos) and is_unlocked
            
            # --- Draw Button ---
            if is_unlocked:
                color = (0, 220, 255) if hovered else (0, 100, 255)
                pygame.draw.rect(self.screen, color, rect, border_radius=20)
                lvl_txt = self.font.render(str(i), True, (255, 255, 255))
                
                # Draw Stars for level
                stars = level_stars.get(i, 0)
                self.draw_stars_at(rect.centerx, rect.bottom + 20, stars)
            else:
                pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=20)
                # Req stars info
                req_stars = 0
                if i >= 4: req_stars = 6
                if i >= 7: req_stars = 12
                
                lvl_txt = self.font_lock.render(f"LOCKED", True, (150, 150, 150))
                req_txt = self.font_lock.render(f"needs {req_stars} ⭐", True, (255, 100, 100))
                self.screen.blit(req_txt, req_txt.get_rect(center=(rect.centerx, rect.centery + 20)))

            txt_rect = lvl_txt.get_rect(center=rect.center if is_unlocked else (rect.centerx, rect.centery - 10))
            self.screen.blit(lvl_txt, txt_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=20)

        # Back icon
        self.btn_back_to_menu = pygame.Rect(30, 30, 120, 40)
        hovered_back = self.btn_back_to_menu.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, (60, 60, 90) if not hovered_back else (100, 100, 150), self.btn_back_to_menu, border_radius=10)
        back_txt = self.font_small.render("MENU", True, (255, 255, 255))
        self.screen.blit(back_txt, back_txt.get_rect(center=self.btn_back_to_menu.center))

        pygame.display.flip()

    def draw_stars_at(self, cx, cy, count):
        star_w = 24
        spacing = 6
        total_w = (star_w * 3) + (spacing * 2)
        start_x = cx - total_w // 2
        for i in range(3):
            color = (255, 215, 0) if i < count else (60, 60, 60)
            x = start_x + i * (star_w + spacing)
            # Simple star shape (diamond/polygon)
            pygame.draw.polygon(self.screen, color, [
                (x+12, cy-12), (x+15, cy-4), (x+24, cy-4), (x+17, cy+2), 
                (x+20, cy+11), (x+12, cy+6), (x+4, cy+11), (x+7, cy+2), 
                (x, cy-4), (x+9, cy-4)
            ])

    def draw_game_over(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))
        
        txt = self.font_go_msg.render("GAME OVER", True, (255, 50, 50))
        rect = txt.get_rect(center=(self.width//2, self.height//2 - 50))
        self.screen.blit(txt, rect)
        
        sub_txt = self.font_go_sub.render("Click Reset to try again", True, (255, 255, 255))
        sub_rect = sub_txt.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(sub_txt, sub_rect)
        
        pygame.display.flip()