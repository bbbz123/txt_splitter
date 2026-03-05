# TXT Splitter GUI Module
# Specialized for bbbz123 - Multi-language & Batch Processing Enhancement
import customtkinter as ctk # type: ignore
from tkinterdnd2 import TkinterDnD, DND_FILES # type: ignore
import os
import re
import threading
from tkinter import filedialog, messagebox, ttk
from collections import Counter

from core.parser import TextParser  # type: ignore[import]
from core.patterns import get_language, get_all_languages, detect_language, build_regexes_from_tokens  # type: ignore[import]
from core.document_loader import SUPPORTED_INPUT_EXTS  # type: ignore[import]
from core.mode_utils import is_chapter_mode, is_constraint_mode, is_line_mode, is_paragraph_mode, is_word_mode  # type: ignore[import]
from core.split_service import SplitService  # type: ignore[import]
from gui.per_file_settings import PerFileSettingsWindow
from typing import Optional, List, Dict, Any

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        
    def enter(self, event=None):
        self.schedule()
        
    def leave(self, event=None):
        self.unschedule()
        self.hide_tooltip()
        
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(800, self.show_tooltip)
        
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
            
    def show_tooltip(self, event=None):
        self.unschedule()
        if self.tooltip_window or not self.text:
            return
            
        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 15
        
        self.tooltip_window = ctk.CTkToplevel(self.widget)  # type: ignore[assignment]
        self.tooltip_window.wm_overrideredirect(True)  # type: ignore[union-attr]
        self.tooltip_window.wm_geometry(f"+{x}+{y}")  # type: ignore[union-attr]
        self.tooltip_window.attributes("-topmost", True)  # type: ignore[union-attr]
        
        label = ctk.CTkLabel(
            self.tooltip_window, 
            text=self.text, 
            fg_color=("gray85", "gray25"), 
            corner_radius=4, 
            text_color=("black", "white"),
            padx=10, pady=5,
            justify="left",
            font=ctk.CTkFont(size=12)
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()  # type: ignore[union-attr]
            self.tooltip_window = None

class GUI(ctk.CTk, TkinterDnD.DnDWrapper): # type: ignore
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("TXT Splitter (by bbbz123)")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Internal state
        self.parser = TextParser()
        self.split_service = SplitService(self.parser)
        self.selected_files: List[str] = []
        self.output_dir: Optional[str] = None
        self.parsed_chapters: Dict[str, Any] = {}
        self.file_encoding: Optional[str] = None
        self.file_settings: Dict[str, Dict[str, Any]] = {}
        self.file_count_var = ctk.StringVar(value="未选择文件")
        self.status_var = ctk.StringVar(value="就绪")
        
        # Configure layout (2 rows)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_action_frame()
        self._build_main_frame()
        
    def _build_main_frame(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        
        # 2 columns in main frame: Settings (Left) | Preview (Right)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # ---- Left Panel: Settings ----
        settings_panel = ctk.CTkFrame(main_frame, fg_color="transparent")
        settings_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # File Drop/Select Area
        self.file_var = ctk.StringVar(value="拖拽文件到此处或点击选择")
        self.file_btn = ctk.CTkButton(
            settings_panel,
            textvariable=self.file_var,
            height=60,
            command=self.select_file
        )
        self.file_btn.pack(fill="x", pady=(0, 6))
        self.file_btn.drop_target_register(DND_FILES)
        self.file_btn.dnd_bind('<<Drop>>', self.handle_drop)
        ToolTip(
            self.file_btn,
            "选择输入文件，或直接拖拽到这里。\n支持: txt, epub, docx, mobi, azw3, 部分 pdf。",
        )

        file_meta_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        file_meta_frame.pack(fill="x", pady=(0, 10))
        self.file_count_label = ctk.CTkLabel(file_meta_frame, textvariable=self.file_count_var, text_color="gray")
        self.file_count_label.pack(side="left")
        self.clear_files_btn = ctk.CTkButton(file_meta_frame, text="清空", width=70, command=self.clear_files)
        self.clear_files_btn.pack(side="right")
        ToolTip(self.clear_files_btn, "清空当前选择并重置预览。")

        fmt_label = ctk.CTkLabel(
            settings_panel,
            text="支持格式: txt / epub / docx / mobi / azw3 / pdf(部分)",
            text_color="gray",
        )
        fmt_label.pack(anchor="w", pady=(0, 12))

        # Individual Settings Button (Hidden by default)
        self.indiv_settings_btn = ctk.CTkButton(
            settings_panel, 
            text="⚙️ 单独设置选中的文件", 
            fg_color="#F57C00", hover_color="#EF6C00",
            command=self.open_per_file_settings
        )
        # Pack the button initially to register it, then hide it
        self.indiv_settings_btn.pack(fill="x", pady=(0, 10), after=self.file_btn)
        self.indiv_settings_btn.pack_forget()
        
        # Language Selector (Moved above Output Dir)
        lang_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        lang_frame.pack(fill="x", pady=(0, 20))
        lbl_lang = ctk.CTkLabel(lang_frame, text="语言:")
        lbl_lang.pack(side="left")
        ToolTip(lbl_lang, "选择文本的主要语言。⚡ Auto 会自动检测。\nSelect the primary language of the text.\n🌐 Multi-Language 专门处理双语/多语文件。")
        lang_options = ["⚡ Auto 自动检测", "🌐 Multi-Language 双语/多语"] + [lp.display_name for lp in get_all_languages()]
        self.lang_combo = ctk.CTkOptionMenu(lang_frame, values=lang_options, width=170)
        self.lang_combo.pack(side="right")
        self.lang_combo.set("⚡ Auto 自动检测")
        ToolTip(self.lang_combo, "选择文本的主要语言。⚡ Auto 会自动检测。\n🌐 Multi-Language 专门处理双语/多语文件。")
        
        # Output Dir Selection
        ctk.CTkLabel(settings_panel, text="输出目录:").pack(anchor="w")
        
        out_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        out_frame.pack(fill="x", pady=(0, 20))
        self.out_var = ctk.StringVar(value="未选择")
        self.output_entry = ctk.CTkEntry(out_frame, textvariable=self.out_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ToolTip(self.output_entry, "指定切割后小文件的存放目录。如果留空，默认会在源文件同目录下创建一个同名文件夹。")
        self.out_browse_btn = ctk.CTkButton(out_frame, text="浏览...", width=60, command=self.select_output_dir)
        self.out_browse_btn.pack(side="right")
        ToolTip(self.out_browse_btn, "点击选择一个本地文件夹作为输出目的地。")
        
        # Output Structure Strategy
        mode_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 20))
        lbl_mode = ctk.CTkLabel(mode_frame, text="切割模式:")
        lbl_mode.pack(side="left")
        ToolTip(lbl_mode, "选择按照小说的原生结构切割，还是强行按照客观的字数、大小进行无情切割。")
        self.output_mode_combo = ctk.CTkOptionMenu(
            mode_frame, 
            values=["📜 智能章节模式",
                    "🗂️ 按文件大小 (KB)",
                    "📝 按字数切分",
                    "📄 按行数切分",
                    "📑 按段落切分"],
            width=170,
            command=self.on_mode_change
        )
        self.output_mode_combo.pack(side="right")
        self.output_mode_combo.set("📜 智能章节模式")
        
        # Strategy Frame (Only for Regex Chapters) - Segmented Button (Slider)
        self.strategy_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        lbl_strat = ctk.CTkLabel(self.strategy_frame, text="保存策略:", width=60)
        lbl_strat.pack(side="left")
        ToolTip(lbl_strat, "改变输出文件的文件夹树状层级结构。\nFlat: 所有独立的小文件都平铺在同一目录下\nNested: 根据小说内部的卷、章等级别嵌套文件夹")
        self.strategy_var = ctk.StringVar(value="Flat 同级输出")
        self.strategy_combo = ctk.CTkOptionMenu(
            self.strategy_frame,
            variable=self.strategy_var,
            values=[
                "Flat 同级输出",
                "Nested/1 按卷建层",
                "Nested/2 按卷→章建层",
                "Nested/全部 全层级嵌套"
            ],
            width=180,
            command=self._on_strategy_change
        )
        self.strategy_combo.pack(side="right", padx=(10, 0))
        ToolTip(self.strategy_combo, "Flat: 平铺输出\nNested: 按照小说内部的篇、卷、章等级别嵌套文件夹")
        self.strategy_frame.pack(fill="x", pady=(0, 10))
        
        # Constraint Limit Setting (Hidden by default)
        self.constraint_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        
        # Comparator dropdown (how to apply the limit)
        self.constraint_comparator_var = ctk.StringVar(value="≈ 约等于")
        self.constraint_comparator_combo = ctk.CTkOptionMenu(
            self.constraint_frame, 
            values=["≈ 约等于", "= 等于", "> 大于", "≥ 大于等于", "< 小于", "≤ 小于等于"],
            variable=self.constraint_comparator_var,
            width=110,
            command=self._sync_break_by_comparator
        )
        self.constraint_comparator_combo.pack(side="left")
        ToolTip(self.constraint_comparator_combo, "选择切割约束的比较方式：\n≈ 约等于：每块尽量接近该限制值\n= 等于：每块严格等于限制值\n> / ≥：超过限制时才切割\n< / ≤：低于限制时才切割")
        
        lbl_limit = ctk.CTkLabel(self.constraint_frame, text="限制:", width=35)
        lbl_limit.pack(side="left", padx=(5, 0))
        self.constraint_limit_var = ctk.StringVar(value="500")
        self.constraint_limit_entry = ctk.CTkEntry(self.constraint_frame, textvariable=self.constraint_limit_var, width=80)
        self.constraint_limit_entry.pack(side="left", padx=(5, 0))
        ToolTip(self.constraint_limit_entry, "输入拆分的限制数量，如限制1000行切一次。")
        
        self.struct_container = ctk.CTkFrame(settings_panel, fg_color="transparent")
        self.struct_container.pack(fill="x", pady=(0, 10))
        
        lbl_str = ctk.CTkLabel(self.struct_container, text="章节层级结构 (篇/章/节):")
        lbl_str.pack(anchor="w")
        ToolTip(lbl_str, "输入多级结构关键字，用逗号分隔（如: 篇,卷,章,节）。\n右侧的“自动分析”按钮可以扫描文本自动推断合适的层级。")
        
        struct_frame = ctk.CTkFrame(self.struct_container, fg_color="transparent")
        struct_frame.pack(fill="x")
        
        self.structure_var = ctk.StringVar(value="章")
        self.structure_entry = ctk.CTkEntry(struct_frame, textvariable=self.structure_var)
        self.structure_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.analyze_btn = ctk.CTkButton(struct_frame, text="自动分析", width=60, command=self.auto_analyze_structure)
        self.analyze_btn.pack(side="right")
        ToolTip(self.analyze_btn, "智能分析当前书稿，自动识别“卷”、“章”、“节”等层级关键词并填入左侧。")
        
        # Auto-update nesting options whenever structure levels change
        self.structure_var.trace_add("write", lambda *_: self.after(50, self._update_strategy_options))
        
        # Options
        self.include_body_var = ctk.BooleanVar(value=True)
        self.include_body_cb = ctk.CTkCheckBox(settings_panel, text="导出章节正文", variable=self.include_body_var)
        self.include_body_cb.pack(anchor="w", pady=(0, 5))
        ToolTip(self.include_body_cb, "如果取消勾选，则只会输出空文件（仅保留文件名，通常用于提取目录结构）。")
        
        self.skip_toc_var = ctk.BooleanVar(value=True)
        self.skip_toc_cb = ctk.CTkCheckBox(settings_panel, text="跳过目录页", variable=self.skip_toc_var)
        self.skip_toc_cb.pack(anchor="w", pady=(0, 10))
        ToolTip(self.skip_toc_cb, "自动识别并过滤小说开头过密集的目录行。")
        
        # Advanced Chunking Options
        # self.chunk_frame removed to avoid packing inside packing error
        self.enable_chunking_var = ctk.BooleanVar(value=False)
        self.chunking_checkbox_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        self.chunking_checkbox_frame.pack(fill="x", pady=(0, 5))
        self.enable_chunking_cb = ctk.CTkCheckBox(self.chunking_checkbox_frame, text="超长文本二次细分", variable=self.enable_chunking_var, command=self.toggle_chunking)
        self.enable_chunking_cb.pack(anchor="w")
        ToolTip(self.enable_chunking_cb, "若截断后发现字数还是大得离谱（如一行有五万字），强制切成碎片小块。")
        
        self.chunk_inputs_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
        
        row1 = ctk.CTkFrame(self.chunk_inputs_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 5))
        self.comparator_var = ctk.StringVar(value="≈ 约等于")
        self.comparator_combo = ctk.CTkOptionMenu(row1, values=["≈ 约等于", "= 等于", "> 大于", "≥ 大于等于", "< 小于", "≤ 小于等于"], variable=self.comparator_var, width=110, command=self._sync_break_by_comparator)
        self.comparator_combo.pack(side="left")
        self.max_len_var = ctk.StringVar(value="1500")
        self.max_len_entry = ctk.CTkEntry(row1, textvariable=self.max_len_var, width=60)
        self.max_len_entry.pack(side="left", padx=(5, 10))
        ToolTip(self.max_len_entry, "当章节文本或者物理块的长度大于这个阈值时，才会触发这套内部细分机制。")
        
        lbl_split = ctk.CTkLabel(row1, text="切为:", width=35)
        lbl_split.pack(side="left")
        
        self.chunk_size_comparator_var = ctk.StringVar(value="≈ 约等于")
        self.chunk_size_comparator_combo = ctk.CTkOptionMenu(
            row1, 
            values=["≈ 约等于", "= 等于", "> 大于", "≥ 大于等于", "< 小于", "≤ 小于等于"],
            variable=self.chunk_size_comparator_var,
            width=110,
            command=self._sync_break_by_comparator
        )
        self.chunk_size_comparator_combo.pack(side="left", padx=(5, 0))

        self.chunk_size_var = ctk.StringVar(value="500")
        self.chunk_size_entry = ctk.CTkEntry(row1, textvariable=self.chunk_size_var, width=60)
        self.chunk_size_entry.pack(side="left", padx=(5, 0))
        ToolTip(self.chunk_size_entry, "期望切分出的每一块碎片的预期容量。")
        
        
        self.chunk_break_frame = ctk.CTkFrame(settings_panel, fg_color="transparent") # Child of settings_panel now
        lbl_break = ctk.CTkLabel(self.chunk_break_frame, text="防生硬截断保护:")
        lbl_break.pack(side="left")
        ToolTip(lbl_break, "Sentence: 智能寻找最近的句号/换行切分\nParagraph: 只在自然段末尾切分\nExact Size: 无视语句，强行准确切断")
        self.chunk_break_combo = ctk.CTkOptionMenu(
            self.chunk_break_frame,
            values=["Sentence 就近句号", "Paragraph 段落末尾", "Exact 强行截断"],
            width=160,
            command=self._sync_comparator_by_break
        )
        self.chunk_break_combo.pack(side="right")
        self.chunk_break_combo.set("Sentence 就近句号")
        
        # Theme Switch
        self.theme_var = ctk.StringVar(value="Dark")
        self.theme_switch = ctk.CTkSwitch(
            settings_panel,
            text="🌙 暗黑模式",
            variable=self.theme_var,
            onvalue="Dark",
            offvalue="Light",
            command=self.toggle_theme
        )
        self.theme_switch.pack(anchor="w", pady=(10, 10))
        ToolTip(self.theme_switch, "切换软件界面的浅色/暗黑模式。")

        # Scan Button
        self.scan_btn = ctk.CTkButton(settings_panel, text="扫描预览", command=self.scan_file)
        self.scan_btn.pack(fill="x", pady=(10, 0))
        ToolTip(self.scan_btn, "点击可以提前将左侧的参数应用到右侧的预览面板里。")
        
        # Encoding Info Label
        self.encoding_label = ctk.CTkLabel(settings_panel, text="检测到的文件编码: N/A", text_color="gray")
        self.encoding_label.pack(anchor="w", pady=(5, 0))
        
        # Initial UI state
        self.on_mode_change("📜 智能章节模式")
        
        
        # ---- Right Panel: Preview List ----
        preview_panel = ctk.CTkFrame(main_frame)
        preview_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(preview_panel, text="预览", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        self.preview_box = ctk.CTkTextbox(preview_panel, state="disabled")
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.preview_tree_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        borderwidth=0,
                        font=("Consolas", 10))
        style.map('Treeview', background=[('selected', '#1f538d')])
        
        self.preview_tree = ttk.Treeview(self.preview_tree_frame, selectmode="extended", show="tree")
        self.preview_tree_scrollbar = ttk.Scrollbar(self.preview_tree_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=self.preview_tree_scrollbar.set)
        self.preview_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        self.preview_tree_scrollbar.pack(side="right", fill="y")
        self.preview_tree.pack(side="left", fill="both", expand=True)
        
    def _build_action_frame(self):
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        controls_row = ctk.CTkFrame(action_frame, fg_color="transparent")
        controls_row.pack(fill="x")

        self.progress_bar = ctk.CTkProgressBar(controls_row)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.progress_bar.set(0)

        self.split_btn = ctk.CTkButton(controls_row, text="开始切割", command=self.start_split, state="disabled")
        self.split_btn.pack(side="right")
        ToolTip(self.split_btn, "按当前配置执行切割。")

        self.status_label = ctk.CTkLabel(action_frame, textvariable=self.status_var, anchor="w", text_color="gray")
        self.status_label.pack(fill="x", pady=(6, 0))

    # --- Event Handlers ---

    def _is_constraint_mode(self, mode: Optional[str] = None) -> bool:
        target_mode = mode if mode is not None else self.output_mode_combo.get()
        return is_constraint_mode(target_mode)

    def _scan_button_label(self, mode: Optional[str] = None) -> str:
        return "预览切割效果" if self._is_constraint_mode(mode) else "扫描预览"

    def _set_scan_button_ready(self, mode: Optional[str] = None):
        self.scan_btn.configure(state="normal", text=self._scan_button_label(mode))

    def _collect_global_settings(self, include_output_dir: bool = False) -> Dict[str, Any]:
        settings: Dict[str, Any] = {
            "mode": self.output_mode_combo.get(),
            "strategy": self.strategy_var.get(),
            "structure": self.structure_var.get().replace("，", ","),
            "language": self._get_selected_lang_id(),
            "constraint_limit": self.constraint_limit_var.get(),
            "constraint_comparator": self.constraint_comparator_var.get(),
            "chunk_break": self.chunk_break_combo.get(),
            "max_length": self.max_len_var.get(),
            "chunk_size": self.chunk_size_var.get(),
            "enable_chunking": self.enable_chunking_var.get(),
            "trigger_comparator": self.comparator_var.get(),
            "chunk_size_comparator": self.chunk_size_comparator_var.get(),
            "include_body": self.include_body_var.get(),
            "skip_toc": self.skip_toc_var.get(),
        }
        if include_output_dir:
            settings["output_dir"] = self.out_var.get()
        return settings

    def _friendly_error_message(self, err_msg: str) -> str:
        msg = (err_msg or "").strip()
        lower = msg.lower()
        if "no extractable text found in pdf" in lower or "returned no text" in lower:
            return (
                "该 PDF 的文本层读取失败（常见于图片型/扫描型 PDF）。\n"
                "当前不做 OCR，请先在外部工具中导出可复制文本后再导入。"
            )
        if "unsupported input format" in lower:
            return "文件格式不受支持，请检查扩展名。"
        if "unable to locate usable extracted content" in lower or "drm" in lower:
            return "电子书可能受 DRM 保护或提取失败，暂时无法读取。"
        return msg
    
    def on_mode_change(self, value):
        # Reset chunk views
        self.strategy_frame.pack_forget()
        self.constraint_frame.pack_forget()
        self.struct_container.pack_forget()
        self.chunking_checkbox_frame.pack_forget()
        self.chunk_inputs_frame.pack_forget()
        self.chunk_break_frame.pack_forget()
        
        # Re-pack in correct order
        if is_chapter_mode(value):
            self.strategy_frame.pack(fill="x", pady=(0, 10), after=self.output_mode_combo.master)
            self.struct_container.pack(fill="x", pady=(0, 10), after=self.strategy_frame)
            self.chunking_checkbox_frame.pack(fill="x", pady=(5, 0), after=self.struct_container)
            if self.enable_chunking_var.get():
                self.chunk_inputs_frame.pack(fill="x", pady=(5, 0), after=self.chunking_checkbox_frame)
                self.chunk_break_frame.pack(fill="x", pady=(5, 0), after=self.chunk_inputs_frame)
            
            self._set_scan_button_ready(value)
            if not self.parsed_chapters:
                self.split_btn.configure(state="disabled")
        else:
            self.constraint_frame.pack(fill="x", pady=(0, 20), after=self.output_mode_combo.master)
            
            if is_word_mode(value):
                self.chunk_break_frame.pack(fill="x", pady=(5, 0), after=self.constraint_frame)
            elif is_line_mode(value) or is_paragraph_mode(value):
                self.chunking_checkbox_frame.pack(fill="x", pady=(5, 0), after=self.constraint_frame)
                if self.enable_chunking_var.get():
                    self.chunk_inputs_frame.pack(fill="x", pady=(5, 0), after=self.chunking_checkbox_frame)
                    self.chunk_break_frame.pack(fill="x", pady=(5, 0), after=self.chunk_inputs_frame)
            
            self._set_scan_button_ready(value)
            self.split_btn.configure(state="normal")
        self.status_var.set(f"模式已更新，可预览 {len(getattr(self, 'parsed_chapters', {}))} 个文件。")
    
    def toggle_chunking(self):
        if self.enable_chunking_var.get():
            self.chunk_inputs_frame.pack(fill="x", pady=(5, 0), after=self.chunking_checkbox_frame)
            self.chunk_break_frame.pack(fill="x", pady=(5, 0), after=self.chunk_inputs_frame)
        else:
            self.chunk_inputs_frame.pack_forget()
            self.chunk_break_frame.pack_forget()

    def toggle_theme(self):
        mode = self.theme_var.get()
        ctk.set_appearance_mode(mode)
        if mode == "Dark":
            self.theme_switch.configure(text="🌙 暗黑模式")
        else:
            self.theme_switch.configure(text="☀️ 浅色模式")
    
    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        supported_files = [f.strip('{}') for f in files if self._is_supported_file(f.strip('{}'))]
        if supported_files:
            self.set_files(supported_files)
        elif files:
            self.status_var.set("拖拽内容中没有可用文件。")
            messagebox.showwarning("不支持的文件", "仅支持 txt/epub/docx/mobi/azw3，以及部分 pdf。")

    def select_file(self):
        pattern = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_INPUT_EXTS))
        file_paths = filedialog.askopenfilenames(
            filetypes=[
                ("Supported Documents", pattern),
                ("Text Files", "*.txt"),
                ("PDF Files (Partial)", "*.pdf"),
                ("EPUB Files", "*.epub"),
                ("Word Files", "*.docx"),
                ("Kindle Files", "*.mobi *.azw3"),
            ]
        )
        if file_paths:
            self.set_files(list(file_paths))

    def _is_supported_file(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() in SUPPORTED_INPUT_EXTS

    def clear_files(self):
        self.selected_files = []
        self.parsed_chapters = {}
        self.file_settings = {}
        self.file_encoding = None
        self.file_var.set("拖拽文件到此处或点击选择")
        self.file_count_var.set("未选择文件")
        self.status_var.set("已清空文件列表。")
        self.out_var.set("未选择")
        self.update_preview("")
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.split_btn.configure(state="disabled")
        self._set_scan_button_ready()
        self.progress_bar.set(0)
        self.indiv_settings_btn.pack_forget()

    def set_files(self, file_paths):
        self.selected_files = file_paths

        if len(file_paths) == 1:
            filename = os.path.basename(file_paths[0])
            self.file_var.set(f"已选择: {filename}")
            output_folder_name = f"{os.path.splitext(filename)[0]}_split"
        else:
            self.file_var.set(f"批量模式: 已选择 {len(file_paths)} 个文件")
            output_folder_name = "Batch_Split_Output"

        ext_counter = Counter(os.path.splitext(p)[1].lower() for p in file_paths)
        ext_summary = ", ".join(f"{k}:{v}" for k, v in sorted(ext_counter.items()))
        self.file_count_var.set(f"{len(file_paths)} 个文件 | {ext_summary}")
        self.status_var.set(f"文件已载入，点击“{self._scan_button_label()}”查看效果。")

        # Auto-set output dir to same directory as first file
        self.output_dir = os.path.join(os.path.dirname(file_paths[0]), output_folder_name)
        self.out_var.set(self.output_dir)

        # Clear preview
        self.update_preview("")
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.split_btn.configure(state="disabled")
        self._set_scan_button_ready()
        self.progress_bar.set(0)
        self.indiv_settings_btn.pack_forget()

    def select_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.out_var.set(dir_path)
            
    def _on_tree_select(self, event):
        selected = self.preview_tree.selection()
        if len(self.selected_files) > 1 and len(selected) > 0:
            item = selected[0]
            tags = self.preview_tree.item(item, "tags")
            if tags and len(tags) > 0:
                self.indiv_settings_btn.pack(fill="x", pady=(5, 10), after=self.file_btn)
                self.indiv_settings_btn.configure(text=f"⚙️ 单独设置: {os.path.basename(tags[0])}")
                self._current_selected_file_path = tags[0]
                return
        
        self.indiv_settings_btn.pack_forget()
        self._current_selected_file_path = None
        
    def open_per_file_settings(self):
        if not hasattr(self, '_current_selected_file_path') or not self._current_selected_file_path:
            return
            
        file_path = self._current_selected_file_path
        current_settings = self.file_settings.get(file_path, {})
        
        PerFileSettingsWindow(
            master=self,
            file_path=file_path,
            current_settings=current_settings,
            on_save_callback=self._on_save_file_settings
        )
        
    def _on_save_file_settings(self, file_path, new_settings):
        if new_settings is None:
            if file_path in self.file_settings:
                del self.file_settings[file_path]
        else:
            self.file_settings[file_path] = new_settings
            
        # Optional: auto-re-scan the file to show changes
        self.scan_file()
        
    def auto_analyze_structure(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "请先选择文本文件 (Please select a file first).")
            return
            
        self.analyze_btn.configure(state="disabled", text="分析中...")
        threading.Thread(target=self._analyze_thread, daemon=True).start()
        
    def _analyze_thread(self):
        try:
            prepared = self.parser.prepare_document(self.selected_files[0])
            try:
                self.file_encoding = prepared.encoding
                # Resolve language first, which handles 'Auto' -> None to actual lang
                lang_id = self._resolve_lang_for_file(prepared.working_text_path, prepared.encoding)
                detected_struct = self.parser.analyze_structure(
                    prepared.working_text_path,
                    encoding=prepared.encoding,
                    lang=lang_id
                )
            finally:
                self.parser.cleanup_prepared_document(prepared)
            self.after(0, self._analyze_complete, detected_struct)
        except Exception as e:
            self.after(0, self._analyze_error, str(e))
            
    def _analyze_complete(self, struct_val):
        self.structure_var.set(struct_val)
        self.analyze_btn.configure(state="normal", text="自动分析")
        
    def _analyze_error(self, err_msg):
        friendly = self._friendly_error_message(err_msg)
        if "OCR" in friendly or "无法读取" in friendly:
            messagebox.showwarning("Analysis Notice", friendly)
        else:
            messagebox.showerror("Analysis Error", f"分析失败: {friendly}")
        self.analyze_btn.configure(state="normal", text="自动分析")
            
    def update_preview(self, text):
        self.preview_tree_frame.pack_forget()
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.preview_box.configure(state="normal")
        self.preview_box.delete("0.0", "end")
        self.preview_box.insert("0.0", text)
        self.preview_box.configure(state="disabled")
        

    # --- Logic Threading ---
    
    def _update_strategy_options(self):
        """Rebuild nesting depth options to match the current structure level count."""
        raw = self.structure_var.get().replace("，", ",")
        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        
        # Strip any regex/quote wrappers to get display name
        def display_name(tok: str) -> str:
            tok = tok.strip('"').strip("“”")
            return tok if tok else tok
        
        options = ["Flat 同级输出"]
        if len(tokens) >= 2:
            level_names = [display_name(t) for t in tokens]
            # For each intermediate depth
            for i in range(1, len(tokens)):
                path_label = "→".join(level_names[:i])  # type: ignore[misc]
                if i == len(tokens) - 1:   # last option = full nesting
                    options.append(f"Nested/全部 按{path_label}")
                else:
                    options.append(f"Nested/{i} 按{path_label}")
        
        current = self.strategy_var.get()
        self.strategy_combo.configure(values=options)
        if current not in options:
            self.strategy_var.set("Flat 同级输出")
    
    def _sync_comparator_by_break(self, break_val: str):
        """If anti-truncation is enabled, force all comparators away from 'Exactly Equal'."""
        if "Sentence" in break_val or "Paragraph" in break_val:
            for var in [self.constraint_comparator_var, self.chunk_size_comparator_var, self.comparator_var]:
                if var.get() == "= 等于":
                    var.set("≈ 约等于")

    def _sync_break_by_comparator(self, comp_val: str):
        """If any comparator is 'Exactly Equal', force break mode to 'Exact Size'."""
        if comp_val == "= 等于":
            self.chunk_break_combo.set("Exact 强行截断")
    
    def _get_selected_lang_id(self) -> str | None:
        """Get the language ID from the language dropdown. Returns None for Auto."""
        val = self.lang_combo.get()
        if 'Auto' in val:
            return None
        if 'Multi' in val:
            return 'multi'
        for lp in get_all_languages():
            if lp.display_name in val:
                return lp.lang_id
        return None

    def _resolve_lang_for_file(self, file_path: str, encoding: str | None = None) -> str:
        """Resolve the actual language ID, auto-detecting if needed."""
        lang_id = self._get_selected_lang_id()
        if lang_id:
            return lang_id
        # Auto-detect from file content
        prepared = None
        try:
            target_path = file_path
            enc = encoding or self.file_encoding
            if not enc or not file_path.lower().endswith('.txt'):
                prepared = self.parser.prepare_document(file_path)
                target_path = prepared.working_text_path
                enc = prepared.encoding
            with open(target_path, 'r', encoding=enc, errors='replace') as f:
                sample = f.read(5000)
            return detect_language(sample)
        except Exception:
            return 'zh'
        finally:
            if prepared is not None:
                self.parser.cleanup_prepared_document(prepared)

    def get_regexes_from_ui(self):
        regexes = []
        raw_input = self.structure_var.get().replace("，", ",")
        tokens = [t.strip() for t in raw_input.split(",") if t.strip()]
        
        # Determine language
        lang_id = self._get_selected_lang_id()
        if not lang_id and self.selected_files:
            lang_id = self._resolve_lang_for_file(self.selected_files[0])
        if not lang_id or lang_id == 'multi':
            lang_id = 'zh'
        
        return build_regexes_from_tokens(tokens, lang_id)
            
    def scan_file(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "请先选择文本文件。")
            return
            
        self.scan_btn.configure(state="disabled", text="处理中...")
        self.status_var.set("正在生成预览...")
        self.split_btn.configure(state="disabled")
        self.update_preview("正在生成预览，请稍候...\n")
        
        global_settings = self._collect_global_settings()

        threading.Thread(target=self._scan_thread, args=(global_settings,), daemon=True).start()

    def _scan_thread(self, global_settings: Dict[str, Any]):
        try:
            result = self.split_service.scan_files(
                selected_files=self.selected_files,
                global_settings=global_settings,
                file_settings=self.file_settings,
                preview_limit=10,
                status_callback=lambda msg: self.after(0, self.status_var.set, msg),
            )

            self.parsed_chapters = result.parsed_chapters
            if result.first_encoding:
                self.file_encoding = result.first_encoding
                self.after(0, self.encoding_label.configure, {"text": f"检测到的文件编码: {result.first_encoding.upper()}"})

            friendly_failed = [(name, self._friendly_error_message(msg)) for name, msg in result.failed_files]

            if not result.parsed_chapters:
                preview_text = "未发现匹配各语言正则的章节。(No chunks found matching patterns/limits.)"
                if friendly_failed:
                    detail = "\n".join(f"- {name}: {msg}" for name, msg in friendly_failed[:8])
                    if len(friendly_failed) > 8:
                        detail += f"\n... 以及另外 {len(friendly_failed) - 8} 个文件。"
                    preview_text += f"\n\n以下文件预览失败:\n{detail}"
                self.after(0, self._scan_complete, preview_text, False, friendly_failed)
            else:
                self.after(0, self._scan_complete_and_render, friendly_failed)
        except Exception as e:
            self.after(0, self._scan_error, str(e))

    def _update_preview_visibility(self):
        self.preview_box.pack_forget()
        self.preview_tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_strategy_change(self, *args):
        if hasattr(self, 'parsed_chapters') and self.parsed_chapters:
            self._scan_complete_and_render()
            
    def _scan_complete_and_render(self, failed_files: Optional[List[tuple[str, str]]] = None):
        self._update_preview_visibility()
        self._render_preview_tree()
        
        # update_preview resets to textbox, so we just clear its content instead of using it here if possible
        # or we just let tree frame be packed. update_preview will hide tree frame, so we shouldn't call it.
        # But we must ensure it doesn't pop up.
        
        self._set_scan_button_ready()
        self.split_btn.configure(state="normal")
        failed_count = len(failed_files or [])
        if failed_count:
            self.status_var.set(f"预览完成，{failed_count} 个文件失败。")
            msg_lines = [f"以下文件预览失败（共 {failed_count} 个）："]
            for name, msg in (failed_files or [])[:8]:
                msg_lines.append(f"- {name}: {msg}")
            if failed_count > 8:
                msg_lines.append(f"... 以及另外 {failed_count - 8} 个。")
            messagebox.showwarning("预览部分失败", "\n".join(msg_lines))
        else:
            self.status_var.set("预览完成，可开始切割。")

    def _render_preview_tree(self):
        """
        Render a hierarchical Treeview preview based on current splitting logic.
        Tailored visual structure and batch nesting by bbbz123.
        """
        self.preview_tree.delete(*self.preview_tree.get_children())
            
        all_results = getattr(self, 'parsed_chapters', {})
        if not all_results:
            self.preview_tree.insert("", "end", text="未找到符合条件的分块。(No sections found.)")
            return
            
        strat = self.strategy_var.get()
        nested_mode = "Flat"
        if "Nested" in strat:
            m = re.search(r'Nested/(\d+)', strat)
            nested_mode = f"Nested:{m.group(1)}" if m else "Nested"

        # If multiple files, add a top-level "Batch" node or just list files
        is_batch = len(all_results) > 1
        
        for file_path, lang_results in all_results.items():
            file_name = os.path.basename(file_path)
            if is_batch:
                # Use the same logic as _split_thread for folder naming
                folder_name = os.path.splitext(file_name)[0]
                file_node = self.preview_tree.insert("", "end", text=f"📂 {folder_name}", open=False, tags=(file_path,))
                
                # Check if it has custom settings and append visual cue
                if file_path in self.file_settings:
                    self.preview_tree.item(file_node, text=f"📂 {folder_name} [⚙️已单独设置]")
            else:
                file_node = ""

            total_langs = len(lang_results)
            # If constraint mode, lang_results might be {'zh': chapters} with is_constraint=True
            is_constraint = False
            for chaps in lang_results.values():
                if chaps and chaps[0].get("is_constraint", False):
                    is_constraint = True
                    break
                    
            if total_langs > 1 and not is_constraint:
                lang_root = self.preview_tree.insert(file_node, "end", text=f"【多语言】发现 {total_langs} 种语言", open=True)
            else:
                lang_root = file_node
                
            for lid, chapters in lang_results.items():
                if not is_constraint:
                    lang_name = get_language(lid).display_name
                    if total_langs > 1:
                        lang_node = self.preview_tree.insert(lang_root, "end", text=f"📁 {lang_name} ({len(chapters)} 章)", open=True)
                    else:
                        lang_node = lang_root
                else:
                    lang_node = lang_root
                
                # Keep track of folder nodes by their exact path tuple
                folder_nodes = {}
                folder_nodes[()] = lang_node
                
                for i, c in enumerate(chapters[:100]): # Limit per file for perf
                    h_path = c.get('hierarchy_path', [])
                    folder_levels = []
                    
                    if len(h_path) > 1 and "Nested" in nested_mode and not c.get("is_constraint", False):
                        if "Nested:1" in nested_mode:
                            folder_levels = h_path[:1]
                        elif "Nested:2" in nested_mode:
                            folder_levels = h_path[:2]
                        else:
                            folder_levels = h_path[:-1]
                            
                    current_parent_node = lang_node
                    current_path = []
                    
                    # Traverse and create necessary folder nodes
                    for folder in folder_levels:
                        folder_safe = re.sub(r'[\\/*?:"<>|]', "", folder.strip())
                        if not folder_safe:
                            continue
                            
                        current_path.append(folder_safe)
                        path_tuple = tuple(current_path)
                        
                        if path_tuple not in folder_nodes:
                            folder_id = self.preview_tree.insert(current_parent_node, "end", text=f"📁 {folder_safe}", open=True)
                            folder_nodes[path_tuple] = folder_id
                            
                        current_parent_node = folder_nodes[path_tuple]
                    
                    # Insert the actual file as a leaf node exactly like output
                    safe_title = c.get('title', '').strip()
                    raw_safe = c.get('raw_title', safe_title).strip()
                    
                    if c.get("is_constraint", False):
                        filename = f"📄 {safe_title}.txt"
                        node_text = f"{filename}  |  行数范围: {c['line_start']} - {c['line_end']}  |  字符数预计: ~{c.get('size_chars', 0)}"
                    else:
                        if "Nested" in nested_mode:
                            filename = f"📄 {i+1:03d}_{raw_safe}.txt"
                        else:
                            filename = f"📄 {i+1:03d}_{safe_title}.txt"
                            
                        node_text = f"{filename} (行 {c['line_start']})"
                        
                    self.preview_tree.insert(current_parent_node, "end", text=node_text, open=True)
                    
                if len(chapters) > 100:
                    self.preview_tree.insert(lang_node, "end", text=f"... 以及剩余 {len(chapters) - 100} 章/切片")
        
        if len(self.selected_files) > 10:
             self.preview_tree.insert("", "end", text=f"⚠️ 注意: 仅预览前 10 个文件。")

    def _scan_complete(
        self,
        preview_text,
        enable_split,
        failed_files: Optional[List[tuple[str, str]]] = None,
    ):
        self.update_preview(preview_text)
        self._set_scan_button_ready()
            
        if enable_split:
            self.split_btn.configure(state="normal")
            self.status_var.set("预览完成，可开始切割。")
        else:
            failed_count = len(failed_files or [])
            if failed_count:
                self.status_var.set(f"预览失败：{failed_count} 个文件无法读取。")
            else:
                self.status_var.set("预览完成，未发现可切分内容。")
            
    def _scan_error(self, err_msg):
        friendly = self._friendly_error_message(err_msg)
        self.update_preview(f"扫描失败:\n{friendly}")
        self._set_scan_button_ready()
            
        self.status_var.set("预览失败。")
        if "OCR" in friendly or "无法读取" in friendly:
            messagebox.showwarning("Scan Notice", friendly)
        else:
            messagebox.showerror("Scan Error", friendly)
        
    def start_split(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "请先选择文本文件。")
            return
            
        out_path = self.out_var.get()
        if out_path == "未选择" or not out_path:
            messagebox.showwarning("Warning", "请选择输出目录。")
            return
            
        # Ensure output directory exists
        os.makedirs(out_path, exist_ok=True)
            
        global_settings = self._collect_global_settings(include_output_dir=True)
        
        # Lock UI
        self.split_btn.configure(state="disabled", text="切割中...")
        self.progress_bar.set(0)
        self.status_var.set(f"开始切割，共 {len(self.selected_files)} 个文件...")
        
        threading.Thread(target=self._split_thread, args=(global_settings,), daemon=True).start()
        
    def _split_thread(self, global_settings: Dict[str, Any]):
        try:
            def on_file_start(current: int, total: int, filename: str):
                self.after(0, self.file_var.set, f"[{current}/{total}] 处理中: {filename}")

            def on_batch_progress(current: int, total: int):
                self.after(0, self.progress_bar.set, current / max(total, 1))
                self.after(0, self.status_var.set, f"批量切割进度: {current}/{total}")

            result = self.split_service.split_files(
                selected_files=self.selected_files,
                global_settings=global_settings,
                file_settings=self.file_settings,
                parsed_chapters=self.parsed_chapters if isinstance(self.parsed_chapters, dict) else {},
                file_start_callback=on_file_start,
                batch_progress_callback=on_batch_progress,
                chunk_progress_callback=self._update_progress if len(self.selected_files) == 1 else None,
            )

            friendly_failed = [(name, self._friendly_error_message(msg)) for name, msg in result.failed_files]
            self.after(0, self._split_complete, friendly_failed, result.total_files, result.output_dir)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, self._split_error, str(e))

    def _update_progress(self, current, total):
        # Only precise updating for single files, for batch it loops too fast to clearly show inside each file
        # But this works good enough
        val = current / max(total, 1)
        self.after(0, self.progress_bar.set, val)
        self.after(0, self.status_var.set, f"切割进度: {current}/{max(total, 1)}")
        
    def _split_complete(
        self,
        failed_files: Optional[List[tuple[str, str]]] = None,
        total_files: Optional[int] = None,
        output_dir: Optional[str] = None,
    ):
        failed_files = failed_files or []
        total = total_files if total_files is not None else len(self.selected_files)
        success_count = max(total - len(failed_files), 0)

        self.split_btn.configure(state="normal", text="开始切割")
        self.progress_bar.set(1)
        self.status_var.set(f"切割完成: 成功 {success_count}/{total} 个文件。")
        if len(self.selected_files) > 1:
            self.file_var.set(f"批量完成: 成功 {success_count}/{total} 个文件")

        if failed_files:
            msg_lines = [f"处理完成，其中 {len(failed_files)} 个文件失败。"]
            for filename, err in failed_files[:8]:
                msg_lines.append(f"- {filename}: {err}")
            if len(failed_files) > 8:
                msg_lines.append(f"... 以及另外 {len(failed_files) - 8} 个。")
            messagebox.showwarning("完成（部分失败）", "\n".join(msg_lines))
        else:
            messagebox.showinfo("完成", "切割成功！\n请检查输出目录。")

        # Open output folder
        try:
            out_path = output_dir or self.out_var.get()

            if os.path.exists(out_path):
                os.startfile(out_path)  # type: ignore[attr-defined]  # nosec B606
        except Exception as e:
            print(f"Could not open output dir: {e}")

    def _split_error(self, err_msg):
        self.split_btn.configure(state="normal", text="开始切割")
        self.status_var.set("切割失败。")
        messagebox.showerror("Split Error", err_msg)

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
            



