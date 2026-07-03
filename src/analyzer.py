import json
import soundfile as sf
import pyloudnorm as pyln
import os
import numpy as np

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
    
    # --- 2. LOUDNESS & PEAK ANALYSIS ---
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    
    # Loudness Range (LRA)
    try:
        lra = meter.loudness_range(data)
    except AttributeError:
        # Fallback if using an older version of pyloudnorm
        lra = 0.0 
    
    true_peak = np.max(np.abs(data))
    # Adding a tiny fraction to prevent log10(0) if the file has pure silence
    true_peak_db = 20 * np.log10(true_peak + 1e-10) 
    
    # Peak-to-Loudness Ratio (PLR)
    plr = true_peak_db - loudness
    
    # --- 3. SPECTRAL BALANCE (FFT) ---
    # Convert stereo to mono for frequency analysis to keep it simple
    if len(data.shape) > 1:
        mono_data = np.mean(data, axis=1)
    else:
        mono_data = data
        
    # Run the Fast Fourier Transform
    fft_out = np.fft.rfft(mono_data)
    fft_mag = np.abs(fft_out)
    freqs = np.fft.rfftfreq(len(mono_data), 1.0/rate)
    
    # Calculate energy in the "Muddy" Bass range (20Hz - 200Hz) vs Total Energy
    bass_idx = np.where((freqs >= 20) & (freqs <= 200))[0]
    bass_energy = np.sum(fft_mag[bass_idx])
    total_energy = np.sum(fft_mag)
    
    bass_ratio = (bass_energy / total_energy) * 100 if total_energy > 0 else 0

    # --- 4. OUTPUT RESULTS ---
    print(f"\n--- Results for {selected_file} ---")
    print(f"1. Loudness:      {loudness:.2f} LUFS (Target: {target} LUFS)")
    print(f"2. True Peak:     {true_peak_db:.2f} dBTP")
    if lra > 0:
        print(f"3. Dynamic Range: {lra:.2f} LU (LRA)")
    print(f"4. PLR (Punch):   {plr:.2f} dB")
    print(f"5. Bass Energy:   {bass_ratio:.1f}% of total spectrum")
    
    # --- 5. DIAGNOSTICS & SUGGESTIONS ---
    print("\n--- Diagnostic Suggestions ---")
    
    # Volume check
    diff = loudness - target
    if abs(diff) < 0.5:
        print("- Volume: Perfect!")
    else:
        print(f"- Volume: Too {'loud' if diff > 0 else 'quiet'} by {abs(diff):.2f} LUFS.")
        
    # Peak check
    if true_peak_db > -1.0:
        print("- Headroom: WARNING! Peaks are dangerously close to or exceeding 0 dBTP (Clipping risk).")
    
    # Dynamics check
    if lra > 0:
        if lra < 4:
            print("- Dynamics: Very compressed. Might sound 'squashed' or flat.")
        elif lra > 12:
            print("- Dynamics: Highly dynamic. Ensure quiet parts aren't lost in the game mix.")
            
    # Spectral check
    if bass_ratio > 30:
        print("- EQ: High bass energy detected. Check for 'muddiness' that might clash with game SFX.")

if __name__ == "__main__":
    select_and_analyze()