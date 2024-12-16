import tkinter as tk
from tkinter import ttk
import subprocess
from pathlib import Path

# Descriptive text constants
CONFIG_DESCRIPTION = (
    "Drivers, export /sbin directory to PATH variable\n"
    "Disable sound on logout\n" 
    "Add repositories using terminal command."
)
XFCE_LOOK_DESCRIPTION = " Themes, wallpapers, icons."
SOFTWARE_DESCRIPTION = "Codecs, multimedia, etc."

# Constants for colors
BACKGROUND_COLOR = "#6f6f6f"
BUTTON_COLOR = "#3daa3b"
BUTTON_ACTIVE_COLOR = "#075004"

# Get the directory where the script is located
script_directory = Path(__file__).parent.resolve()

# Run a shell script located at the specified path
def run_script(script_path):
    print(f"[DEBUG] Attempting to run script at: {script_path}")
    try:
        subprocess.run(
            ['x-terminal-emulator', '-e', f"bash -c 'cd {script_path.parent}; ./install.sh; exec bash'"],
            check=True
        )
        print(f"[DEBUG] Script executed successfully: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Script execution failed: {e}")



# Run the configuration script
def run_config():
    script_path = script_directory / 'configuration' / 'install.sh'
    print(f"[DEBUG] Running configuration script: {script_path}")
    run_script(script_path)

# Run the xfce-look script
def run_xfce_look():
    script_path = script_directory / 'xfce_look' / 'install.sh'
    print(f"[DEBUG] Running xfce-look script: {script_path}")
    run_script(script_path)

# Run the software script
def run_software():
    script_path = script_directory / 'software' / 'install.sh'
    print(f"[DEBUG] Running software script: {script_path}")
    run_script(script_path)

# Create the main application window
print("[DEBUG] Initializing main window application")
root = tk.Tk()
root.title("BASHIUM")
root.configure(bg=BACKGROUND_COLOR)

# Configure styles for various widgets
print("[DEBUG] Configuring widget styles")
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background=BACKGROUND_COLOR, foreground="black", font=("TkDeafaultFont", 12, "bold"))
style.configure("TButton", background=BUTTON_COLOR, foreground="black", font=("TkDeafaultFont", 12, "bold"), padding=15)
style.map("TButton", background=[["active", BUTTON_ACTIVE_COLOR]])

# Add widgets for the Configuration section
label = ttk.Label(root, text="Configuration", font=("TkDeafaultFont", 15, "bold"))
label.grid(column=0, row=1, padx=15, pady=15, sticky=tk.W)

button = ttk.Button(root, text="RUN", command=run_config)
button.grid(column=1, row=1, padx=15, pady=15, sticky=tk.W)

label_desc = ttk.Label(root, text=CONFIG_DESCRIPTION)
label_desc.grid(column=2, row=1, padx=15, pady=15, sticky=tk.W)

# Add widgets for the xfce-look section
label = ttk.Label(root, text="xfce-look", font=("TkDeafaultFont", 15, "bold"))
label.grid(column=0, row=2, padx=15, pady=15, sticky=tk.W)

button = ttk.Button(root, text="RUN", command=run_xfce_look)
button.grid(column=1, row=2, padx=15, pady=15, sticky=tk.W)

label_desc = ttk.Label(root, text=XFCE_LOOK_DESCRIPTION)
label_desc.grid(column=2, row=2, padx=15, pady=15, sticky=tk.W)

# Add widgets for the Software section
label = ttk.Label(root, text="Software", font=("TkDeafaultFont", 15, "bold"))
label.grid(column=0, row=3, padx=15, pady=15, sticky=tk.W)

button = ttk.Button(root, text="RUN", command=run_software)
button.grid(column=1, row=3, padx=15, pady=15, sticky=tk.W)

label_desc = ttk.Label(root, text=SOFTWARE_DESCRIPTION)
label_desc.grid(column=2, row=3, padx=15, pady=15, sticky=tk.W)

root.mainloop()