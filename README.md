# BASHIUM

**BASHIUM** is a graphical tool written in Python that provides a user-friendly interface to manage and execute a collection of system configuration scripts tailored for Debian-based Linux distributions.

It leverages `tkinter` and `ttkbootstrap` to present a clean and responsive GUI for running system tweaks, software installers, and appearance configurations. BASHIUM is designed for users who prefer a visual way to set up or customize their Debian-based environment without manually handling multiple terminal scripts.

---

## Features

* Organized, GUI-based access to configuration and setup scripts
* Easily extendable — add your own scripts or modify existing ones
* Clean, modern interface with `ttkbootstrap` styling
* Designed specifically for Debian-based systems

---

## System Requirements

This application depends on the system-provided `tkinter` GUI toolkit and Python virtual environment support.  
Make sure to install these packages before launching BASHIUM:

```bash
sudo apt install python3-tk python3-venv

```

---

## Python Dependencies

Python packages used by the application are listed in `requirements.txt`, including:

* `ttkbootstrap` — modern theming for tkinter

These dependencies will be installed automatically when running the setup script (see below).

---

## Running the Application

To ensure all dependencies are handled correctly and to keep your environment clean, the project uses a Python virtual environment.

### Quick Start

Clone the repository and run the startup script:

```bash
git clone http://github.com/ArturStachera/bashium.git
cd bashium
chmod +x bashium.sh
./bashium.sh
```

This script will:

* Check if a virtual environment exists under `env/`
* If not, it will create it and install all Python dependencies
* Activate the environment
* Run the application

---

### Manual Steps (Optional)

If you prefer to do everything manually:

```bash
python3 -m venv env
source env/bin/activate
pip install ttkbootstrap
python3 main.py
```

---

## Folder Structure

```bash
bashium-master/
├── bashium.sh           # Startup script
├── configuration/       # Scripts and configs managed by the app
├── env/                 # Virtual environment (auto-created)
├── main.py              # Main Python GUI entry point
├── requirements.txt     # Python dependencies
├── software/            # Optional tools or custom setups
├── xfce_look/           # XFCE theming/configuration files
├── LICENSE              # MIT license
└── README.md            # You’re reading this
```

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
