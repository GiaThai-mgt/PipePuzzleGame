import heapq

class PipeGameAI:
    def __init__(self, game):
        # Lưu đối tượng PipeGameLogic chứa dữ liệu lưới và luật chơi
        self.game = game

    def heuristic(self, r, c):
        # Hàm heuristic sử dụng khoảng cách Manhattan tới điểm đích
        end_r, end_c = self.game.end_pos
        return abs(r - end_r) + abs(c - end_c)

    def solve(self):
        """
        Thuật toán A* tìm đường nối thông lưới.
        Trả về một Dictionary dạng dict[(r, c)] = số_lần_xoay (0 đến 3) nếu tìm thấy, 
        hoặc None nếu vô nghiệm.
        """
        start_r, start_c = self.game.start_pos
        end_r, end_c = self.game.end_pos
        
        # Lấy hướng nguồn nước ban đầu tại start_pos
        initial_entry_direction = self.game.DIRECTION_MAP.get(self.game.source_direction)
        if initial_entry_direction is None:
            return None
            
        # Trạng thái A* quy định: (hàng, cột, hướng_nước_vừa_chảy_vào_ô_này)
        start_state = (start_r, start_c, initial_entry_direction)
        
        # Hàng đợi ưu tiên (Priority Queue) của thuật toán A* -> lưu tuples: (f_score, g_score, state)
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start_r, start_c), 0, start_state))
        
        # came_from dùng để truy vết quá trình đi và lưu lại "góc quay" ta đã dùng để đến ô này
        # Định dạng: came_from[state_hiện_tại] = (state_trước_đó, góc_quay_của_ô_trước_đó)
        came_from = {}
        
        # g_score lưu chi phí (số lượng ống đã nối nối) từ Start
        g_score = {start_state: 0}
        
        while open_set:
            f, g, current_state = heapq.heappop(open_set)
            r, c, entry_dir = current_state
            
            # --- ĐIỀU KIỆN ĐẾN ĐÍCH NẰM TẠI ĐÂY ---
            if (r, c) == (end_r, end_c):
                # Nước đã chạm tới đích, cần tìm 1 góc quay hợp lệ cho đích để đón được nước này
                end_pipe_type = self.game.grid_type[r][c]
                valid_end_rot = -1
                for rot in range(4):
                    if entry_dir in self.game.PIPE_CONNECTIONS[end_pipe_type][rot]:
                        valid_end_rot = rot
                        break
                
                # Nước nối thông thành công, tiến hành khôi phục kết quả!
                if valid_end_rot != -1:
                    return self.reconstruct_path(came_from, current_state, valid_end_rot)
            
            # --- XÚC TIẾN CHẠY CÁC LÁNG GIỀNG ---
            current_pipe_type = self.game.grid_type[r][c]
            
            # Thử qua cả 4 kiểu xoay cho ống tại vị trí (r, c)
            for rot in range(4):
                openings = self.game.PIPE_CONNECTIONS[current_pipe_type][rot]
                
                # Nếu góc quay rot này KHÔNG LÀM RA CỬA ĐÓN NƯỚC, bỏ qua
                if entry_dir not in openings:
                    continue
                    
                # Ống đã nhận nước, nó sẽ tủa ra ở các cửa còn lại của góc quay này
                for outgoing_dir in openings:
                    # Tránh nước chảy ngược lại hướng nó vừa bơi vào
                    if outgoing_dir == entry_dir:
                        continue
                        
                    # Tính toán đường đi vào lưới kế tiếp
                    dr, dc = 0, 0
                    if outgoing_dir == self.game.TOP: 
                        dr = -1
                        next_entry_dir = self.game.BOTTOM  # Ra cổng trên thì sẽ tiến vào cổng dưới của ô phía trên
                    elif outgoing_dir == self.game.BOTTOM: 
                        dr = 1
                        next_entry_dir = self.game.TOP
                    elif outgoing_dir == self.game.LEFT: 
                        dc = -1
                        next_entry_dir = self.game.RIGHT
                    elif outgoing_dir == self.game.RIGHT: 
                        dc = 1
                        next_entry_dir = self.game.LEFT
                    
                    nr, nc = r + dr, c + dc
                    
                    # Cản lại nếu ô kế tiếp đi ra khỏi map hoặc là ô trống (loại 0)
                    if not (0 <= nr < self.game.size and 0 <= nc < self.game.size):
                        continue
                    if self.game.grid_type[nr][nc] == 0:
                        continue
                        
                    next_state = (nr, nc, next_entry_dir)
                    tentative_g_score = g + 1
                    
                    # Nếu khám phá ra lộ trình này tối ưu hơn, cập nhật chi phí
                    if next_state not in g_score or tentative_g_score < g_score[next_state]:
                        came_from[next_state] = (current_state, rot)
                        g_score[next_state] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(nr, nc)
                        heapq.heappush(open_set, (f_score, tentative_g_score, next_state))
                        
        return None  # Không có con đường nào đáp ứng

    def reconstruct_path(self, came_from, current_state, end_rot):
        # Tập hợp và trả về cấu hình xoay dành riêng cho phần đường ống mới tìm được
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
        """Tiến hành giải và thiết lập sự xoay chiều lên lưới thực."""
        print(f"\n[AI] Đang tìm kiếm giải pháp cho Màn {self.game.current_level}...")
        solution = self.solve()
        
        if solution:
            print("[AI] ĐÃ TÌM THẤY ĐƯỜNG ĐI! Tự động xoay ống...")
            for (r, c), rot in solution.items():
                self.game.grid_rotation[r][c] = rot
                print(f"  - Ô ({r}, {c}) \t=> Xoay đến góc: {rot}")
            
            # Tự động thẩm định lại bằng chính hàm verify check_win() của bạn
            if self.game.check_win():
                print("[AI] Nước đã thông mạch và chiến thắng! 🎉")
                return True
            else:
                print("[AI] (Lỗi) Tìm thấy đường nhưng check_win() không chấp nhận!")
                return False
        else:
            print("[AI] Bó tay, Màn này vô nghiệm cho hướng nguồn hiện tại.")
            return False
