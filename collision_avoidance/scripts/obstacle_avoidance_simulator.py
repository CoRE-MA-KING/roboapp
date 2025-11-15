import itertools
import numpy as np
import math
import sys
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MplPolygon
from matplotlib.animation import FuncAnimation
import time

# ----- パラメータ -----
# シミュレーション設定
ROBOT_RADIUS = 0.5    # ロボットの半径[m]
MAX_SPEED = 2.0      # 最大速度[m/s]
DT = 0.02            # シミュレーションの時間ステップ[s]（50Hz）
REPULSIVE_GAIN = 0.7 # 斥力ゲイン
INFLUENCE_RANGE = 0.2 # 影響範囲[m]
K_CMD = 8.0          # コマンド速度に対する追従ゲイン (F_cmd = K_CMD * (v_cmd - v))

# LIDAR設定
LIDAR_RATE = 15   # LIDARスキャン周波数[Hz]
LIDAR_DT = 1.0 / LIDAR_RATE  # LIDARスキャン間隔[s]

# ----- LIDAR & 障害物 -----
class LidarSimulator:
    def __init__(self, num_beams=90, max_range=5.0, noise_std=0.01):
        self.num_beams = num_beams
        self.max_range = max_range
        self.noise_std = noise_std
        self.angles = np.linspace(0, 2*np.pi, num_beams, endpoint=False)
        
        # 逐次更新用の状態管理
        self.current_angle_idx = 0  # 現在のスキャン位置
        self.last_update_time = 0.0  # 最後の更新時刻
        self.scan_points = []        # 1周分の点群データ（グローバル座標）
        self.points_age = []        # 各点の経過時間
        
        # グローバル/ローカル座標でのキャッシュ
        self.last_scan_points_local = None
        self.last_scan_points_global = None

        # 1周あたりのビーム数から1ステップあたりのビーム数を計算
        # 1秒間にLIDAR_RATE周するので、DTあたりのビーム数は以下のように計算
        self.beams_per_step = max(1, int(np.ceil(self.num_beams * LIDAR_RATE * DT)))

        # ビーム単位ベクトル（ローカル座標）を事前計算して trig を削減
        cos_vals = np.cos(self.angles)
        sin_vals = np.sin(self.angles)
        # store as Nx2 float array for fast indexed access
        self.beam_unit_vectors = np.column_stack((cos_vals, sin_vals))
        # scheduling based on wall-clock to keep LIDAR rate stable even if frame rate fluctuates
        self.beams_per_second = float(self.num_beams) * float(LIDAR_RATE)
        self.last_update_wall = time.perf_counter()

    def transform_to_global(self, local_points, robot_pos, robot_heading):
        """ロボット座標系の点群をグローバル座標系に変換"""
        if local_points is None or len(local_points) == 0:
            return None
        c, s = np.cos(robot_heading), np.sin(robot_heading)
        R = np.array([[c, -s], [s, c]])
        global_points = np.dot(local_points, R.T) + robot_pos
        return global_points

    def transform_to_local(self, global_points, robot_pos, robot_heading):
        """グローバル座標系の点群をロボット座標系に変換"""
        if global_points is None or len(global_points) == 0:
            return None
        translated = global_points - robot_pos
        c, s = np.cos(-robot_heading), np.sin(-robot_heading)
        R_inv = np.array([[c, -s], [s, c]])
        local_points = np.dot(translated, R_inv.T)
        return local_points


    def get_scan(self, robot_pos, robot_vel, robot_cmd_vel, robot_heading, obstacles, current_time):
        """
        LIDARスキャンを実行し、ロボット座標系とグローバル座標系の点群を更新する。
        
        シミュレーションの時間ステップ(DT)ごとに数点のビームを更新し、
        1周分のデータが揃うまで古いデータを保持する。各点は取得時の実際の
        ロボット姿勢で計測される。
        """
        # Decide how many beams to process based on simulation time progression
        # (use current_time passed in by the simulator) so LIDAR updates are
        # deterministic with respect to sim time rather than wall-clock.
        elapsed_sim = current_time - self.last_update_time if self.last_update_time is not None else 0.0
        # update ages by the simulation time passed
        self.points_age = [(age + elapsed_sim) for age in self.points_age]
        # how many beams should have been emitted during elapsed_sim
        beams_to_emit = int(self.beams_per_second * elapsed_sim)
        if beams_to_emit <= 0:
            # advance sim-time baseline and nothing else to do
            self.last_update_time = current_time
            return self.last_scan_points_global
        
        # 最新からnum_beamsより古いデータは1周期以上経過したと判断する
        while len(self.points_age) > self.num_beams:
            self.points_age.pop(0)
            self.scan_points.pop(0)
            
        # このステップで取得する新しいビームを処理（最小限のPythonオーバーヘッド）
        # cap beams to reasonable amount to avoid huge backlogs
        beams = min(beams_to_emit, max(1, int(self.beams_per_second)))
        # Pre-bind locals for speed
        scan_points_append = self.scan_points.append
        points_age_append = self.points_age.append
        max_range = self.max_range
        noise_std = self.noise_std
        beam_vectors = self.beam_unit_vectors
        obs_list = obstacles
        idx = self.current_angle_idx
        # precompute rotation components
        c, s = math.cos(robot_heading), math.sin(robot_heading)
        for _ in range(beams):
            ux, uy = beam_vectors[idx]  # local unit vector (cos, sin)
            # compute global beam direction as floats (avoid small arrays)
            bx = c * ux - s * uy
            by = s * ux + c * uy

            # ray origin in global coords
            rx, ry = robot_pos[0], robot_pos[1]

            # 障害物との交差判定
            min_dist = max_range
            for obstacle in obs_list:
                dist = obstacle.intersect((rx, ry), (bx, by))
                if dist is not None and dist < min_dist:
                    min_dist = dist

            # ノイズ追加
            min_dist = max(0.0, min_dist + (np.random.normal(0, noise_std)))

            # ローカル座標での点（origin=(0,0)）
            pt_local = (ux * min_dist, uy * min_dist)

            scan_points_append(pt_local)
            points_age_append(0.0)

            # 次のビーム角度へ
            idx = (idx + 1) % self.num_beams
        # store updated index and time
        self.current_angle_idx = idx
        self.last_update_time = current_time

        # 表示用の点群を更新
        if self.scan_points:
            self.last_scan_points_local = np.array(self.scan_points)
            self.last_scan_times = np.array(self.points_age)  # 年齢をそのまま使用
            # スキャン終了時の姿勢に対するローカル座標へ変換
            self.last_scan_points_global = self.transform_to_global(
                self.last_scan_points_local, robot_pos, robot_heading)
        else:
            self.last_scan_points_global = None
            self.last_scan_times = None
            self.last_scan_points_local = None

        return self.last_scan_points_global

