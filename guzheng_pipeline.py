import os
import glob
import librosa
import numpy as np
import pandas as pd

output_audio_dir = 'output_mp3'
# 確保只抓取結尾是 _main.mp3 的檔案
audio_files = glob.glob(os.path.join(output_audio_dir, '*_main.mp3'))

all_results = []

print(f"正在安全掃描並分析全部 {len(audio_files)} 個主音檔...\n")

for file_path in audio_files:
    filename = os.path.basename(file_path)
    base_name = filename.replace('_main.mp3', '')

    # 1. 智慧辨識技法 (Technique)
    if 'gliss' in base_name:
        file_type = 'gliss'
    elif 'chord' in base_name:
        file_type = 'chord'
    elif 'strech' in base_name:
        file_type = 'strech'
    else:
        print(f" 無法辨識技法，跳過檔案: {filename}")
        continue

    # 2. 智慧辨識琴號 (Instrument ID: ins1, ins2, ins3, ins4...)
    ins_id = None
    for ins in ['ins1', 'ins2', 'ins3', 'ins4']:
        if ins in base_name:
            ins_id = ins
            break
    
    if not ins_id:
        print(f" 無法辨識琴號，跳過檔案: {filename}")
        continue

    # 3. 抓取測試次數 (Take) - 抓取檔名最後的數字
    try:
        take_id = base_name.split('_')[-1]
    except:
        take_id = '1'

    # 載入音檔進行聲學分析
    y, sr = librosa.load(file_path, sr=None)

    # 1. 亮度：頻譜重心
    brightness = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

    # 2. 純淨度：HNR 諧波噪聲比
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    harmonic_energy = np.sum(y_harmonic ** 2)
    noise_energy = np.sum(y_percussive ** 2)
    hnr_proxy = 10 * np.log10(harmonic_energy / (noise_energy + 1e-6))

    # 3. 能量分佈連續性：頻譜平坦度
    flatness = np.mean(librosa.feature.spectral_flatness(y=y))

    # 4. 殘響/聲音漂多久：Sustain Time (-40dB 衰減時間)
    rms = librosa.feature.rms(y=y)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    times = librosa.times_like(rms, sr=sr)
    
    peak_idx = np.argmax(rms_db)
    tail_times = times[peak_idx:]
    tail_db = rms_db[peak_idx:]
    
    below_40 = np.where(tail_db <= -40)[0]
    if len(below_40) > 0:
        sustain_time = tail_times[below_40[0]] - tail_times[0]
    else:
        if tail_db[-1] - tail_db[0] < -1:
            slope = (tail_db[-1] - tail_db[0]) / (tail_times[-1] - tail_times[0])
            sustain_time = (-40 - tail_db[0]) / slope
        else:
            sustain_time = tail_times[-1] - tail_times[0]

    all_results.append({
        'Instrument': ins_id,
        'Technique': file_type,
        'Take': take_id,
        'Brightness (Hz)': round(brightness, 2),
        'Purity/HNR (dB)': round(hnr_proxy, 2),
        'Continuity (Flatness x1k)': round(flatness * 1000, 4),
        'Sustain Time (s)': round(max(0.1, sustain_time), 2)
    })

df_all = pd.DataFrame(all_results)
df_all = df_all.sort_values(by=['Instrument', 'Technique', 'Take'])

print(f"\n 成功解析並處理了 {len(df_all)} 個檔案！")
print("=== 各琴跨所有技法的最終綜合總結表 ===")
df_grand_summary = df_all.groupby('Instrument')[
    ['Brightness (Hz)', 'Purity/HNR (dB)', 'Continuity (Flatness x1k)', 'Sustain Time (s)']
].mean().reset_index()
print(df_grand_summary.to_string(index=False))
