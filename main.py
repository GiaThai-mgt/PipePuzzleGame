import pygame
from game_logic import PipeGameLogic
from graphics import PipeGameGraphics
from ai_solver import PipeGameAI

def main():
    logic = PipeGameLogic()
    gui = PipeGameGraphics(w=800, h=800)
    ai = PipeGameAI(logic)
    
    # Game States
    STATE_MENU = 0
    STATE_LEVEL_SELECT = 1
    STATE_GAME = 2
    current_state = STATE_MENU
    
    level_stars = {i: 0 for i in range(1, 10)}
    total_stars = 0
    unlocked_up_to = 1

    running = True
    clock = pygame.time.Clock()
    
    # Time tracking variables
    game_over = False
    penalty_ms = 0
    hints_left = 3
    start_ticks = pygame.time.get_ticks()
    remaining_ms = 0
    
    is_win, visited = False, set()
    first_hint_shown = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        total_stars = sum(level_stars.values())
        
        # Unlock logic
        unlocked_up_to = 3 # Levels 1-3 always available
        if total_stars >= 6: unlocked_up_to = 6
        if total_stars >= 12: unlocked_up_to = 9
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # --- MENU STATE ---
                    if current_state == STATE_MENU:
                        if gui.btn_play and gui.btn_play.collidepoint(mouse_pos):
                            current_state = STATE_LEVEL_SELECT
                            continue
                            
                    # --- LEVEL SELECT STATE ---
                    elif current_state == STATE_LEVEL_SELECT:
                        if hasattr(gui, 'btn_back_to_menu') and gui.btn_back_to_menu.collidepoint(mouse_pos):
                            current_state = STATE_MENU
                            continue

                        for rect, lvl_num in gui.level_btns:
                            if rect.collidepoint(mouse_pos) and lvl_num <= unlocked_up_to:
                                logic.load_level(lvl_num)
                                is_win, visited = logic.check_flow()
                                start_ticks = pygame.time.get_ticks()
                                penalty_ms = 0
                                hints_left = 3 if logic.current_level < 6 else 0 # L6+ no manual hints
                                game_over = False
                                first_hint_shown = False
                                current_state = STATE_GAME
                                break
                        continue

                    # --- GAME STATE ---
                    elif current_state == STATE_GAME:
                        if gui.btn_home and gui.btn_home.collidepoint(mouse_pos):
                            current_state = STATE_LEVEL_SELECT
                            continue

                        # 1. UI Buttons
                        if gui.btn_back.collidepoint(mouse_pos):
                            prev_lvl = logic.current_level - 1 if logic.current_level > 1 else logic.max_level
                            if prev_lvl <= unlocked_up_to:
                                logic.load_level(prev_lvl)
                                is_win, visited = logic.check_flow()
                                start_ticks = pygame.time.get_ticks()
                                penalty_ms = 0
                                hints_left = 3 if logic.current_level < 6 else 0
                                game_over = False
                                current_state = STATE_GAME
                            continue

                        if gui.btn_next.collidepoint(mouse_pos):
                            next_lvl = (logic.current_level % logic.max_level) + 1
                            if next_lvl <= unlocked_up_to:
                                logic.load_level(next_lvl)
                                is_win, visited = logic.check_flow()
                                start_ticks = pygame.time.get_ticks()
                                penalty_ms = 0
                                hints_left = 3 if logic.current_level < 6 else 0
                                game_over = False
                                current_state = STATE_GAME
                            continue
                            
                        if gui.btn_reset.collidepoint(mouse_pos):
                            logic.load_level(logic.current_level)
                            is_win, visited = logic.check_flow()
                            start_ticks = pygame.time.get_ticks()
                            penalty_ms = 0
                            hints_left = 3 if logic.current_level < 6 else 0
                            game_over = False
                            continue
                            
                        if gui.btn_ai.collidepoint(mouse_pos):
                            if hints_left > 0 and not game_over and not is_win:
                                solution = ai.solve()
                                if solution:
                                    to_rotate = [((r, c), rot) for (r, c), rot in solution.items() if logic.grid_rotation[r][c] != rot]
                                    if to_rotate:
                                        import random
                                        (r, c), correct_rot = random.choice(to_rotate)
                                        logic.grid_rotation[r][c] = correct_rot
                                        penalty_ms += 10000
                                        hints_left -= 1
                                        is_win, visited = logic.check_flow()
                            continue
                        
                        # 2. Grid Interactors
                        if not is_win and not game_over:
                            grid_pos = gui.get_grid_pos(mouse_pos, logic)
                            if grid_pos:
                                r, c = grid_pos
                                logic.rotate_pipe(r, c)
                                is_win, visited = logic.check_flow()

        # --- Rendering Logic Based on State ---
        if current_state == STATE_MENU:
            gui.draw_menu()
        elif current_state == STATE_LEVEL_SELECT:
            gui.draw_level_select(max_level_count=logic.max_level, unlocked_up_to=unlocked_up_to, level_stars=level_stars, total_stars=total_stars)
        elif current_state == STATE_GAME:
            passed_ms = pygame.time.get_ticks() - start_ticks
            remaining_ms = (logic.time_limit * 1000) - passed_ms - penalty_ms
            if remaining_ms <= 0:
                remaining_ms = 0
                game_over = True
            
            # Special Rule: L1 First Pipe Hint
            if logic.current_level == 1 and not is_win and not game_over and not first_hint_shown:
                solution = ai.solve()
                if solution:
                    sr, sc = logic.start_pos
                    if (sr, sc) in solution and logic.grid_rotation[sr][sc] != solution[(sr, sc)]:
                        logic.grid_rotation[sr][sc] = solution[(sr, sc)]
                        first_hint_shown = True

            # Special Rule: L3 Start Hint (Auto-hint for 5 seconds)
            l3_hint_active = logic.current_level == 3 and passed_ms < 5000
            current_suggestions = None
            if l3_hint_active:
                if not hasattr(logic, 'l3_cached_solution'):
                    logic.l3_cached_solution = ai.solve()
                current_suggestions = logic.l3_cached_solution

            # Show hint glow for manual hints too
            # (If hints_left changed, we can show a hint briefly, but let's keep it simple)

            gui.draw(logic, visited, remaining_ms, hints_left, suggestions=current_suggestions)
            
            if game_over:
                gui.draw_game_over()
            
            if is_win:
                # Star Calculation
                time_ratio = remaining_ms / (logic.time_limit * 1000)
                stars = 1
                if logic.current_level == 1:
                    if time_ratio >= 0.5: stars = 3
                    elif time_ratio >= 0.2: stars = 2
                else:
                    if time_ratio >= 0.7: stars = 3
                    elif time_ratio >= 0.4: stars = 2
                
                # Cap stars if max rotations reached
                if logic.current_level >= 7 and logic.rotation_count >= logic.max_rotations - 2:
                    stars = min(stars, 2)

                if stars > level_stars[logic.current_level]:
                    level_stars[logic.current_level] = stars

                win_txt = gui.font.render(f"WINNER! +{stars} ⭐", True, (255, 215, 0))
                gui.screen.blit(win_txt, (gui.width//2 - 80, gui.offset_y - 40))
                pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
