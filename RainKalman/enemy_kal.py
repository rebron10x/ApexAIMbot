from filterpy.kalman import KalmanFilter
import numpy as np

class EnemyTracker:
    def __init__(self):
        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        self.kf.x = np.array([[0.], [0.]])  # 初始状态 (x, dx)
        self.kf.F = np.array([[1., 1.], [0., 1.]])  # 状态转移矩阵
        self.kf.H = np.array([[1., 0.]])  # 测量矩阵
        self.kf.P *= 1000.  # 初始协方差矩阵
        self.kf.R = 8  # 测量噪声的方差

    def predict_enemy_position(self, current_enemy_pos):
        # 预测下一时刻的状态
        self.kf.predict()

        # 更新测量值
        z = current_enemy_pos[0]
        self.kf.update(z)

        # 返回预测位置
        return self.kf.x[0]

