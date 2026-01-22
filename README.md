# BASHIUM

**BASHIUM** is a small GUI launcher for Debian configuration scripts.

It uses `tkinter` + `ttkbootstrap` to provide a clean interface for running system tweaks, software installers, and appearance setup scripts.

---

## Features

- **Script launcher GUI**
- **Easy to extend** (add/modify scripts under `configuration/`, `software/`, `xfce_look/`)
- **Modern look & feel** via `ttkbootstrap`
- **Theme/palette preset selector** (persisted per-user)
- **Debian-focused** (APT sources, firmware, NVIDIA drivers)

---

## Requirements

Install the system packages required to run the GUI and bootstrap the Python virtualenv:

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-tk \
  python3-venv \
  curl \
  git
```

Notes:

- `curl` can be required by `pip`/build steps on minimal installs.
- Some scripts may additionally require tools like `unzip` (for XFCE themes/icons).

---

## Python dependencies

Python packages are listed in `requirements.txt` (currently: `ttkbootstrap`).

---

## Running

### Quick start

```bash
git clone https://github.com/ArturStachera/bashium.git
cd bashium
chmod +x bashium.sh
./bashium.sh
```

The startup script will:

- **Create** a virtual environment under `env/` (if missing)
- **Install** Python dependencies
- **Start** the application

### Manual run (optional)

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## Folder structure

```text
bashium/
  bashium.sh
  main.py
  requirements.txt
  configuration/
  software/
  xfce_look/
```

---

## NVIDIA Drivers (Debian)

The NVIDIA flow is implemented in:

- `configuration/nvidia.sh`

It is called from:

- `configuration/firmware.sh`

### What it does

When an NVIDIA GPU is detected, the script:

- Asks whether to use the proprietary NVIDIA driver or Nouveau
- If proprietary is selected:
  - Ensures Debian `contrib non-free non-free-firmware` components are enabled
  - Installs `nvidia-detect` and picks the recommended package (including legacy packages such as `nvidia-legacy-470xx-driver` when applicable)
  - Enables `*-backports` automatically if the recommended package is not available in the current APT sources
  - Blacklists Nouveau and updates initramfs
- If Nouveau is selected:
  - Removes the Nouveau blacklist (if present)
  - Optionally purges installed `nvidia-*` packages

After changing the driver, a reboot is recommended.

### Repo and release detection

During the NVIDIA flow, BASHIUM detects:

- Debian track: `stable`, `testing`, `unstable` (based on `apt-cache policy`)
- Whether `*-backports` is already enabled
- Whether `non-free` is already present in APT sources

This is used to avoid enabling backports on `unstable` and to make the flow more robust across different Debian releases.

### Troubleshooting

- If you see messages like "Conflicting nouveau kernel module loaded" during installation, it usually means Nouveau was already loaded by the running kernel session. BASHIUM will blacklist Nouveau for the next boot, but a reboot is still required for the proprietary driver to take over.
- If you enabled `*-backports` (explicitly or implicitly) and then see dependency errors for `firmware-linux-nonfree` / `firmware-misc-nonfree`, make sure the firmware packages are installed from the same suite as the NVIDIA packages (stable vs backports). BASHIUM attempts to keep them consistent automatically.
- Boot logs showing repeated `ata` / `I/O error` messages indicate storage problems and are unrelated to GPU drivers. Check the disk/cable/port and review SMART data.

---

## GUI appearance

You can switch the UI appearance from the top bar.

The selected preset is stored in:

- `~/.config/bashium/config.json` (or `$XDG_CONFIG_HOME/bashium/config.json`)

### Palette presets (HEX colors)

The GUI uses palette presets based on HTML-like HEX codes (for example `#282828`).

The palette preset is stored in the config file under `palette_preset`.

---

## Contributing

Feel free to fork this repository and contribute via pull requests.
Any improvements, bug fixes, or suggestions are welcome!

---

## License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## Author

**Artur Stachera**
