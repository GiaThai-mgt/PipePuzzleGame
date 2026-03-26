class PipeGameLogic:
    def __init__(self, size=5):
        self.size = size
        # Ma trận lưu hướng của ống (0, 1, 2, 3 tương ứng 0, 90, 180, 270 độ)
        self.grid_rotation = [[0 for _ in range(size)] for _ in range(size)]
        
        # Ma trận lưu loại ống (Thái tự quy định loại ống ở đây)
        self.grid_type = [[1 for _ in range(size)] for _ in range(size)] 
        
        self.start_pos = (0, 0)
        self.end_pos = (size-1, size-1)
        self.source_direction = "TOP" # Cho màn 3 của Thái đây

    def rotate_pipe(self, r, c):
        """Xoay ống tại vị trí r, c thêm 90 độ"""
        self.grid_rotation[r][c] = (self.grid_rotation[r][c] + 1) % 4
        print(f"Ô ({r},{c}) hiện đang ở hướng: {self.grid_rotation[r][c]}")

    def check_win(self):
        """
        Thái sẽ viết thuật toán DFS ở đây để kiểm tra thông mạch.
        Nếu nước chảy tới được self.end_pos thì return True.
        """
        # Tạm thời trả về False để game chạy không lỗi
        return False