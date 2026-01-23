import customtkinter as ctk
from pathlib import Path
import subprocess
import shutil
import shlex
import json
import os
import traceback
from datetime import datetime
from typing import Optional

# Konfiguracja CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_DESCRIPTION = (
    "Drivers, export /sbin directory to PATH variable\n"
    "Disable sound on logout"
)

XFCE_LOOK_DESCRIPTION = (
    "Install XFCE themes, wallpapers, and icons.\n"
    "The script asks for username and installs resources in user folders."
)

SOFTWARE_DESCRIPTION = "Codecs, multimedia, compilation and extra software scripts."


def _safe_check_output(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def _log_exception(context: str, exc: BaseException) -> None:
    try:
        cfg_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "bashium"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        log_path = cfg_dir / "bashium.log"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().isoformat(timespec='seconds')}] {context}\n")
            f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    except Exception:
        return


def detect_nvidia_gpu() -> bool:
    out = _safe_check_output(["lspci", "-nn"])
    return "nvidia" in out.lower()


def detect_bluetooth_controller() -> bool:
    out_rfkill = _safe_check_output(["rfkill", "list"])
    if "bluetooth" in out_rfkill.lower():
        return True

    out_lspci = _safe_check_output(["lspci"])
    if "bluetooth" in out_lspci.lower():
        return True

    out_lsusb = _safe_check_output(["lsusb"])
    if "bluetooth" in out_lsusb.lower():
        return True

    try:
        entries = os.listdir("/sys/class/bluetooth")
        return any(e.startswith("hci") for e in entries)
    except Exception:
        return False


def detect_wifi_vendors() -> set[str]:
    hw = "\n".join(
        [
            _safe_check_output(["lspci", "-nn"]),
            _safe_check_output(["lsusb"]),
        ]
    ).lower()

    vendors: set[str] = set()
    if not hw.strip():
        return vendors

    if any(x in hw for x in ["network controller", "wireless", "wi-fi", "802.11"]):
        if any(x in hw for x in ["intel", "8086:"]):
            vendors.add("Intel")
        if any(x in hw for x in ["broadcom", "bcm", "14e4:"]):
            vendors.add("Broadcom")
        if any(x in hw for x in ["realtek", "rtl", "10ec:", "0bda:"]):
            vendors.add("Realtek")
        if any(x in hw for x in ["atheros", "qualcomm", "168c:", "0cf3:"]):
            vendors.add("Atheros/Qualcomm")
        if any(x in hw for x in ["mediatek", "mediatk", "mtk", "14c3:", "0e8d:"]):
            vendors.add("MediaTek")
        if any(x in hw for x in ["ralink", "148f:"]):
            vendors.add("Ralink")

    return vendors


def detect_usb_devices_summary() -> str:
    out = _safe_check_output(["lsusb"]).strip()
    if not out:
        return "USB: unknown"
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return f"USB: {len(lines)} device(s)"


def has_nonfree_enabled() -> bool:
    cmd = ["bash", "-lc", "grep -Rqs -- 'non-free' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null"]
    try:
        return subprocess.run(cmd, check=False).returncode == 0
    except Exception:
        return False


