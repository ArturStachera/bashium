import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
from pathlib import Path
import shlex
import json
import os

CONFIG_DESCRIPTION = (
    "Drivers, export /sbin directory to PATH variable\n"
    "Disable sound on logout\n"
)

XFCE_LOOK_DESCRIPTION = (
    "Install XFCE themes, wallpapers, and icons.\n"
    "The script asks for username and installs resources in user folders."
)

SOFTWARE_DESCRIPTION = "Codecs, multimedia, compilation and extra software scripts."


class ScriptModule:
    def __init__(self, name: str, script_path: Path, description: str, enabled: bool = True):
        self.name = name
        self.script_path = script_path
        self.description = description
        self.enabled = enabled

    def run(self):
        print(f"[DEBUG] Attempting to run script: {self.script_path}")
        try:
            if self.script_path.is_dir():
                script_dir = shlex.quote(str(self.script_path))
                cmd = f"cd {script_dir} && ./install.sh; exec bash"
            else:
                script_dir = shlex.quote(str(self.script_path.parent))
                script_name = shlex.quote(str(self.script_path.name))
                cmd = f"cd {script_dir} && bash ./{script_name}; exec bash"
            subprocess.run(
                ['x-terminal-emulator', '-e', 'bash', '-c', cmd],
                check=True
            )
            print(f"[DEBUG] Script executed successfully: {self.script_path}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Script execution failed: {e}")


class BashiumApp:
    def __init__(self, root: ttk.Window, modules: list[ScriptModule]):
        self.root = root
        self.modules = modules
        self.config_path = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "bashium" / "config.json"
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

        header_frame = ttk.Frame(self.root, style="Bashium.TFrame")
        header_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="nsew")
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        header = ttk.Label(header_frame, text="BASHIUM – System Tweaker", font=("Segoe UI", 20, "bold"), style="Bashium.TLabel")
        header.grid(row=0, column=0, sticky="w")

        controls_frame = ttk.Frame(header_frame, style="Bashium.TFrame")
        controls_frame.grid(row=0, column=1, sticky="e")
        controls_frame.columnconfigure(0, weight=0)

        palette_presets = {
            "Gruvbox Dark": {"bg": "#282828", "fg": "#ebdbb2", "accent": "#fabd2f", "muted": "#3c3836"},
            "Gruvbox Light": {"bg": "#fbf1c7", "fg": "#3c3836", "accent": "#d79921", "muted": "#7c6f64"},
            "Tokyo Night": {"bg": "#1a1b26", "fg": "#c0caf5", "accent": "#7aa2f7", "muted": "#24283b"},
            "Cyberpunk": {"bg": "#0b0f1a", "fg": "#e6e6e6", "accent": "#ff2a6d", "muted": "#1b1f36"},
            "Neon Cyan": {"bg": "#07161b", "fg": "#d7f9ff", "accent": "#00f5ff", "muted": "#0b2a33"},
        }
        selected_preset = self._load_palette_preset(default="Neon Cyan")
        self.palette_var = ttk.StringVar(value=selected_preset)
        palette_box = ttk.Combobox(controls_frame, textvariable=self.palette_var, values=list(palette_presets.keys()), state="readonly", width=16, style="Bashium.TCombobox")
        palette_box.grid(row=0, column=0, sticky="e")

        def on_palette_change(event=None):
            preset = self.palette_var.get()
            palette = palette_presets.get(preset)
            self._apply_palette(palette)
            self._save_palette_preset(preset)

        palette_box.bind("<<ComboboxSelected>>", on_palette_change)
        on_palette_change()

        for idx, module in enumerate(self.modules, start=1):
            ttk.Label(self.root, text=module.name, font=("Segoe UI", 14, "bold"), style="Bashium.TLabel").grid(
                column=0, row=idx, padx=10, pady=5, sticky="nsew"
            )

            run_button = ttk.Button(self.root, text="RUN", command=module.run, style="Bashium.TButton")
            run_button.grid(
                column=1, row=idx, padx=10, pady=5,
                ipadx=10, ipady=5,
                sticky="nsew"
            )

            if not module.enabled:
                run_button.configure(state=DISABLED)

            ttk.Label(self.root, text=module.description, wraplength=400, anchor="w", justify="left", style="Bashium.TLabel").grid(
                column=2, row=idx, padx=10, pady=5, sticky="nsew"
            )

    def _load_palette_preset(self, default: str) -> str:
        try:
            data = self._load_config()
            preset = data.get("palette_preset")
            if isinstance(preset, str) and preset:
                return preset
        except Exception:
            pass
        return default

    def _save_palette_preset(self, preset: str) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            data = self._load_config()
            data["palette_preset"] = preset
            self.config_path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass

    def _load_config(self) -> dict:
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _apply_palette(self, palette: dict | None) -> None:
        if not palette:
            return

        style = self.root.style
        bg = palette.get("bg")
        fg = palette.get("fg")
        accent = palette.get("accent")
        muted = palette.get("muted")

        try:
            self.root.configure(background=bg)
        except Exception:
            pass

        demonstrate_colors = {
            "background": bg,
            "foreground": fg,
        }

        try:
            style.configure("Bashium.TFrame", **demonstrate_colors)
            style.configure("Bashium.TLabel", **demonstrate_colors)
            style.configure(
                "Bashium.TCombobox",
                foreground=fg,
                fieldbackground=bg,
                background=bg,
                selectbackground=muted or bg,
                selectforeground=fg,
                arrowcolor=fg,
            )
        except Exception:
            pass

        try:
            style.configure(
                "Bashium.TButton",
                foreground=bg,
                background=accent,
                bordercolor=accent,
                focusthickness=2,
                focuscolor=muted or accent,
            )
            style.map(
                "Bashium.TButton",
                background=[("active", muted or accent), ("pressed", muted or accent)],
                foreground=[("active", bg), ("pressed", bg)],
            )
        except Exception:
            pass


def has_nvidia_gpu() -> bool:
    try:
        out = subprocess.check_output(["lspci"], text=True, stderr=subprocess.DEVNULL)
        return "nvidia" in out.lower()
    except Exception:
        return False



def main():
    base_dir = Path(__file__).parent.resolve()

    nvidia_detected = has_nvidia_gpu()
    nvidia_desc = "Detected NVIDIA GPU. You can configure drivers now." if nvidia_detected else "No NVIDIA GPU detected on this system."

    modules = [
        ScriptModule("Configuration", base_dir / "configuration", CONFIG_DESCRIPTION),
        ScriptModule("NVIDIA", base_dir / "configuration" / "nvidia.sh", nvidia_desc, enabled=nvidia_detected),
        ScriptModule("Xfce Look", base_dir / "xfce_look", XFCE_LOOK_DESCRIPTION),
        ScriptModule("Software", base_dir / "software", SOFTWARE_DESCRIPTION),
    ]

    root = ttk.Window(themename="darkly")
    app = BashiumApp(root, modules)
    root.mainloop()


if __name__ == "__main__":
    main()
