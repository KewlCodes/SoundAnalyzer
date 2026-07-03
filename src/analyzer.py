import json
import soundfile as sf
import pyloudnorm as pyln
import os
import numpy as np # Ensure this is at the top

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

    # --- ANALYSIS SECTION ---
    file_path = os.path.join(data_dir, selected_file)
    data, rate = sf.read(file_path)
    
    # Loudness
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    
    # True Peak Calculation
    true_peak = np.max(np.abs(data))
    true_peak_db = 20 * np.log10(true_peak)
    
    # --- OUTPUT SECTION ---
    print(f"\n--- Results for {selected_file} ---")
    print(f"Loudness:  {loudness:.2f} LUFS (Target: {target} LUFS)")
    print(f"True Peak: {true_peak_db:.2f} dBTP")
    
    # Loudness Status
    diff = loudness - target
    if abs(diff) < 0.5:
        print("Status: Perfect!")
    else:
        print(f"Status: Too {'loud' if diff > 0 else 'quiet'} by {abs(diff):.2f} LUFS.")
        
    # Clipping Warning
    if true_peak_db > 0:
        print("WARNING: Track is clipping (above 0 dBTP)!")

if __name__ == "__main__":
    select_and_analyze()