"""
Global Figure Generation Script for XUPT 2026 Campus MCM
Generates 3 high-quality publication-ready figures:
1. Method Flowchart (4-step pipeline)
2. Noise Heatmap (3x2 matrix)
3. Results Radar Chart (5-dimensional comparison)

Author: Generated for XUPT 2026-B
Date: 2026-05-07
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
import seaborn as sns
from pathlib import Path

# Configuration
DPI = 200
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set publication style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'font.family': 'sans-serif',
    'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'Arial', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'axes.linewidth': 1.0,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.5,
})


def generate_flowchart():
    """
    Figure 1: Method Flowchart
    4-step pipeline with rounded rectangles and arrows
    """
    fig, ax = plt.subplots(figsize=(12, 6), dpi=DPI)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Step definitions
    steps = [
        {
            'name': '问题一\n时间对齐',
            'method': '三次样条 +\n一维搜索',
            'x': 1.5,
            'y': 3,
            'color': '#2C3E50',
            'output': 'Δτ*'
        },
        {
            'name': '问题二\n联合融合',
            'method': '联合估计 +\n卡尔曼滤波',
            'x': 4.5,
            'y': 3,
            'color': '#34495E',
            'output': '10Hz 轨迹'
        },
        {
            'name': '问题三\n偏差判定',
            'method': 'Wald 检验 +\nAIC 准则',
            'x': 7.5,
            'y': 3,
            'color': '#5D6D7E',
            'output': '判决 H0'
        },
        {
            'name': '问题四\n任务调度',
            'method': 'SG 平滑 +\nCP-SAT',
            'x': 10.5,
            'y': 3,
            'color': '#717D7E',
            'output': '25 任务'
        }
    ]

    # Draw steps
    box_width = 1.8
    box_height = 1.6

    for step in steps:
        # Main box
        box = FancyBboxPatch(
            (step['x'] - box_width/2, step['y'] - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            edgecolor='black',
            facecolor=step['color'],
            alpha=0.8,
            linewidth=2
        )
        ax.add_patch(box)

        # Step name (title)
        ax.text(step['x'], step['y'] + 0.4, step['name'],
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white')

        # Method description
        ax.text(step['x'], step['y'] - 0.2, step['method'],
                ha='center', va='center', fontsize=8.5,
                color='white', style='italic')

    # Draw arrows between steps
    arrow_y = 3
    arrow_props = dict(
        arrowstyle='->,head_width=0.4,head_length=0.6',
        lw=2.5,
        color='black',
        zorder=1
    )

    for i in range(len(steps) - 1):
        x1 = steps[i]['x'] + box_width/2
        x2 = steps[i+1]['x'] - box_width/2

        arrow = FancyArrowPatch(
            (x1, arrow_y), (x2, arrow_y),
            **arrow_props
        )
        ax.add_patch(arrow)

        # Arrow label (data flow)
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, arrow_y + 0.5, steps[i]['output'],
                ha='center', va='bottom', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor='gray', alpha=0.9))

    # Input/Output annotations
    ax.annotate('输入：\n附件 1-3\n原始观测',
                xy=(steps[0]['x'] - box_width/2, arrow_y),
                xytext=(0.3, arrow_y),
                fontsize=8, ha='center',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#F2F3F4',
                         edgecolor='black', linewidth=1.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    ax.annotate('输出：\n最优任务\n调度方案',
                xy=(steps[-1]['x'] + box_width/2, arrow_y),
                xytext=(11.7, arrow_y),
                fontsize=8, ha='center',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#F2F3F4',
                         edgecolor='black', linewidth=1.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    fig.suptitle('方法论流程：四问递进结构', fontsize=14, fontweight='bold', y=0.95)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig_method_flowchart.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[1/3] Flowchart saved: {output_path}")


def generate_noise_heatmap():
    """噪声热力图（中文版，高级感配色）"""
    data = np.array([
        [0.0000, 0.0000],
        [0.8239, 0.7966],
        [4.1674, 2.8973]
    ])

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=DPI)

    im = ax.imshow(data, cmap='Blues', aspect='auto', vmin=0, vmax=5.0)

    ax.set_xticks(np.arange(2))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels(['方式 1 (4 Hz)', '方式 2 (5 Hz)'], fontsize=11)
    ax.set_yticklabels(['附件 1（无噪声）', '附件 2（含噪声）', '附件 3（真实数据）'], fontsize=11)

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('噪声水平 σ (m)', rotation=270, labelpad=18, fontsize=11)

    for i in range(3):
        for j in range(2):
            color = 'white' if data[i, j] > 2.5 else 'black'
            ax.text(j, i, f'{data[i, j]:.2f} m',
                    ha="center", va="center", color=color,
                    fontsize=12, fontweight='bold')

    ax.set_xticks(np.arange(2) - 0.5, minor=True)
    ax.set_yticks(np.arange(3) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", size=0)

    ax.set_xlabel('定位方式', fontsize=12)
    ax.set_ylabel('数据来源', fontsize=12)
    ax.set_title('三份附件观测噪声水平对比', fontsize=13, fontweight='bold', pad=12)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig_noise_heatmap.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[2/3] Noise heatmap saved: {output_path}")


def generate_radar_chart():
    """雷达图（中文版）"""
    categories = ['时间\n精度', '空间\n精度', '鲁棒性',
                  '任务\n完成度', '计算\n效率']
    N = len(categories)

    data = {
        '问题一：样条对齐': [1.0, 1.0, 0.7, 0.5, 0.95],
        '问题二：联合估计+KF': [0.9, 0.7, 0.85, 0.5, 0.85],
        '问题四：CP-SAT 调度': [0.5, 0.6, 0.7, 0.69, 0.99],
    }

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    colors = ['#2C3E50', '#27AE60', '#E74C3C']
    markers = ['o', 's', 'D']

    fig, ax = plt.subplots(figsize=(10, 9), subplot_kw=dict(projection='polar'), dpi=DPI)

    for idx, (method, values) in enumerate(data.items()):
        vals = values + values[:1]
        ax.plot(angles, vals, '-', linewidth=2.5, label=method,
                color=colors[idx], marker=markers[idx], markersize=8)
        ax.fill(angles, vals, alpha=0.12, color=colors[idx])
        for i, (angle, val) in enumerate(zip(angles[:-1], values)):
            ax.annotate(f'{val:.2f}', xy=(angle, val), fontsize=8,
                       ha='center', va='bottom', color=colors[idx], weight='bold')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, weight='bold')

    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9, color='gray')

    ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.5)

    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=11,
              frameon=True, shadow=True, fancybox=True)

    plt.title('多维度性能综合评价',
              fontsize=14, fontweight='bold', pad=25, y=1.08)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig_results_radar.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[3/3] Radar chart saved: {output_path}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("XUPT 2026-B Global Figure Generation")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"DPI: {DPI}")
    print("=" * 60)

    # Generate all figures
    generate_flowchart()
    generate_noise_heatmap()
    generate_radar_chart()

    print("=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    for fig_file in OUTPUT_DIR.glob("fig_*.png"):
        size_mb = fig_file.stat().st_size / (1024 * 1024)
        print(f"  - {fig_file.name} ({size_mb:.2f} MB)")
    print()


if __name__ == "__main__":
    main()
