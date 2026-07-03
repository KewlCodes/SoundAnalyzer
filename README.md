# 🎛️ Game Audio Diagnostic Tool & Visual Analyzer

A specialized Python-based audio mastering utility engineered specifically for **indie game developers and sound designers**. This tool automates technical compliance auditing by parsing raw `.wav` audio assets and rendering an interactive, high-performance **4-panel visual dashboard**. 

It evaluates volume standards, maps frequency distribution signatures, tracks time-frequency alterations, and verifies stereo phase stability so your game sounds flawless across all playback hardware.

---

## 🚀 Key Telemetry & Diagnostic Features

* **Integrated Loudness (`LUFS`):** Evaluates overall perceived loudness over time using industry-standard **ITU-R BS.1770-4** curves to effortlessly normalize your game’s asset library.
* **True Peak Headroom (`dBTP`):** Monitors inter-sample peak signals to guarantee your mix components stay safely below digital clipping thresholds.
* **Acoustic Spectrum Mapping:** Isolates and calculates the exact power distribution of the **Bass Zone (20Hz - 200Hz)** to instantly identify "muddy mixes" that clash with gameplay sound effects (SFX).
* **Time-Frequency Spectrogram:** Maps audio energy density across a time-frequency matrix using optimized flat-image rendering to isolate hidden clicks or harsh resonant build-ups.
* **Stereo Phase Vectorscope:** Plots a live spatial cloud of your stereo field alongside a mathematical **Phase Correlation Index** to guarantee full mono-compatibility on small mobile devices.

---

## 📁 Project Structure

```text
├── data/                       # Target directory for uncompressed .wav master files
├── src/
│   └── analyzer.py             # Main DSP calculation & Matplotlib dashboard engine
├── config.json                 # Target LUFS calibration profile configuration
└── requirements.txt            # Locked sandbox environment dependency manifest

⚙️ Installation & Setup
💡 Prerequisite: Ensure you have Python installed and your shell terminal window focused on the project root folder.

1. Activate Sandbox Virtual Environment
Initialize your local isolated sandbox environment by running:

PowerShell
.\venv\Scripts\Activate.ps1
2. Install Project Manifest Dependencies
Synchronize your workspace environment with the pinned library framework requirements:

PowerShell
python -m pip install -r requirements.txt
🕹️ Production Pipeline Workflow
Export your audio track from your DAW as an uncompressed, raw .wav file.

Drop the file cleanly inside the local data/ project directory.

Initiate the command execution pipeline script:

PowerShell
python src/analyzer.py
Enter the index integer corresponding to your target asset and hit Enter.

🎯 Note: The terminal will instantly output localized quantitative variables, and an interactive Audio Diagnostic Dashboard window will materialize on your desktop screen.

📊 Decoding the 4-Panel Dashboard
🟦 Panel 1: Volume & Headroom Overview (Top Left)
Blue Bar (Your Loudness): Visually compares your track's average volume metrics directly against your designated target profile benchmark (Green Bar).

Orange Bar (True Peak): Represents your hardware ceiling ceiling limit. If this metric climbs up near or past 0.00, your track is actively causing digital distortion and clipping.

🟥 Panel 2: Master EQ Spectrum (Top Right)
Plots your mix equalization curve on a Logarithmic Scale calibrated to match biological human hearing curves.

Highlights the crucial Bass Zone in a red boundary. If the curve spikes excessively inside this boundary, utilize a High-Pass Filter (HPF) inside your DAW to reclaim headroom for gameplay sound assets like footsteps or explosions.

🟪 Panel 3: Time vs. Frequency Spectrogram (Bottom Left)
Reads left-to-right across the duration of your audio track timeline.

Bright yellow and white contours map high-energy events. Look for vertical pillars to find sudden transient spikes, or horizontal streaks to isolate piercing resonant rings.

🟩 Panel 4: Stereo Width Vectorscope (Bottom Right)
Visualizes the acoustic 3D soundstage. A tight vertical stick represents a pure mono signal; a broad diamond cloud indicates a wide, immersive stereo field.

🚨 Phase Correlation Indicator: Must remain strictly between 0.0 and +1.0. If it drops below zero, a warning flashes indicating dangerous Phase Cancellation issues that will cause elements of your track to completely vanish on mobile phone speakers.

🛠️ Technical Engine & Framework Specifications
Library	Subsystem Component Task Area	Standard Compliance / Implementation
numpy	Low-Level Array Operations & Matrix Algebra	Stereo separation & arithmetic averaging
soundfile	Binary Audio Stream I/O Interfacing	Uncompressed PCM .wav byte parsing
pyloudnorm	Loudness Measurement DSP Core	Fully ITU-R BS.1770-4 compliant gating
scipy	Windowed Signal Processing Math	Short-Time Fourier Transform (STFT) algorithms
matplotlib	Render Pipeline Graphic User UI Layout	Logarithmic graphing & real-time color mapping