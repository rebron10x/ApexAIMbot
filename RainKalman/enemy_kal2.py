from filterpy.kalman import KalmanFilter
import numpy as np

class EnemyTracker:
    def __init__(self, bullet_speed, time_step):
        self.bullet_speed = bullet_speed
        self.time_step = time_step

        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        self.kf.x = np.array([[0.], [0.]])  # 初始状态 (x, dx)

        # 根据子弹飞行时间计算状态转移矩阵 F
        self.kf.F = np.array([[1., time_step], [0., 1.]])  

        self.kf.H = np.array([[1., 0.]])  # 测量矩阵
        self.kf.P *= 600.  # 初始协方差矩阵
        self.kf.R = 10  # 测量噪声的方差

    def predict_enemy_position(self, current_enemy_pos):
        # 预测下一时刻的状态
        self.kf.predict()

        # 更新测量值并加入提前量
        if current_enemy_pos[0] > 0:
            z = current_enemy_pos[0] + self.bullet_speed * self.time_step
            self.kf.update(z)
        if current_enemy_pos[0] < 0:
            z = current_enemy_pos[0] - self.bullet_speed * self.time_step
            self.kf.update(z)

        # 返回预测位置
        return self.kf.x[0]