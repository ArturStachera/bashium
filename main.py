import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
from pathlib import Path
import shlex

CONFIG_DESCRIPTION = (
    "Drivers, export /sbin directory to PATH variable\n"
    "Disable sound on logout\n"
    "Add repositories using terminal commands."
)

XFCE_LOOK_DESCRIPTION = (
    "Install XFCE themes, wallpapers, and icons.\n"
    "The script asks for username and installs resources in user folders."
)

SOFTWARE_DESCRIPTION = "Codecs, multimedia, compilation and extra software scripts."


class ScriptModule:
    def __init__(self, name: str, script_path: Path, description: str):
        self.name = name
        self.script_path = script_path
        self.description = description

    def run(self):
        print(f"[DEBUG] Attempting to run script: {self.script_path}")
        try:
            script_dir = shlex.quote(str(self.script_path.parent))
            cmd = f"cd {script_dir} && ./install.sh; exec bash"
            subprocess.run(
                ['kitty', '-e', 'bash', '-c', cmd],
                check=True
            )
            print(f"[DEBUG] Script executed successfully: {self.script_path}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Script execution failed: {e}")


class BashiumApp:
    def __init__(self, root: ttk.Window, modules: list[ScriptModule]):
        self.root = root
        self.modules = modules
        self.setup_ui()

    def setup_ui(self):
        self.root.title("BASHIUM")
        self.root.geometry("900x500")
        self.root.rowconfigure(0, weight=0)

        for i in range(len(self.modules) + 1):
            self.root.rowconfigure(i + 1, weight=1)

        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=5)

        header = ttk.Label(self.root, text="BASHIUM – System Tweaker", font=("Segoe UI", 20, "bold"))
        header.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="n")

        for idx, module in enumerate(self.modules, start=1):
            ttk.Label(self.root, text=module.name, font=("Segoe UI", 14, "bold")).grid(
                column=0, row=idx, padx=10, pady=5, sticky="nsew"
            )

            run_button = ttk.Button(self.root, text="RUN", bootstyle=SUCCESS, command=module.run)
            run_button.grid(
                column=1, row=idx, padx=10, pady=5,
                ipadx=10, ipady=5,
                sticky="nsew"
            )

            ttk.Label(self.root, text=module.description, wraplength=400, anchor="w", justify="left").grid(
                column=2, row=idx, padx=10, pady=5, sticky="nsew"
            )


def main():
    base_dir = Path(__file__).parent.resolve()

    modules = [
        ScriptModule("Configuration", base_dir / "configuration" / "install.sh", CONFIG_DESCRIPTION),
        ScriptModule("Xfce Look", base_dir / "xfce_look" / "install.sh", XFCE_LOOK_DESCRIPTION),
        ScriptModule("Software", base_dir / "software" / "install.sh", SOFTWARE_DESCRIPTION),
    ]

    root = ttk.Window(themename="darkly")
    app = BashiumApp(root, modules)
    root.mainloop()


if __name__ == "__main__":
    main()