class CircleObstacle:
    def __init__(self, center, radius):
        self.center = np.array(center)
        self.radius = radius

    def intersect(self, origin, direction):
        # ray-circle intersection (returns distance t along direction) or None
            # operate in pure-Python floats to avoid per-call numpy allocation
            ox, oy = origin[0], origin[1]
            dx, dy = direction[0], direction[1]
            cx, cy = self.center[0], self.center[1]
            ocx = ox - cx
            ocy = oy - cy
            a = dx*dx + dy*dy
            b = 2.0 * (ocx*dx + ocy*dy)
            c = ocx*ocx + ocy*ocy - self.radius * self.radius
            disc = b*b - 4*a*c
            if disc < 0:
                return None
            t = (-b - math.sqrt(disc)) / (2.0*a)
            if t < 0:
                return None
            return t

class PolygonObstacle:
    def __init__(self, vertices):
        # vertices: list or array of (x,y) points in order
        self.vertices = np.array(vertices, dtype=float)
        # precompute axis-aligned bounding box for quick rejection
        xs = self.vertices[:, 0]
        ys = self.vertices[:, 1]
        self.min_x = float(np.min(xs))
        self.max_x = float(np.max(xs))
        self.min_y = float(np.min(ys))
        self.max_y = float(np.max(ys))

    def intersect(self, origin, direction):
        # Ray-segment intersection for each edge. Return smallest positive t or None.
        ox, oy = origin
        dx, dy = direction
        # quick AABB rejection: check if ray intersects polygon bounding box
        # using slab method
        tmin = -float('inf')
        tmax = float('inf')
        if abs(dx) > 1e-12:
            tx1 = (self.min_x - ox) / dx
            tx2 = (self.max_x - ox) / dx
            tmin = max(tmin, min(tx1, tx2))
            tmax = min(tmax, max(tx1, tx2))
        else:
            # ray parallel to x slabs: if origin x not within bbox, reject
            if ox < self.min_x or ox > self.max_x:
                return None
        if abs(dy) > 1e-12:
            ty1 = (self.min_y - oy) / dy
            ty2 = (self.max_y - oy) / dy
            tmin = max(tmin, min(ty1, ty2))
            tmax = min(tmax, max(ty1, ty2))
        else:
            if oy < self.min_y or oy > self.max_y:
                return None
        # if slab intersection is empty or entirely behind ray origin, reject
        if tmax < tmin or tmax < 0:
            return None
        min_t = None
        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i+1) % n]
            vx, vy = x2 - x1, y2 - y1
            # Solve origin + t*dir = (x1,y1) + u*(v)
            # [dx, -vx] [t] = [x1 - ox]
            # [dy, -vy] [u]   [y1 - oy]
            denom = dx * (-vy) - dy * (-vx)  # dx*(-vy) - dy*(-vx) = -dx*vy + dy*vx
            if abs(denom) < 1e-9:
                continue
            rhs_x = x1 - ox
            rhs_y = y1 - oy
            t = (rhs_x * (-vy) - rhs_y * (-vx)) / denom
            u = (dx * rhs_y - dy * rhs_x) / denom
            # u in [0,1] means intersection on segment, t>=0 on ray
            if t >= 0 and u >= 0 and u <= 1:
                if min_t is None or t < min_t:
                    min_t = t
        return min_t