class ScriptModule:
    def __init__(self, name: str, script_path: Path, description: str, enabled: bool = True):
        self.name = name
        self.script_path = script_path
        self.description = description
        self.enabled = enabled

    def _build_shell_command(self) -> str:
        if self.script_path.is_dir():
            script_dir = shlex.quote(str(self.script_path))
            return f"cd {script_dir} && ./install.sh; exec bash"

        script_dir = shlex.quote(str(self.script_path.parent))
        script_name = shlex.quote(str(self.script_path.name))
        return f"cd {script_dir} && bash ./{script_name}; exec bash"

    def _find_terminal(self) -> tuple[list[str] | None, str]:
        shell_cmd = self._build_shell_command()
        human_cmd = f"bash -lc {shlex.quote(shell_cmd)}"

        candidates = [
            "x-terminal-emulator",
            "gnome-terminal",
            "kgx",
            "konsole",
            "xfce4-terminal",
            "mate-terminal",
            "tilix",
            "alacritty",
            "kitty",
            "lxterminal",
            "xterm",
        ]

        term = None
        for c in candidates:
            if shutil.which(c):
                term = c
                break

        if term is None:
            return None, human_cmd

        # Terminal-specific invocation
        if term in {"gnome-terminal", "mate-terminal"}:
            return [term, "--", "bash", "-lc", shell_cmd], human_cmd
        if term == "kgx":
            return [term, "--", "bash", "-lc", shell_cmd], human_cmd
        if term == "konsole":
            return [term, "-e", "bash", "-lc", shell_cmd], human_cmd
        if term == "xfce4-terminal":
            return [term, "--command", f"bash -lc {shlex.quote(shell_cmd)}"], human_cmd
        if term == "tilix":
            return [term, "-e", f"bash -lc {shlex.quote(shell_cmd)}"], human_cmd
        if term in {"alacritty", "kitty", "lxterminal", "xterm", "x-terminal-emulator"}:
            return [term, "-e", "bash", "-lc", shell_cmd], human_cmd

        return [term, "-e", "bash", "-lc", shell_cmd], human_cmd

    def run(self) -> None:
        argv, human_cmd = self._find_terminal()
        if argv is None:
            raise RuntimeError(
                "No supported terminal emulator found. "
                "Install one of: gnome-terminal, konsole, xfce4-terminal, xterm. "
                f"You can run this manually: {human_cmd}"
            )

        try:
            subprocess.Popen(argv)
        except Exception as e:
            raise RuntimeError(f"Failed to launch terminal: {e}. Command: {' '.join(argv)}")


