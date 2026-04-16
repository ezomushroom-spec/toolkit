import os
import re
import shutil
from typing import List, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD

from app.core.shortcut_launcher import ShortcutLauncher
from app.models import Group, MajorTab, MinorTab, Shortcut
from app.ui.theme import get_theme
from app.utils.path_utils import get_asset_path


class LauncherApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, config_manager):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.config_manager = config_manager
        self.theme = get_theme(self.config_manager.theme_name)
        ctk.set_appearance_mode(self.theme["appearance_mode"])
        ctk.set_default_color_theme(self.theme["color_theme"])

        self.current_major_tab: Optional[MajorTab] = None
        self.current_minor_tab: Optional[MinorTab] = None
        self.search_results: List[Shortcut] = []
        self.is_visible = False
        self.hotkey_service = None
        self.tray_service = None

        self.launcher = ShortcutLauncher(
            on_launch_success=self._on_launch_success,
            on_launch_error=self._on_launch_error,
        )

        self._setup_window()
        self._build_ui()
        self._load_initial_state()

    def attach_runtime_services(self, hotkey_service, tray_service) -> None:
        self.hotkey_service = hotkey_service
        self.tray_service = tray_service

    def _setup_window(self) -> None:
        self.title("Launcher V2 Remake")
        icon_path = get_asset_path("icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        try:
            self.geometry(self.config_manager.window_geometry)
            if self.config_manager.window_position:
                self.geometry(f"+{self.config_manager.window_position}")
        except Exception:
            self.geometry("1100x720")
        self.minsize(920, 580)
        self.configure(fg_color=self.theme["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_configure)

    def _build_ui(self) -> None:
        self.header = ctk.CTkFrame(self, fg_color=self.theme["bg_secondary"], corner_radius=12)
        self.header.pack(fill="x", padx=12, pady=(12, 8))

        self.search_entry = ctk.CTkEntry(self.header, placeholder_text="検索して Enter で起動", height=38)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=12)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._launch_first_search_result)

        self.theme_button = ctk.CTkButton(self.header, text="テーマ", width=72, command=self._toggle_theme)
        self.theme_button.pack(side="right", padx=(0, 12), pady=12)

        self.menu_button = ctk.CTkButton(self.header, text="メニュー", width=88, command=self._show_menu)
        self.menu_button.pack(side="right", padx=(0, 8), pady=12)

        self.search_popup = ctk.CTkFrame(self, fg_color=self.theme["bg_secondary"], corner_radius=10)
        self.search_popup.place_forget()

        self.major_frame = self._create_bar_section("大タブ")
        self.major_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.minor_frame = self._create_bar_section("小タブ")
        self.minor_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.content_frame = ctk.CTkFrame(self, fg_color=self.theme["bg_secondary"], corner_radius=12)
        self.content_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        content_header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        content_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        self.content_title = ctk.CTkLabel(content_header, text="ショートカット", font=ctk.CTkFont(size=18, weight="bold"))
        self.content_title.pack(side="left")

        self.content_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self, text="", anchor="w", text_color=self.theme["text_secondary"])
        self.status_label.pack(fill="x", padx=16, pady=(0, 10))

    def _create_bar_section(self, title: str):
        frame = ctk.CTkFrame(self, fg_color=self.theme["bg_secondary"], corner_radius=12)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        list_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent", orientation="horizontal", height=52)
        list_frame.pack(fill="x", padx=10, pady=(0, 8))

        action_frame = ctk.CTkFrame(header, fg_color="transparent")
        action_frame.pack(side="right")

        frame.list_frame = list_frame
        frame.action_frame = action_frame
        return frame

    def _load_initial_state(self) -> None:
        if self.config_manager.major_tabs:
            self.current_major_tab = self.config_manager.major_tabs[0]
            if self.current_major_tab.minor_tabs:
                self.current_minor_tab = self.current_major_tab.minor_tabs[0]
        self._refresh_major_tabs()
        self._refresh_minor_tabs()
        self._refresh_content()
        self._update_status()

    def _refresh_major_tabs(self) -> None:
        self._clear_container(self.major_frame.list_frame)
        self._clear_container(self.major_frame.action_frame)
        for tab in self.config_manager.major_tabs:
            self._create_tab_row(
                self.major_frame.list_frame,
                tab.name,
                self.current_major_tab and tab.id == self.current_major_tab.id,
                lambda current=tab: self._select_major_tab(current),
                lambda current=tab: self._rename_major_tab(current.id),
                lambda current=tab: self._move_major_tab(current.id, -1),
                lambda current=tab: self._move_major_tab(current.id, 1),
                lambda current=tab: self._delete_major_tab(current.id),
                compact=False,
            )
        ctk.CTkButton(self.major_frame.action_frame, text="+", width=28, height=28, command=self._add_major_tab).pack(side="right")

    def _refresh_minor_tabs(self) -> None:
        self._clear_container(self.minor_frame.list_frame)
        self._clear_container(self.minor_frame.action_frame)
        if not self.current_major_tab:
            return
        for tab in self.current_major_tab.minor_tabs:
            self._create_tab_row(
                self.minor_frame.list_frame,
                tab.name,
                self.current_minor_tab and tab.id == self.current_minor_tab.id,
                lambda current=tab: self._select_minor_tab(current),
                lambda current=tab: self._rename_minor_tab(current.id),
                lambda current=tab: self._move_minor_tab(current.id, -1),
                lambda current=tab: self._move_minor_tab(current.id, 1),
                lambda current=tab: self._delete_minor_tab(current.id),
                compact=True,
            )
        ctk.CTkButton(self.minor_frame.action_frame, text="+", width=28, height=28, command=self._add_minor_tab).pack(side="right")

    def _create_tab_row(self, parent, label, selected, on_select, on_rename, on_left, on_right, on_delete, compact: bool = False) -> None:
        row = ctk.CTkFrame(parent, fg_color=self.theme["bg_tertiary"] if selected else self.theme["bg_primary"])
        row.pack(side="left", padx=(10 if compact else 0, 6), pady=2)
        ctk.CTkButton(
            row,
            text=label,
            anchor="w",
            fg_color="transparent",
            height=30,
            width=140 if not compact else 120,
            command=on_select,
        ).pack(side="left", padx=(6, 0), pady=3)
        ctk.CTkButton(row, text="←", width=24, height=26, command=on_left).pack(side="left", padx=1)
        ctk.CTkButton(row, text="→", width=24, height=26, command=on_right).pack(side="left", padx=1)
        ctk.CTkButton(row, text="名", width=24, height=26, command=on_rename).pack(side="left", padx=1)
        ctk.CTkButton(row, text="削", width=24, height=26, fg_color=self.theme["danger"], hover_color="#a44444", command=on_delete).pack(side="left", padx=(1, 5))

    def _refresh_content(self) -> None:
        self._clear_container(self.content_scroll)
        if not self.current_minor_tab:
            ctk.CTkLabel(self.content_scroll, text="小タブを作成してください", text_color=self.theme["text_secondary"]).pack(pady=40)
            return

        self.content_title.configure(text=f"{self.current_minor_tab.name} のショートカット")
        for group in self.current_minor_tab.groups:
            self._create_group_panel(group)

        ctk.CTkButton(self.content_scroll, text="+ グループ追加", command=self._add_group).pack(anchor="w", pady=(8, 0))

    def _create_group_panel(self, group: Group) -> None:
        panel = ctk.CTkFrame(self.content_scroll, fg_color=self.theme["bg_primary"], corner_radius=12)
        panel.pack(fill="x", pady=5)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 6))

        collapsed = self.config_manager.is_group_collapsed(group.id)
        arrow = "▶" if collapsed else "▼"
        ctk.CTkButton(
            header,
            text=f"{arrow} {group.name} ({len(group.shortcuts)})",
            anchor="w",
            fg_color="transparent",
            command=lambda current=group: self._toggle_group(current.id),
        ).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(header, text="+", width=28, height=28, command=lambda current=group: self._add_shortcut(current.id)).pack(side="left", padx=2)
        ctk.CTkButton(header, text="名", width=28, height=28, command=lambda current=group: self._rename_group(current.id)).pack(side="left", padx=2)
        ctk.CTkButton(header, text="↑", width=28, height=28, command=lambda current=group: self._move_group(current.id, -1)).pack(side="left", padx=2)
        ctk.CTkButton(header, text="↓", width=28, height=28, command=lambda current=group: self._move_group(current.id, 1)).pack(side="left", padx=2)
        ctk.CTkButton(header, text="削", width=28, height=28, fg_color=self.theme["danger"], hover_color="#a44444", command=lambda current=group: self._delete_group(current.id)).pack(side="left", padx=(2, 0))

        if collapsed:
            return

        body = ctk.CTkFrame(panel, fg_color="transparent")
        body.pack(fill="x", padx=10, pady=(0, 10))

        try:
            body.drop_target_register(DND_FILES)
            body.dnd_bind("<<Drop>>", lambda event, current=group: self._handle_drop(event, current.id))
        except Exception:
            pass

        if not group.shortcuts:
            ctk.CTkLabel(body, text="ファイルをドロップして追加", text_color=self.theme["text_secondary"]).pack(anchor="w", padx=8, pady=(0, 8))
            return

        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x")
        for column in range(4):
            grid.grid_columnconfigure(column, weight=1)

        for index, shortcut in enumerate(group.shortcuts):
            row = index // 4
            column = index % 4
            card = self._create_shortcut_row(grid, group.id, shortcut)
            card.grid(row=row, column=column, sticky="nsew", padx=3, pady=3)

    def _create_shortcut_row(self, parent, group_id: str, shortcut: Shortcut) -> None:
        row = ctk.CTkFrame(parent, fg_color=self.theme["bg_tertiary"], corner_radius=12)
        row.configure(border_width=1, border_color=self.theme["bg_secondary"], width=168, height=110)
        row.grid_propagate(False)

        header = ctk.CTkFrame(row, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 2))

        app_mark = self._shortcut_mark(shortcut)
        ctk.CTkLabel(
            header,
            text=app_mark,
            width=24,
            height=24,
            corner_radius=7,
            fg_color=self.theme["accent"],
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left")

        title = f"{'📌 ' if self.config_manager.is_pinned(shortcut.id) else ''}{shortcut.name}"
        ctk.CTkLabel(
            header,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        ctk.CTkLabel(
            row,
            text=self._format_path(shortcut.path),
            anchor="w",
            justify="left",
            wraplength=148,
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=10),
        ).pack(fill="x", padx=8)

        meta = ctk.CTkFrame(row, fg_color="transparent")
        meta.pack(fill="x", padx=8, pady=(4, 2))
        ctk.CTkLabel(
            meta,
            text=self._shortcut_type_label(shortcut),
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=9),
        ).pack(side="left")
        ctk.CTkLabel(
            meta,
            text=os.path.basename(os.path.dirname(shortcut.path)) or "-",
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=9),
        ).pack(side="right")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=(2, 6))
        ctk.CTkButton(actions, text="起動", width=44, height=24, command=lambda current=shortcut: self._launch_shortcut(current)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="管", width=26, height=24, command=lambda current=shortcut: self._launch_shortcut(current, as_admin=True)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="📌", width=26, height=24, command=lambda current=shortcut: self._toggle_pin(current.id)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="↑", width=22, height=24, command=lambda current=shortcut: self._move_shortcut(group_id, current.id, -1)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="↓", width=22, height=24, command=lambda current=shortcut: self._move_shortcut(group_id, current.id, 1)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="名", width=22, height=24, command=lambda current=shortcut: self._rename_shortcut(group_id, current.id)).pack(side="left", padx=1)
        ctk.CTkButton(actions, text="削", width=22, height=24, fg_color=self.theme["danger"], hover_color="#a44444", command=lambda current=shortcut: self._delete_shortcut(group_id, current.id)).pack(side="left", padx=1)
        return row

    def _on_search_change(self, event=None) -> None:
        query = self.search_entry.get().strip().lower()
        self.search_results = []
        if not query:
            self.search_popup.place_forget()
            return
        for _, _, _, shortcut in self.config_manager.find_all_shortcuts():
            if query in shortcut.name.lower() or query in shortcut.path.lower():
                self.search_results.append(shortcut)
            if len(self.search_results) >= 8:
                break
        self._render_search_popup()

    def _render_search_popup(self) -> None:
        self._clear_container(self.search_popup)
        if not self.search_results:
            self.search_popup.place_forget()
            return
        for shortcut in self.search_results:
            ctk.CTkButton(
                self.search_popup,
                text=shortcut.name,
                anchor="w",
                fg_color="transparent",
                command=lambda current=shortcut: self._launch_search_result(current),
            ).pack(fill="x", padx=4, pady=2)
        self.update_idletasks()
        x = self.search_entry.winfo_rootx() - self.winfo_rootx()
        y = self.search_entry.winfo_rooty() - self.winfo_rooty() + self.search_entry.winfo_height() + 6
        self.search_popup.place(x=x, y=y, width=self.search_entry.winfo_width())

    def _launch_first_search_result(self, event=None) -> None:
        if self.search_results:
            self._launch_search_result(self.search_results[0])

    def _launch_search_result(self, shortcut: Shortcut) -> None:
        self.search_entry.delete(0, "end")
        self.search_popup.place_forget()
        self._launch_shortcut(shortcut)

    def _select_major_tab(self, tab: MajorTab) -> None:
        self.current_major_tab = tab
        self.current_minor_tab = tab.minor_tabs[0] if tab.minor_tabs else None
        self._refresh_major_tabs()
        self._refresh_minor_tabs()
        self._refresh_content()

    def _select_minor_tab(self, tab: MinorTab) -> None:
        self.current_minor_tab = tab
        self._refresh_minor_tabs()
        self._refresh_content()

    def _add_major_tab(self) -> None:
        name = simpledialog.askstring("新規大タブ", "大タブ名を入力:")
        if not name:
            return
        tab = MajorTab(name=name)
        self.config_manager.add_major_tab(tab)
        self._select_major_tab(tab)

    def _rename_major_tab(self, tab_id: str) -> None:
        tab = next((item for item in self.config_manager.major_tabs if item.id == tab_id), None)
        if not tab:
            return
        name = simpledialog.askstring("名前変更", "新しい大タブ名:", initialvalue=tab.name)
        if name:
            tab.name = name
            self.config_manager.save_config()
            self._refresh_major_tabs()

    def _delete_major_tab(self, tab_id: str) -> None:
        if not messagebox.askyesno("確認", "大タブを削除しますか？"):
            return
        self.config_manager.remove_major_tab(tab_id)
        self.current_major_tab = self.config_manager.major_tabs[0] if self.config_manager.major_tabs else None
        self.current_minor_tab = self.current_major_tab.minor_tabs[0] if self.current_major_tab and self.current_major_tab.minor_tabs else None
        self._refresh_major_tabs()
        self._refresh_minor_tabs()
        self._refresh_content()

    def _move_major_tab(self, tab_id: str, direction: int) -> None:
        self.config_manager.move_major_tab(tab_id, direction)
        self._refresh_major_tabs()

    def _add_minor_tab(self) -> None:
        if not self.current_major_tab:
            return
        name = simpledialog.askstring("新規小タブ", "小タブ名を入力:")
        if not name:
            return
        tab = MinorTab(name=name)
        self.current_major_tab.add_minor_tab(tab)
        self.config_manager.save_config()
        self._select_minor_tab(tab)

    def _rename_minor_tab(self, tab_id: str) -> None:
        if not self.current_major_tab:
            return
        tab = next((item for item in self.current_major_tab.minor_tabs if item.id == tab_id), None)
        if not tab:
            return
        name = simpledialog.askstring("名前変更", "新しい小タブ名:", initialvalue=tab.name)
        if name:
            tab.name = name
            self.config_manager.save_config()
            self._refresh_minor_tabs()
            self._refresh_content()

    def _delete_minor_tab(self, tab_id: str) -> None:
        if not self.current_major_tab or not messagebox.askyesno("確認", "小タブを削除しますか？"):
            return
        self.current_major_tab.remove_minor_tab(tab_id)
        self.config_manager.save_config()
        self.current_minor_tab = self.current_major_tab.minor_tabs[0] if self.current_major_tab.minor_tabs else None
        self._refresh_minor_tabs()
        self._refresh_content()

    def _move_minor_tab(self, tab_id: str, direction: int) -> None:
        if not self.current_major_tab:
            return
        self.current_major_tab.move_minor_tab(tab_id, direction)
        self.config_manager.save_config()
        self._refresh_minor_tabs()

    def _add_group(self) -> None:
        if not self.current_minor_tab:
            return
        name = simpledialog.askstring("新規グループ", "グループ名を入力:")
        if not name:
            return
        self.current_minor_tab.add_group(Group(name=name))
        self.config_manager.save_config()
        self._refresh_content()

    def _rename_group(self, group_id: str) -> None:
        group = self._find_group(group_id)
        if not group:
            return
        name = simpledialog.askstring("グループ名変更", "新しいグループ名:", initialvalue=group.name)
        if name:
            group.name = name
            self.config_manager.save_config()
            self._refresh_content()

    def _delete_group(self, group_id: str) -> None:
        if not self.current_minor_tab or not messagebox.askyesno("確認", "グループを削除しますか？"):
            return
        self.current_minor_tab.remove_group(group_id)
        self.config_manager.save_config()
        self._refresh_content()

    def _move_group(self, group_id: str, direction: int) -> None:
        if not self.current_minor_tab:
            return
        self.current_minor_tab.move_group(group_id, direction)
        self.config_manager.save_config()
        self._refresh_content()

    def _toggle_group(self, group_id: str) -> None:
        self.config_manager.set_group_collapsed(group_id, not self.config_manager.is_group_collapsed(group_id))
        self._refresh_content()

    def _add_shortcut(self, group_id: str) -> None:
        path = filedialog.askopenfilename(title="ファイルを選択")
        if path:
            self._append_shortcut(group_id, path)

    def _append_shortcut(self, group_id: str, path: str) -> None:
        group = self._find_group(group_id)
        if not group:
            return
        name = os.path.basename(path) or path
        group.add_shortcut(Shortcut(name=name, path=path, type=self._detect_shortcut_type(path)))
        self.config_manager.save_config()
        self._refresh_content()
        self._update_status()

    def _rename_shortcut(self, group_id: str, shortcut_id: str) -> None:
        shortcut = self._find_shortcut(group_id, shortcut_id)
        if not shortcut:
            return
        name = simpledialog.askstring("名前変更", "新しいショートカット名:", initialvalue=shortcut.name)
        if name:
            shortcut.name = name
            self.config_manager.save_config()
            self._refresh_content()

    def _delete_shortcut(self, group_id: str, shortcut_id: str) -> None:
        if not messagebox.askyesno("確認", "ショートカットを削除しますか？"):
            return
        group = self._find_group(group_id)
        if not group:
            return
        group.remove_shortcut(shortcut_id)
        self.config_manager.save_config()
        self._refresh_content()
        self._update_status()

    def _move_shortcut(self, group_id: str, shortcut_id: str, direction: int) -> None:
        group = self._find_group(group_id)
        if not group:
            return
        group.move_shortcut(shortcut_id, direction)
        self.config_manager.save_config()
        self._refresh_content()

    def _toggle_pin(self, shortcut_id: str) -> None:
        self.config_manager.toggle_pin(shortcut_id)
        self._refresh_content()

    def _launch_shortcut(self, shortcut: Shortcut, as_admin: bool = False) -> None:
        self.launcher.launch(shortcut, as_admin=as_admin)

    def _on_launch_success(self, shortcut: Shortcut) -> None:
        self.config_manager.add_recent_app(shortcut.path, shortcut.name)
        self.config_manager.increment_usage(shortcut.id)
        self._update_status(f"{shortcut.name} を起動しました")

    def _on_launch_error(self, shortcut: Shortcut, message: str) -> None:
        messagebox.showerror("起動エラー", f"{shortcut.name}: {message}")

    def _show_menu(self) -> None:
        menu = ctk.CTkToplevel(self)
        menu.title("メニュー")
        menu.geometry("320x340")
        menu.transient(self)
        menu.grab_set()

        ctk.CTkLabel(menu, text="最近使用したアプリ", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(12, 6))
        recent_frame = ctk.CTkScrollableFrame(menu, height=160)
        recent_frame.pack(fill="both", expand=True, padx=12)
        for item in self.config_manager.recent_apps[:5]:
            shortcut = Shortcut(name=item["name"], path=item["path"], type=self._detect_shortcut_type(item["path"]))
            ctk.CTkButton(
                recent_frame,
                text=item["name"],
                anchor="w",
                command=lambda current=shortcut: [menu.destroy(), self._launch_shortcut(current)],
            ).pack(fill="x", pady=3)

        actions = ctk.CTkFrame(menu, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(actions, text="設定をエクスポート", command=lambda: self._export_config(menu)).pack(fill="x", pady=4)
        ctk.CTkButton(actions, text="設定をインポート", command=lambda: self._import_config(menu)).pack(fill="x", pady=4)
        ctk.CTkButton(actions, text="終了", fg_color=self.theme["danger"], hover_color="#a44444", command=lambda: [menu.destroy(), self.quit_app()]).pack(fill="x", pady=4)

    def _export_config(self, menu) -> None:
        menu.destroy()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if path:
            shutil.copy2(self.config_manager.config_file, path)
            messagebox.showinfo("完了", "設定をエクスポートしました")

    def _import_config(self, menu) -> None:
        menu.destroy()
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        if not messagebox.askyesno("確認", "現在の設定を上書きしますか？"):
            return
        backup = self.config_manager.config_file.with_suffix(".backup.json")
        if self.config_manager.config_file.exists():
            shutil.copy2(self.config_manager.config_file, backup)
        shutil.copy2(path, self.config_manager.config_file)
        messagebox.showinfo("完了", f"設定をインポートしました。\nバックアップ: {backup.name}\n再起動してください。")

    def _toggle_theme(self) -> None:
        self.config_manager.theme_name = "light" if self.config_manager.theme_name == "dark" else "dark"
        self.config_manager.save_config()
        messagebox.showinfo("テーマ変更", "テーマを保存しました。次回起動時に反映されます。")

    def _handle_drop(self, event, group_id: str) -> None:
        for path in self._parse_drop_paths(event.data):
            self._append_shortcut(group_id, path)

    def _parse_drop_paths(self, data: str) -> List[str]:
        matches = re.findall(r"\{([^}]+)\}|(\S+)", data)
        paths = []
        for left, right in matches:
            path = left or right
            if path:
                paths.append(path)
        return paths

    def _on_configure(self, event) -> None:
        if event.widget != self:
            return
        if hasattr(self, "_configure_after_id"):
            self.after_cancel(self._configure_after_id)
        self._configure_after_id = self.after(400, self._save_geometry)

    def _save_geometry(self) -> None:
        match = re.match(r"(\d+x\d+)([+-]\d+[+-]\d+)?", self.geometry())
        if not match:
            return
        self.config_manager.window_geometry = match.group(1)
        if match.group(2):
            self.config_manager.window_position = match.group(2).lstrip("+")
        self.config_manager.save_config()

    def _on_close(self) -> None:
        self.config_manager.shutdown()
        self.withdraw()
        self.is_visible = False

    def show_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        self.is_visible = True

    def hide_window(self) -> None:
        self.withdraw()
        self.is_visible = False

    def toggle_visibility(self) -> None:
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def quit_app(self) -> None:
        self.config_manager.shutdown()
        self.destroy()

    def _find_group(self, group_id: str) -> Optional[Group]:
        if not self.current_minor_tab:
            return None
        return next((group for group in self.current_minor_tab.groups if group.id == group_id), None)

    def _find_shortcut(self, group_id: str, shortcut_id: str) -> Optional[Shortcut]:
        group = self._find_group(group_id)
        if not group:
            return None
        return next((shortcut for shortcut in group.shortcuts if shortcut.id == shortcut_id), None)

    def _detect_shortcut_type(self, path: str) -> str:
        if os.path.isdir(path):
            return "folder"
        if path.lower().endswith((".exe", ".lnk", ".bat", ".cmd")):
            return "application"
        return "file"

    def _format_path(self, path: str) -> str:
        normalized = path.replace("/", os.sep)
        if len(normalized) <= 22:
            return normalized
        head = normalized[:10]
        tail = normalized[-9:]
        return f"{head}...{tail}"

    def _shortcut_mark(self, shortcut: Shortcut) -> str:
        name = shortcut.name.strip()
        if not name:
            return "?"
        return name[0].upper()

    def _shortcut_type_label(self, shortcut: Shortcut) -> str:
        if shortcut.type == "folder":
            return "FOLDER"
        if shortcut.type == "application":
            return "APP"
        return "FILE"

    def _update_status(self, message: Optional[str] = None) -> None:
        total = sum(len(group.shortcuts) for tab in self.config_manager.major_tabs for minor in tab.minor_tabs for group in minor.groups)
        if message:
            self.status_label.configure(text=f"{message} | 合計 {total} 件")
        else:
            self.status_label.configure(text=f"合計 {total} 件 | 設定: {self.config_manager.config_file}")

    def _clear_container(self, widget) -> None:
        for child in widget.winfo_children():
            child.destroy()
