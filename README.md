# Stimmenfeanher\_Heidenheim







\# 🎙️ Stimmenfänger – Real-Time German Speech-to-Text with BERT Attention Analysis



This project combines real-time speech-to-text transcription with keyword extraction and attention scoring. Using a lightweight speech recognition model, it transcribes spoken German audio, then leverages KeyBERT to identify and score the most relevant keywords from the transcribed text. This tool can be useful for applications like voice-driven search, meeting transcription, or content analysis.




---

\## 📝 To Do

# Animation:
- Background textures
- Text with Displacement
- Reihen einzeln animieren
- Stable Diffusion ?
- Text animieren
- Color change over time
- What to so with Empty space
- Y-Axis Animation more random
- Typography ?

# System:
- Watchdog

# Speech-to-Text:
- Google API einbauen
- Python Script in Startup && Send UDP clock for restart

# Startup Routing:
- Beamer autostart
- Screens Autostart, WOL

# Microphone
- Verlängerung Kabel
- Raspberry Pi ?

# FTP upload:
- Ftp upload
- Webseite bauen

# Hardware:
- Box bauen
- HDMI-Network testen

# Aufbau:
- Beamer Halterung ?
- Auto ausleihen


# Abbau:
- Bis wann ?


\## 📦 Installation



Make sure you have Python 3.8–3.10 installed.



\### 1. Set up the environment



```bash

conda create -n stt python=3.12.8

conda activate stt




\# Install Libary



pip install -r requirements.txt



---


\# Download Model: vosk-model-small-de-0.15

https://alphacephei.com/vosk/models

& unzip in /stt folder



\## 🔍 Overview how to start:


python -u stt_de_keywords_top5_unigrams.py --device 1 --model "C:\Users\simon\Documents\Stimmenfaenger\stt\vosk-model-small-de-0.15"






---