class ModuleCard(ctk.CTkFrame):
    """Nowoczesna karta modułu z animacjami"""
    
    def __init__(self, master, module: ScriptModule, colors: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.module = module
        self.colors = colors
        
        self.configure(
            fg_color=colors["card_bg"],
            corner_radius=12,
            border_width=2,
            border_color=colors["border"]
        )
        
        # Padding wewnętrzny
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header z nazwą
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=module.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors["accent"]
        )
        name_label.pack(side="left")
        
        # Status indicator
        status_color = colors["success"] if module.enabled else colors["muted"]
        status_dot = ctk.CTkLabel(
            header_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=status_color
        )
        status_dot.pack(side="left", padx=(10, 0))
        
        # Opis
        desc_label = ctk.CTkLabel(
            self,
            text=module.description,
            font=ctk.CTkFont(size=12),
            text_color=colors["fg"],
            anchor="w",
            justify="left",
            wraplength=500
        )
        desc_label.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        
        # Przycisk RUN
        self.run_button = ctk.CTkButton(
            self,
            text="▶ RUN SCRIPT",
            command=self._run_with_dialog,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=colors["accent"],
            hover_color=colors["accent_hover"],
            text_color="#000000" if module.enabled else "#404040",
            corner_radius=8,
            height=40,
            state="normal" if module.enabled else "disabled"
        )
        self.run_button.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Hover effect
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
    
    def _on_hover(self, event):
        if self.module.enabled:
            self.configure(border_color=self.colors["accent"])
    
    def _on_leave(self, event):
        self.configure(border_color=self.colors["border"])
    
    def _run_with_dialog(self):
        try:
            dialog = ctk.CTkToplevel(self)
            dialog.title("Confirm Execution")
            dialog.geometry("400x200")
            dialog.transient(self.master)
            dialog.bind("<Escape>", lambda _e: dialog.destroy())

            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"400x200+{x}+{y}")

            try:
                ctk.CTkLabel(
                    dialog,
                    text=f"Run {self.module.name}?",
                    font=ctk.CTkFont(size=16, weight="bold")
                ).pack(pady=(20, 10))

                ctk.CTkLabel(
                    dialog,
                    text="This will execute the script in a terminal window.",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                ).pack(pady=(0, 20))

                button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
                button_frame.pack(pady=10)
            except Exception as e:
                _log_exception("Failed to build confirm dialog UI", e)
                ctk.CTkLabel(
                    dialog,
                    text="Dialog error. Please close this window and check ~/.config/bashium/bashium.log",
                    font=ctk.CTkFont(size=13),
                    wraplength=360,
                    justify="left",
                ).pack(pady=20, padx=20)
                ctk.CTkButton(
                    dialog,
                    text="Close",
                    command=dialog.destroy,
                    width=120,
                ).pack(pady=10)
                return

            def confirm():
                dialog.destroy()

                try:
                    self.module.run()
                except Exception as e:
                    _log_exception("Failed to launch script terminal", e)
                    try:
                        err = ctk.CTkToplevel(self)
                        err.title("Execution error")
                        err.geometry("620x260")
                        err.transient(self.master)
                        err.bind("<Escape>", lambda _e: err.destroy())

                        err.update_idletasks()
                        x = (err.winfo_screenwidth() // 2) - (620 // 2)
                        y = (err.winfo_screenheight() // 2) - (260 // 2)
                        err.geometry(f"620x260+{x}+{y}")

                        ctk.CTkLabel(
                            err,
                            text="Could not launch the terminal to run the script.",
                            font=ctk.CTkFont(size=16, weight="bold"),
                        ).pack(pady=(20, 10), padx=20, anchor="w")

                        textbox = ctk.CTkTextbox(err, height=120)
                        textbox.pack(fill="both", expand=True, padx=20, pady=(0, 10))
                        textbox.insert("1.0", str(e))
                        textbox.configure(state="disabled")

                        ctk.CTkButton(
                            err,
                            text="Close",
                            command=err.destroy,
                            width=120,
                        ).pack(pady=(0, 20))
                    except Exception as dialog_err:
                        _log_exception("Failed to show execution error dialog", dialog_err)

            ctk.CTkButton(
                button_frame,
                text="Execute",
                command=confirm,
                fg_color=self.colors["success"],
                hover_color=self.colors["success_hover"],
                width=120
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                fg_color="gray40",
                hover_color="gray30",
                width=120
            ).pack(side="left", padx=5)
        except Exception as e:
            _log_exception("Unhandled error in _run_with_dialog", e)
            return


class BashiumApp:
    PALETTES = {
        "Gruvbox Dark": {
            "bg": "#282828",
            "fg": "#ebdbb2",
            "fg_secondary": "#bdae93",
            "accent": "#fabd2f",
            "accent_hover": "#d79921",
            "card_bg": "#3c3836",
            "border": "#504945",
            "muted": "#7c6f64",
            "success": "#b8bb26",
            "success_hover": "#98971a",
        },
        "Gruvbox Light": {
            "bg": "#fbf1c7",
            "fg": "#3c3836",
            "fg_secondary": "#665c54",
            "accent": "#d79921",
            "accent_hover": "#b57614",
            "card_bg": "#f2e5bc",
            "border": "#d5c4a1",
            "muted": "#7c6f64",
            "success": "#98971a",
            "success_hover": "#79740e",
        },
        "Tokyo Night": {
            "bg": "#1a1b26",
            "fg": "#c0caf5",
            "fg_secondary": "#9aa5ce",
            "accent": "#7aa2f7",
            "accent_hover": "#5a82d7",
            "card_bg": "#24283b",
            "border": "#414868",
            "muted": "#565f89",
            "success": "#9ece6a",
            "success_hover": "#7ea84a",
        },
        "Cyberpunk": {
            "bg": "#0b0f1a",
            "fg": "#e6e6e6",
            "fg_secondary": "#b0b0b0",
            "accent": "#ff2a6d",
            "accent_hover": "#df0a4d",
            "card_bg": "#1b1f36",
            "border": "#2b2f46",
            "muted": "#6b6f86",
            "success": "#05ffa1",
            "success_hover": "#00df81",
        },
        "Neon Cyan": {
            "bg": "#07161b",
            "fg": "#d7f9ff",
            "fg_secondary": "#a0c9d1",
            "accent": "#00f5ff",
            "accent_hover": "#00d5df",
            "card_bg": "#0b2a33",
            "border": "#1b3a43",
            "muted": "#5b7a83",
            "success": "#00ff9f",
            "success_hover": "#00df7f",
        },
    }
    
    def __init__(self, root: ctk.CTk, modules: list[ScriptModule], hw_info: dict):
        self.root = root
        self.modules = modules
        self.hw_info = hw_info
        self.config_path = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "bashium" / "config.json"
        self.module_cards = []
        
        self.setup_window()
        self.setup_ui()
        
        # Załaduj i zastosuj zapisany motyw
        saved_palette = self._load_palette_preset()
        self.palette_var.set(saved_palette)
        self._apply_palette()
    
    def setup_window(self):
        self.root.title("BASHIUM - System Tweaker")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Centrowanie okna
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ BASHIUM",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        self.title_label.pack(side="left")
        
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="System Tweaker & Configuration Tool",
            font=ctk.CTkFont(size=14),
        )
        self.subtitle_label.pack(side="left", padx=(15, 0))
        
        # Theme selector
        self.palette_var = ctk.StringVar()
        theme_menu = ctk.CTkOptionMenu(
            header_frame,
            values=list(self.PALETTES.keys()),
            variable=self.palette_var,
            command=lambda _: self._apply_palette(),
            font=ctk.CTkFont(size=12),
            width=150
        )
        theme_menu.pack(side="right")
        
        # Hardware info panel
        self.hw_panel = ctk.CTkFrame(main_frame, corner_radius=12)
        self.hw_panel.pack(fill="x", pady=(0, 20))
        
        self.hw_title = ctk.CTkLabel(
            self.hw_panel,
            text="🖥️ Hardware Detection",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.hw_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Grid dla info o hardware
        info_grid = ctk.CTkFrame(self.hw_panel, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        hw_items = [
            ("Wi-Fi", self.hw_info.get("wifi_text", "Unknown")),
            ("Bluetooth", self.hw_info.get("bt_text", "Unknown")),
            ("NVIDIA", self.hw_info.get("nvidia_text", "Unknown")),
            ("Repository", self.hw_info.get("nonfree_text", "Unknown")),
            ("USB Devices", self.hw_info.get("usb_text", "Unknown")),
        ]
        
        self.hw_labels = []
        for i, (label, value) in enumerate(hw_items):
            row = i // 2
            col = i % 2
            
            item_frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            item_frame.grid(row=row, column=col, sticky="w", padx=15, pady=5)
            
            label_widget = ctk.CTkLabel(
                item_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            label_widget.pack(side="left")
            
            value_widget = ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=12),
            )
            value_widget.pack(side="left", padx=(5, 0))
            
            self.hw_labels.append((label_widget, value_widget))
        
        # Scrollable frame dla modułów
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent",
            corner_radius=0
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Grid dla kart modułów (2 kolumny)
        for idx, module in enumerate(self.modules):
            row = idx // 2
            col = idx % 2
            
            card = ModuleCard(
                scroll_frame,
                module,
                self._get_current_colors()
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.module_cards.append(card)
        
        # Konfiguracja grid
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)
    
    def _get_current_colors(self) -> dict:
        palette_name = self.palette_var.get()
        return self.PALETTES.get(palette_name, self.PALETTES["Neon Cyan"])
    
    def _apply_palette(self):
        colors = self._get_current_colors()
        
        # Ustaw tryb appearance
        if "Light" in self.palette_var.get():
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
        
        # Zapisz wybór
        self._save_palette_preset(self.palette_var.get())
        
        # Zaktualizuj kolory header
        self.title_label.configure(text_color=colors["fg"])
        self.subtitle_label.configure(text_color=colors["fg_secondary"])
        
        # Zaktualizuj kolory hardware panel
        self.hw_title.configure(text_color=colors["fg"])
        for label_widget, value_widget in self.hw_labels:
            label_widget.configure(text_color=colors["fg"])
            value_widget.configure(text_color=colors["fg_secondary"])
        
        # Zaktualizuj wszystkie karty
        for card in self.module_cards:
            card.colors = colors
            card.configure(
                fg_color=colors["card_bg"],
                border_color=colors["border"]
            )
            if hasattr(card, 'run_button'):
                card.run_button.configure(
                    fg_color=colors["accent"],
                    hover_color=colors["accent_hover"]
                )
            # Zaktualizuj kolory wewnątrz karty
            for widget in card.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    # Sprawdź czy to nie jest status dot
                    if widget.cget("text") == "●":
                        continue
                    widget.configure(text_color=colors["fg"])
                elif isinstance(widget, ctk.CTkFrame):
                    for subwidget in widget.winfo_children():
                        if isinstance(subwidget, ctk.CTkLabel):
                            if subwidget.cget("text") == "●":
                                continue
                            # Header labels (nazwy modułów) - accent color
                            if subwidget.cget("font").cget("weight") == "bold":
                                subwidget.configure(text_color=colors["accent"])
                            else:
                                subwidget.configure(text_color=colors["fg"])
                elif isinstance(widget, ctk.CTkButton):
                    # Ustaw kolor tekstu przycisku - czarny dla aktywnych, ciemno-szary dla nieaktywnych
                    is_enabled = str(widget.cget("state")) == "normal"
                    widget.configure(text_color="#000000" if is_enabled else "#404040")
    
    def _load_palette_preset(self) -> str:
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                preset = data.get("palette_preset")
                if preset in self.PALETTES:
                    return preset
        except Exception:
            pass
        return "Neon Cyan"
    
    def _save_palette_preset(self, preset: str):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"palette_preset": preset}
            self.config_path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass


def main():
    base_dir = Path(__file__).parent.resolve()

    nvidia_detected = detect_nvidia_gpu()
    bt_detected = detect_bluetooth_controller()
    wifi_vendors = detect_wifi_vendors()
    nonfree_enabled = has_nonfree_enabled()
    usb_summary = detect_usb_devices_summary()

    wifi_desc = "None detected" if not wifi_vendors else "Detected: " + ", ".join(sorted(wifi_vendors))
    nvidia_desc = "Detected" if nvidia_detected else "Not detected"
    bt_desc = "Detected" if bt_detected else "Not detected"
    nonfree_desc = "Enabled" if nonfree_enabled else "Not enabled"

    hw_info = {
        "wifi_text": wifi_desc,
        "bt_text": bt_desc,
        "nvidia_text": nvidia_desc,
        "nonfree_text": nonfree_desc,
        "usb_text": usb_summary,
    }

    nvidia_module_desc = "Detected NVIDIA GPU. Configure drivers and settings." if nvidia_detected else "No NVIDIA GPU detected on this system."
    firmware_desc = f"Auto-detect and install firmware for detected hardware. {wifi_desc}"
    bluetooth_desc = f"Install and configure Bluetooth tools. {bt_desc}"

    modules = [
        ScriptModule("Configuration", base_dir / "configuration", CONFIG_DESCRIPTION),
        ScriptModule("Firmware", base_dir / "configuration" / "firmware.sh", firmware_desc, enabled=bool(wifi_vendors)),
        ScriptModule("Bluetooth", base_dir / "configuration" / "bluetooth.sh", bluetooth_desc, enabled=bt_detected),
        ScriptModule("NVIDIA", base_dir / "configuration" / "nvidia.sh", nvidia_module_desc, enabled=nvidia_detected),
        ScriptModule("Xfce Look", base_dir / "xfce_look", XFCE_LOOK_DESCRIPTION),
        ScriptModule("Software", base_dir / "software", SOFTWARE_DESCRIPTION),
    ]

    root = ctk.CTk()
    app = BashiumApp(root, modules, hw_info=hw_info)
    root.mainloop()


if __name__ == "__main__":
    main()
