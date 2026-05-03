# Jio5G-Stabilizer

A lightweight Windows utility that smooths internet traffic to help stabilize Jio 5G hotspot connections during large downloads.

Built with:
- Python
- PyQt6
- WinDivert

## Features

- Live network speed monitor
- Simple GUI
- Packet-based traffic shaping
- Helps reduce 5G → LTE fallback during hotspot downloads
- Lightweight and easy to use

## Why?

Some Jio 5G connections become unstable during large sustained downloads (game downloads, Steam, Riot, etc.) and fall back to LTE.

This tool smooths traffic bursts to keep throughput more stable.

## Requirements

- Windows
- Python 3.10+
- Administrator privileges

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Build EXE

```bash
pyinstaller --onefile --windowed main.py
```

IMPORTANT:
Place `WinDivert.dll` beside the generated EXE.

## Disclaimer

This is an experimental personal project and not a professional traffic shaping solution.