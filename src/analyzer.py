import json
import soundfile as sf
import pyloudnorm as pyln
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def select_and_analyze():
    config = load_config()
    target = config.get('target_lufs', -14.0)
    data_dir = "data"
    
    files = [f for f in os.listdir(data_dir) if f.endswith(".wav")]
    
    if not files:
        print("No .wav files found in the 'data/' folder.")
        return

    print("\n--- Available Tracks ---")
    for i, filename in enumerate(files):
        print(f"{i + 1}: {filename}")
    
    choice = input("\nEnter the number of the track to analyze: ")
    
    try:
        index = int(choice) - 1
        selected_file = files[index]
    except (ValueError, IndexError):
        print("Invalid selection. Please run the script again.")
        return

    # --- 1. LOAD AUDIO ---
    file_path = os.path.join(data_dir, selected_file)
    data, rate = sf.read(file_path)
    
    # Check if stereo or mono
    is_stereo = len(data.shape) > 1 and data.shape[1] == 2
    
    # --- 2. LOUDNESS & PEAK ANALYSIS ---
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    
    try:
        lra = meter.loudness_range(data)
    except AttributeError:
        lra = 0.0 
    
    true_peak = np.max(np.abs(data))
    true_peak_db = 20 * np.log10(true_peak + 1e-10) 
    
    # --- 3. SPECTRAL & STEREO CALCS ---
    # Create mono version for frequency math
    if is_stereo:
        mono_data = np.mean(data, axis=1)
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        
        # Calculate Phase Correlation (-1 to +1)
        # +1 means perfectly in phase (mono), 0 means wide stereo, -1 means out of phase (canceling)
        correlation = np.corrcoef(left_channel, right_channel)[0, 1]
    else:
        mono_data = data
        correlation = 1.0 # Mono is always perfectly correlated
        
    fft_out = np.fft.rfft(mono_data)
    fft_mag = np.abs(fft_out)
    freqs = np.fft.rfftfreq(len(mono_data), 1.0/rate)
    
    bass_idx = np.where((freqs >= 20) & (freqs <= 200))[0]
    bass_energy = np.sum(fft_mag[bass_idx])
    total_energy = np.sum(fft_mag)
    bass_ratio = (bass_energy / total_energy) * 100 if total_energy > 0 else 0

    # --- 4. TERMINAL OUTPUT ---
    print(f"\n--- Results for {selected_file} ---")
    print(f"Loudness:      {loudness:.2f} LUFS")
    print(f"True Peak:     {true_peak_db:.2f} dBTP")
    print(f"Phase Matrix:  {correlation:.2f} (1=Mono, 0=Wide, -1=Phase Issues)")

    # --- 5. THE 4-PANEL VISUAL DASHBOARD ---
    fig = plt.figure(figsize=(16, 9))
    fig.canvas.manager.set_window_title(f"Audio Diagnostic Dashboard - {selected_file}")
    
    # Set up a 2x2 grid
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0]) # Top Left
    ax2 = fig.add_subplot(gs[0, 1]) # Top Right
    ax3 = fig.add_subplot(gs[1, 0]) # Bottom Left
    ax4 = fig.add_subplot(gs[1, 1]) # Bottom Right

    # PANEL 1: Loudness & Headroom (Top Left)
    metrics = ['Your Loudness', 'Target', 'True Peak']
    values = [loudness, target, true_peak_db]
    colors = ['#3498db', '#2ecc71', '#e74c3c' if true_peak_db > -1.0 else '#f39c12']
    
    ax1.bar(metrics, values, color=colors, width=0.5)
    ax1.set_ylabel('Decibels (dB / LUFS)')
    ax1.set_title('Volume & Headroom Overview')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    for rect, val in zip(ax1.patches, values):
        height = rect.get_height()
        ax1.annotate(f'{val:.2f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3 if height > 0 else -15), textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

    # PANEL 2: Frequency Distribution (Top Right)
    fft_db = 20 * np.log10(fft_mag + 1e-5)
    visible_idx = np.where((freqs >= 20) & (freqs <= 20000))[0]
    ax2.plot(freqs[visible_idx], fft_db[visible_idx], color='#2c3e50', alpha=0.8)
    ax2.axvspan(20, 200, color='#e74c3c', alpha=0.15, label=f'Bass Zone ({bass_ratio:.1f}%)')
    ax2.set_xscale('log')
    ax2.set_xlim(20, 20000)
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Amplitude (dB)')
    ax2.set_title('Master EQ Spectrum')
    ax2.legend()
    ax2.grid(True, which="both", linestyle='--', alpha=0.5)

# PANEL 3: Spectrogram Waterfall (Bottom Left) - OPTIMIZED
    # 1. We increase nperseg to lower the time resolution (fewer blocks to draw)
    f, t, Sxx = signal.spectrogram(mono_data, rate, nperseg=4096, noverlap=2048)
    
    # 2. We use imshow instead of pcolormesh (imshow renders as a single flat image, which is 100x faster)
    ax3.imshow(10 * np.log10(Sxx + 1e-10), aspect='auto', cmap='magma', origin='lower', 
               extent=[t.min(), t.max(), f.min(), f.max()])
    
    ax3.set_yscale('symlog', linthresh=20)
    ax3.set_ylim(20, 20000)
    ax3.set_ylabel('Frequency (Hz)')
    ax3.set_xlabel('Time (Seconds)')
    ax3.set_title('Time vs. Frequency (Spectrogram)')

    # PANEL 4: Stereo Vectorscope Phase (Bottom Right) - OPTIMIZED
    if is_stereo:
        # Lowered from 50,000 to 10,000 dots to prevent graphics lag
        sample_size = min(10000, len(left_channel))
        indices = np.random.choice(len(left_channel), sample_size, replace=False)
        
        mid = (left_channel[indices] + right_channel[indices]) / 2
        side = (left_channel[indices] - right_channel[indices]) / 2
        
        # Increased transparency (alpha) to compensate for fewer dots
        ax4.scatter(side, mid, color='#00d2d3', alpha=0.1, s=1)
        ax4.axvline(0, color='gray', alpha=0.5, linestyle='--')
        ax4.axhline(0, color='gray', alpha=0.5, linestyle='--')
        ax4.set_xlim(-1, 1)
        ax4.set_ylim(-1, 1)
        ax4.set_title(f'Stereo Width (Phase Correl: {correlation:.2f})')
        ax4.set_xlabel('Side (L-R) - Width')
        ax4.set_ylabel('Mid (L+R) - Mono Center')
        
        if correlation < 0:
             ax4.text(0, -0.9, "WARNING: PHASE CANCELLATION", color='red', ha='center', fontweight='bold')
    else:
        ax4.text(0.5, 0.5, 'MONO FILE\nNo Stereo Data', ha='center', va='center', fontsize=14)
        ax4.set_xticks([])
        ax4.set_yticks([])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    select_and_analyze()