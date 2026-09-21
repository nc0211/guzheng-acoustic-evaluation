import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 你的最終綜合數據
data = {
    'Instrument': ['ins1', 'ins2', 'ins3'],
    'Brightness (Hz)': [1403.48, 1065.60, 866.05],
    'Purity/HNR (dB)': [13.55, 13.71, 12.01],
    'Continuity (Flatness x1k)': [0.1338, 0.0256, 0.0155],
    'Sustain Time (s)': [4.67, 4.56, 3.44],
}

df_summary = pd.DataFrame(data)

# 設定中文字型（若環境支援，這裡使用通用設定）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ================= 1. 繪製 4 大指標獨立長條對比圖 =================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Guzheng Acoustic Quality Multi-Dimensional Comparison', fontsize=16, fontweight='bold')

metrics = [
    ('Brightness (Hz)', 'Brightness (Higher = Brighter)', 'royalblue'),
    ('Purity/HNR (dB)', 'Purity / HNR (Higher = Cleaner)', 'forestgreen'),
    ('Continuity (Flatness x1k)', 'Spectral Continuity (Higher = Smoother)', 'darkorange'),
    ('Sustain Time (s)', 'Sustain Time (Higher = Longer Reverb)', 'purple')
]

for idx, (col, title, color) in enumerate(metrics):
    row = idx // 2
    col_idx = idx % 2
    ax = axes[row, col_idx]
    
    bars = ax.bar(df_summary['Instrument'], df_summary[col], color=color, alpha=0.8, width=0.5)
    ax.set_title(title, fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # 在長條上方加上數值標籤
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('output_plots/guzheng_comparison_bars.png', dpi=300)
plt.show()

# ================= 2. 繪製多維度正規化雷達圖 (Radar Chart) =================
# 為了讓不同單位的指標能在雷達圖上公平比較，我們將數據進行 Min-Max 正規化 (0 到 1 之間)
df_normalized = df_summary.copy()
features = ['Brightness (Hz)', 'Purity/HNR (dB)', 'Continuity (Flatness x1k)', 'Sustain Time (s)']

for feature in features:
    min_val = df_summary[feature].min()
    max_val = df_summary[feature].max()
    if max_val - min_val == 0:
        df_normalized[feature] = 1.0
    else:
        df_normalized[feature] = (df_summary[feature] - min_val) / (max_val - min_val)

# 雷達圖設定
labels = ['Brightness\n(明亮度)', 'Purity (HNR)\n(純淨度)', 'Continuity\n(能量連續性)', 'Sustain Time\n(殘響漂浮)']
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:0]  # 閉合

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

colors = ['royalblue', 'forestgreen', 'crimson']

for i, row in df_normalized.iterrows():
    values = row[features].values.flatten().tolist()
    values += values[:0]  # 閉合
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=row['Instrument'], color=colors[i])
    ax.fill(angles, values, color=colors[i], alpha=0.15)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=11, fontweight='bold')

ax.set_title('Guzheng Multi-Dimensional Acoustic Radar Chart (Normalized)', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=12)

plt.tight_layout()
plt.savefig('output_plots/guzheng_radar_chart.png', dpi=300)
plt.show()

print(" 圖表已成功產出，並自動儲存至 output_plots/ 資料夾中！")
