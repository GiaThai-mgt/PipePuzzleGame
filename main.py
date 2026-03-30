import pygame
from game_logic import PipeGameLogic
from graphics import PipeGameGraphics
from ai_solver import PipeGameAI

def main():
    logic = PipeGameLogic()
    gui = PipeGameGraphics(w=800, h=800)
    ai = PipeGameAI(logic)
    
    running = True
    clock = pygame.time.Clock()
    
    # Calculate initial flow
    is_win, visited = logic.check_flow()

    # Lưu trữ bề mặt văn bản thắng và vị trí của nó
    # Stores the win text surface and its position
    win_text_surface = None
    win_text_rect = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 1. UI Buttons
                    if gui.btn_next.collidepoint(mouse_pos):
                        next_lvl = (logic.current_level % logic.max_level) + 1
                        logic.load_level(next_lvl)
                        is_win, visited = logic.check_flow()
                        # Đặt lại bề mặt văn bản thắng khi tải cấp độ mới
                        # Reset win text surface when a new level is loaded
                        win_text_surface = None
                        continue
                        
                    if gui.btn_reset.collidepoint(mouse_pos):
                        logic.load_level(logic.current_level)
                        is_win, visited = logic.check_flow()
                        # Đặt lại bề mặt văn bản thắng khi đặt lại cấp độ
                        # Reset win text surface when resetting the level
                        win_text_surface = None
                        continue
                        
                    if gui.btn_ai.collidepoint(mouse_pos):
                        solution = ai.solve()
                        if solution:
                            for (r, c), rot in solution.items():
                                logic.grid_rotation[r][c] = rot
                            is_win, visited = logic.check_flow()
                            # Đặt lại bề mặt văn bản thắng khi AI tìm thấy giải pháp
                            # Reset win text surface when AI finds a solution
                            win_text_surface = None
                        else:
                            print("Không tìm được đường đi")
                        continue
                    
                    # 2. Grid Interactors
                    if not is_win:
                        grid_pos = gui.get_grid_pos(mouse_pos, logic)
                        if grid_pos:
                            r, c = grid_pos
                            logic.rotate_pipe(r, c)
                            is_win, visited = logic.check_flow()
                            # Đặt lại bề mặt văn bản thắng khi xoay ống
                            # Reset win text surface when rotating a pipe
                            win_text_surface = None
                            if is_win:
                                print(f"Level {logic.current_level} Thắng!")

        # Rendering
        gui.draw(logic, visited)
        
        # Win prompt
        # Hiển thị thông báo thắng nếu game đã thắng
        # Displays win message if the game is won
        if is_win:
            if win_text_surface is None:
                win_text_surface = gui.font.render("WINNER! GO NEXT LEVEL", True, (0, 255, 0))
                win_text_rect = win_text_surface.get_rect(center=(gui.width//2, gui.offset_y - 40))
            gui.screen.blit(win_text_surface, win_text_rect)
            pygame.display.flip()
        else:
            # Đặt lại bề mặt văn bản thắng nếu trò chơi không còn ở trạng thái thắng
            # Resets win text surface if the game is no longer in a win state
            win_text_surface = None
            
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
