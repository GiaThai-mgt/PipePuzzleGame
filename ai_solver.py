class AISolver:
    def __init__(self, matrix):
        self.matrix = matrix  # Ma trận các ống nước từ game_logic

    def solve(self):
        """
        Hàm chính để giải đố. 
        Trả về danh sách các bước xoay (x, y, số lần xoay).
        """
        print("AI đang tính toán đường đi tối ưu...")
        
        # Ví dụ: Giả sử AI thấy ô (1, 2) cần xoay 1 
        solutions = [(1, 2, 1)] 
        return solutions

    def heuristic(self, current_pos, goal_pos):
        """
        Hàm lượng giá cho thuật toán A* (Tính khoảng cách Manhattan)
        """
        return abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])