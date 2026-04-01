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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 1. UI Buttons
                    if gui.btn_back.collidepoint(mouse_pos):
                        prev_lvl = logic.current_level - 1 if logic.current_level > 1 else logic.max_level
                        logic.load_level(prev_lvl)
                        is_win, visited = logic.check_flow()
                        gui.set_active_button("back")
                        continue

                    if gui.btn_next.collidepoint(mouse_pos):
                        next_lvl = (logic.current_level % logic.max_level) + 1
                        logic.load_level(next_lvl)
                        is_win, visited = logic.check_flow()
                        gui.set_active_button("next")
                        continue
                        
                    if gui.btn_reset.collidepoint(mouse_pos):
                        logic.load_level(logic.current_level)
                        is_win, visited = logic.check_flow()
                        gui.set_active_button("reset")
                        continue
                        
                    if gui.btn_ai.collidepoint(mouse_pos):
                        solution = ai.solve()
                        if solution:
                            for (r, c), rot in solution.items():
                                logic.grid_rotation[r][c] = rot
                            is_win, visited = logic.check_flow()
                        else:
                            print("Không tìm được đường đi")
                        gui.set_active_button("ai")
                        continue
                    
                    # 2. Grid Interactors
                    if not is_win:
                        grid_pos = gui.get_grid_pos(mouse_pos)
                        if grid_pos:
                            r, c = grid_pos
                            logic.rotate_pipe(r, c)
                            is_win, visited = logic.check_flow()
                            if is_win:
                                print(f"Level {logic.current_level} Thắng!")

        # Rendering
        gui.draw(logic, visited)
        
        # Win prompt
        if is_win:
            win_txt = gui.font.render("WINNER! GO NEXT LEVEL", True, (0, 255, 0))
            gui.screen.blit(win_txt, (gui.width//2 - 130, gui.offset_y - 40))
            pygame.display.flip()
            
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
