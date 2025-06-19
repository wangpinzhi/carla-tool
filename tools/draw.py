import numpy as np
import matplotlib.pyplot as plt
import os

def draw(folder, scene):
    # 替换为你的txt文件目录路径
    # folder = "output\outdoor_Town07\post_data"
    # scene = "outdoor_Town07_2"

    folder_path = os.path.join(folder, scene)

    # 存储所有相机位置的列表
    camera_positions = []

    # 获取并按名称排序所有txt文件
    file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.txt')])  # 根据实际文件名调整排序方式
    file_list = file_list[1:] 

    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        
        # 读取4x4变换矩阵
        matrix = np.loadtxt(file_path)
        
        # 提取平移分量（假设矩阵为相机到世界坐标系的变换矩阵）
        # 平移分量位于矩阵的第四列前三个元素
        tx, ty, tz = matrix[:3, 3]
        camera_positions.append([tx, ty, tz])

    # 转换为numpy数组
    camera_positions = np.array(camera_positions)

    # 创建3D图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制轨迹
    ax.plot(camera_positions[:, 0],  # X坐标
            camera_positions[:, 1],  # Y坐标
            camera_positions[:, 2],  # Z坐标
            # marker='o',             # 数据点标记
            # markersize=4,           # 标记大小
            linestyle='-',          # 连线样式
            linewidth=2,            # 连线粗细
            color='b')              # 颜色

    # 设置坐标轴标签
    ax.set_xlabel('X Axis', fontsize=12)
    ax.set_ylabel('Y Axis', fontsize=12)
    ax.set_zlabel('Z Axis', fontsize=12)

    # 设置标题
    # plt.title('Camera Movement Trajectory', fontsize=14)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 调整视角（可选参数）
    ax.view_init(elev=20, azim=-35)  # 仰角20度，方位角-35度

    output_path = os.path.join(folder, f"{scene}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')  

    # 关闭图形，释放内存
    plt.close(fig)

folder = "output\indoor_city\post_data"
scenes = "indoor_city"

for i in range(1, 7):
    scene = f"{scenes}_{i}"
    draw(folder, scene)