# ----- ロボットと操作 -----
class Robot:
    def __init__(self, x=0.0, y=0.0, width=0.8, length=1.0):
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([0.0, 0.0], dtype=float)
        self.cmd_vel = np.array([0.0, 0.0], dtype=float)
        self.width = width    # ロボットの幅 [m]
        self.length = length  # ロボットの長さ [m]
        self.radius = ROBOT_RADIUS  # 古い円形表現との互換性のため保持

    def get_vertices(self, heading):
        """ロボットの4つの頂点座標を計算（グローバル座標系）"""
        # ローカル座標での頂点位置（車体中心基準）
        half_w = self.width / 2.0
        half_l = self.length / 2.0
        local_vertices = np.array([
            [-half_l, -half_w],  # 左後
            [-half_l, half_w],   # 右後
            [half_l, half_w],    # 右前
            [half_l, -half_w],   # 左前
        ])
        
        # 回転行列
        c, s = np.cos(heading), np.sin(heading)
        R = np.array([[c, -s], [s, c]])
        
        # 回転して並進（グローバル座標に変換）
        global_vertices = np.dot(local_vertices, R.T) + self.pos
        return global_vertices

    def update(self, force, dt):
        # この簡易モデルでは force をそのまま加速度として扱う
        acc = force
        self.vel += acc * dt
        speed = np.linalg.norm(self.vel)
        if speed > MAX_SPEED and speed > 1e-8:
            self.vel *= (MAX_SPEED / speed)
        self.pos += self.vel * dt

    def set_cmd_vel(self, cmd_vel):
        # cmd_vel は目標速度（指令速度）として扱う
        self.cmd_vel = np.array(cmd_vel, dtype=float)

class KeyboardController:
    def __init__(self, robot):
        self.robot = robot
        self.key_mapping = {
            'up': np.array([0.0, 1.0]),
            'down': np.array([0.0, -1.0]),
            'left': np.array([-1.0, 0.0]),
            'right': np.array([1.0, 0.0])
        }
        self.pressed_keys = set()

    def on_key_press(self, event):
        # event.key はバックエンドに依存します。'up' などが渡る前提。
        key = event.key
        if key in self.key_mapping:
            self.pressed_keys.add(key)
            self.update_robot_cmd()

    def on_key_release(self, event):
        key = event.key
        if key in self.key_mapping:
            self.pressed_keys.discard(key)
            self.update_robot_cmd()

    def update_robot_cmd(self):
        cmd = np.zeros(2)
        for k in self.pressed_keys:
            cmd += self.key_mapping[k]
        if np.any(cmd):
            cmd = cmd / np.linalg.norm(cmd) * MAX_SPEED
        self.robot.set_cmd_vel(cmd)

# ----- 斥力の計算 -----
def calculate_vertex_repulsive_force(vertex_pos, global_obstacle_points):
    """
    1つの頂点に対する斥力を計算
    vertex_pos: 頂点位置（グローバル座標）
    global_obstacle_points: 障害物点群（グローバル座標）
    """
    if global_obstacle_points is None or len(global_obstacle_points) == 0:
        return np.zeros(2)
    
    # グローバル座標での距離計算
    distances = cdist([vertex_pos], global_obstacle_points).flatten()
    mask = distances <= INFLUENCE_RANGE
    if not np.any(mask):
        return np.zeros(2)
    
    nearby = global_obstacle_points[mask]
    d = distances[mask]
    # avoid divide-by-zero
    d = np.maximum(d, 1e-6)
    # 頂点から障害物への方向ベクトル（グローバル座標系）
    dirs = vertex_pos - nearby
    dirs = dirs / d.reshape(-1, 1)
    
    # ガウス関数に基づく斥力場の計算
    # U(d) = REPULSIVE_GAIN * exp(-(d/sigma)^2)
    # F(d) = -∇U(d) = (2d/sigma^2) * U(d) * dirs
    # sigma = INFLUENCE_RANGE/2 とすることで、
    # INFLUENCE_RANGEでポテンシャルがほぼ0になるようにする
    sigma = INFLUENCE_RANGE / 2.0
    potential = REPULSIVE_GAIN * np.exp(-(d/sigma)**2)
    # 距離による減衰を組み込んだ力の大きさ
    magnitudes = (2.0 * d / (sigma**2)) * potential
    
    # 合力計算（グローバル座標系）
    total = np.sum(dirs * magnitudes.reshape(-1, 1), axis=0)
    return total

def calculate_repulsive_force(robot_vertices, global_obstacle_points):
    """
    ロボットの4頂点それぞれに働く斥力を合成
    robot_vertices: ロボットの4頂点位置（グローバル座標系）
    global_obstacle_points: 障害物点群（グローバル座標）
    """
    # 各頂点での斥力を計算
    vertex_forces = [
        calculate_vertex_repulsive_force(vertex, global_obstacle_points)
        for vertex in robot_vertices
    ]
    
    # 4つの斥力の合力を返す
    total_force = np.sum(vertex_forces, axis=0)
    return total_force

# ----- メイン -----

def main():
    # 障害物定義
    obstacles = [
        # CircleObstacle([2.0, 2.0], 0.5),
        # CircleObstacle([-1.0, 1.5], 0.3),
        CircleObstacle([0.0, 0.0], 0.5),
        PolygonObstacle([[-4.0, -4.0], [-4.0, 5.0], [4.0, 5.0], [4.0, 4.0], [-3.0, 2.0], [-3.0, -4.0]]),
    ]

    lidar = LidarSimulator()
    robot = Robot(3.0, 2.0)
    controller = KeyboardController(robot)

    # プロット初期化
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.grid(True)
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_aspect('equal')

    # ロボットの形状（四角形）
    vertices = robot.get_vertices(0.0)  # 初期姿勢での頂点
    robot_polygon = MplPolygon(vertices, color='steelblue', alpha=0.5)
    ax.add_patch(robot_polygon)

    for obs in obstacles:
        if isinstance(obs, CircleObstacle):
            ax.add_patch(Circle(obs.center, obs.radius, color='gray', alpha=0.3))
        elif isinstance(obs, PolygonObstacle):
            poly_patch = MplPolygon(obs.vertices, color='gray', alpha=0.3)
            ax.add_patch(poly_patch)
        else:
            # unknown obstacle type: try to draw if possible
            try:
                ax.add_patch(Circle(obs.center, obs.radius, color='gray', alpha=0.3))
            except Exception:
                pass

    # scatter with colormap for per-beam timestamp visualization
    scatter = ax.scatter([], [], c=[], cmap='viridis', vmin=0.0, vmax=1.0, alpha=0.6, s=10)
    cmd_quiver = ax.quiver([], [], [], [], color='royalblue', scale=10)  # 指令速度の矢印も調整
    rep_quiver = ax.quiver([], [], [], [], color='tomato', scale=60, width=0.008)  # 合力の矢印も調整
    # 各頂点での斥力を表示するための矢印（異なる色で表示）
    vertex_colors = ['orange', 'orange', 'orange', 'orange']  # 左後、右後、右前、左前
    vertex_rep_quivers = [
        ax.quiver([], [], [], [], color=color, scale=60, alpha=0.7, width=0.005)  # scaleを大きく、線を細く
        for color in vertex_colors
    ]
    # robot heading arrow (shows orientation independent of velocity)
    heading_quiver = ax.quiver([], [], [], [], color='black', scale=1, width=0.02)

    fig.canvas.mpl_connect('key_press_event', controller.on_key_press)
    fig.canvas.mpl_connect('key_release_event', controller.on_key_release)

    sim_time = 0.0  # シミュレーション時刻
    # ロボットの進行方向を計算するための関数
    def calculate_robot_heading():
        """ロボットの進行方向を計算（速度ベクトルの向き）"""
        vel = robot.vel
        if np.all(vel == 0):
            # 停止中は前回の向きを保持
            return getattr(robot, 'last_heading', 0.0)
        heading = np.arctan2(vel[1], vel[0])
        robot.last_heading = heading  # 向きを保存
        return heading

    def update(frame):
        nonlocal sim_time
        
        # ロボットの現在の進行方向を計算
        robot_heading = 0.0#calculate_robot_heading()

        # 現在のシミュレーション時刻でLIDARスキャンを取得（更新はLIDAR_RATEで自動制御）
        # get_scan signature: (robot_pos, robot_vel, robot_cmd_vel, robot_heading, obstacles, current_time)
        points_global = lidar.get_scan(robot.pos, robot.vel, robot.cmd_vel, robot_heading, obstacles, sim_time)

        # 描画用: ローカル座標で保存された点群を現在のロボット姿勢で変換して表示
        if getattr(lidar, 'last_scan_points_local', None) is not None:
            points_to_display = lidar.transform_to_global(lidar.last_scan_points_local, robot.pos, robot_heading)
            scatter.set_offsets(points_to_display)
            if getattr(lidar, 'last_scan_times', None) is not None:
                colors_norm = lidar.last_scan_times / float(LIDAR_DT)
                scatter.set_array(colors_norm)
        else:
            scatter.set_offsets(np.zeros((0, 2)))  # 空の点群
            scatter.set_array(np.array([]))

        # 斥力計算ロボット座標系
        # ロボット座標系での4頂点位置
        local_vertices = robot.get_vertices(0.0) - robot.pos  # 原点中心の頂点位置
        
        # 各頂点での斥力を計算
        vertex_forces = [
            calculate_vertex_repulsive_force(vertex, lidar.last_scan_points_local)
            for vertex in local_vertices
        ]
        
        # 頂点ごとの斥力を可視化
        for vertex, force, quiver in zip(local_vertices, vertex_forces, vertex_rep_quivers):
            # 頂点位置をグローバル座標に変換
            global_vertex = vertex + robot.pos
            quiver.set_offsets([global_vertex])
            quiver.set_UVC(force[0], force[1])
        
        # 合力を計算
        rep_force = np.sum(vertex_forces, axis=0)

        # 指令速度(cmd_vel)は目標速度。コマンドに従うための力を速度誤差に比例させて作る。
        f_cmd = K_CMD * (robot.cmd_vel - robot.vel)
        total_force = f_cmd + rep_force
        robot.update(total_force, DT)

        # シミュレーション時刻を進める
        sim_time += DT

        # ロボットの描画を更新（姿勢を反映）
        robot_heading = 0.0  # calculate_robot_heading()
        vertices = robot.get_vertices(robot_heading)
        robot_polygon.set_xy(vertices)

        # ベクトル表示の更新
        # set_offsets expects Nx2 array; for single arrow wrap in list
        cmd_quiver.set_offsets([robot.pos])
        cmd_quiver.set_UVC(robot.cmd_vel[0], robot.cmd_vel[1])
        rep_quiver.set_offsets([robot.pos])
        rep_quiver.set_UVC(rep_force[0], rep_force[1])

        return (scatter, robot_polygon, cmd_quiver, rep_quiver, 
                *vertex_rep_quivers)  # 頂点ごとの斥力矢印を追加

    # アニメーション作成
    # blit=False にして互換性を高める
    ani = FuncAnimation(fig, update, frames=itertools.count(), interval=int(DT*1000), blit=False, cache_frame_data=False)
    # 保持
    globals()['ani'] = ani
    # plt.title('Artificial Potential Field Obstacle Avoidance Simulator')
    plt.show()

if __name__ == '__main__':
    main()
