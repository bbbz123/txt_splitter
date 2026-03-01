import customtkinter as ctk # type: ignore
from core.patterns import get_all_languages  # type: ignore[import]
import os

class PerFileSettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, file_path, current_settings, on_save_callback):
        super().__init__(master)
        self.title("单独设置 (Individual Settings)")
        self.geometry("480x420")
        self.attributes("-topmost", True)
        
        self.file_path = file_path
        self.current_settings = current_settings or {}
        self.on_save_callback = on_save_callback
        
        # --- UI Build ---
        
        filename = os.path.basename(file_path)
        lbl_file = ctk.CTkLabel(self, text=f"文件: {filename}", wraplength=450, justify="left", font=ctk.CTkFont(weight="bold"))
        lbl_file.pack(pady=(10, 20), padx=10, fill="x")
        
        # 1. Output Mode
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(mode_frame, text="切割模式:").pack(side="left")
        self.mode_var = ctk.StringVar(value=self.current_settings.get("mode", "📜 智能章节模式"))
        self.mode_combo = ctk.CTkOptionMenu(
            mode_frame, 
            values=["跟随全局 (Global)", "📜 智能章节模式", "🗂️ 按文件大小 (KB)", "📝 按字数切分", "📄 按行数切分", "📑 按段落切分"],
            variable=self.mode_var,
            width=170,
            command=self._on_mode_change
        )
        self.mode_combo.pack(side="right")
        
        # 2. Strategy (For Regex)
        self.strategy_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.strategy_frame, text="保存策略:").pack(side="left")
        self.strategy_var = ctk.StringVar(value=self.current_settings.get("strategy", "Flat 同级输出"))
        self.strategy_combo = ctk.CTkOptionMenu(
            self.strategy_frame,
            variable=self.strategy_var,
            values=["跟随全局 (Global)", "Flat 同级输出", "Nested/1 按卷建层", "Nested/2 按卷→章建层", "Nested/全部 全层级嵌套"],
            width=170
        )
        self.strategy_combo.pack(side="right")
        
        # 3. Structure Tokens
        self.struct_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.struct_frame, text="层级结构 (逗号分隔, 留空跟随全局):").pack(anchor="w")
        self.structure_var = ctk.StringVar(value=self.current_settings.get("structure", ""))
        self.structure_entry = ctk.CTkEntry(self.struct_frame, textvariable=self.structure_var)
        self.structure_entry.pack(fill="x", pady=(5, 0))
        
        # 4. Language Override
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.lang_frame, text="语言覆盖:").pack(side="left")
        self.lang_var = ctk.StringVar(value=self.current_settings.get("language", "跟随全局 (Global)"))
        lang_options = ["跟随全局 (Global)", "⚡ Auto 自动检测", "🌐 Multi-Language 双语/多语"] + [lp.display_name for lp in get_all_languages()]
        self.lang_combo = ctk.CTkOptionMenu(self.lang_frame, values=lang_options, variable=self.lang_var, width=170)
        self.lang_combo.pack(side="right")
        
        # 5. Constraint Frame
        self.constraint_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.constraint_comparator_var = ctk.StringVar(value=self.current_settings.get("constraint_comparator", "≈ 约等于"))
        self.constraint_comparator_combo = ctk.CTkOptionMenu(
            self.constraint_frame, 
            values=["跟随全局 (Global)", "≈ 约等于", "= 等于", "> 大于", "≥ 大于等于", "< 小于", "≤ 小于等于"],
            variable=self.constraint_comparator_var,
            width=110
        )
        self.constraint_comparator_combo.pack(side="left")
        ctk.CTkLabel(self.constraint_frame, text="限制:").pack(side="left", padx=5)
        self.constraint_limit_var = ctk.StringVar(value=str(self.current_settings.get("constraint_limit", "")))
        self.constraint_limit_entry = ctk.CTkEntry(self.constraint_frame, textvariable=self.constraint_limit_var, width=80)
        self.constraint_limit_entry.pack(side="left")
        
        self.chunk_break_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.chunk_break_frame, text="截断保护:").pack(side="left")
        self.chunk_break_var = ctk.StringVar(value=self.current_settings.get("chunk_break", "跟随全局 (Global)"))
        self.chunk_break_combo = ctk.CTkOptionMenu(
            self.chunk_break_frame,
            values=["跟随全局 (Global)", "Sentence 就近句号", "Paragraph 段落末尾", "Exact 强行截断"],
            variable=self.chunk_break_var,
            width=140
        )
        self.chunk_break_combo.pack(side="right")
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30, side="bottom")
        
        ctk.CTkButton(btn_frame, text="清除独立设置", fg_color="#D32F2F", hover_color="#B71C1C", command=self._clear).pack(side="left")
        ctk.CTkButton(btn_frame, text="保存并应用", command=self._save).pack(side="right")
        
        # Init visibility
        self._on_mode_change(self.mode_var.get())
        
    def _on_mode_change(self, value):
        self.strategy_frame.pack_forget()
        self.struct_frame.pack_forget()
        self.lang_frame.pack_forget()
        self.constraint_frame.pack_forget()
        self.chunk_break_frame.pack_forget()
        
        if "跟随全局" in value:
            # Show nothing extra if following global mode
            pass
        elif "章节模式" in value or "Regex" in value:
            self.strategy_frame.pack(fill="x", padx=20, pady=5, after=self.mode_combo.master)
            self.struct_frame.pack(fill="x", padx=20, pady=5, after=self.strategy_frame)
            self.lang_frame.pack(fill="x", padx=20, pady=5, after=self.struct_frame)
        else:
            self.constraint_frame.pack(fill="x", padx=20, pady=5, after=self.mode_combo.master)
            self.chunk_break_frame.pack(fill="x", padx=20, pady=5, after=self.constraint_frame)
            
    def _save(self):
        new_settings = {
            "mode": self.mode_var.get(),
            "strategy": self.strategy_var.get(),
            "structure": self.structure_var.get().strip(),
            "language": self.lang_var.get(),
            "constraint_comparator": self.constraint_comparator_var.get(),
            "chunk_break": self.chunk_break_var.get()
        }
        
        limit_val = self.constraint_limit_var.get().strip()
        if limit_val:
            try:
                new_settings["constraint_limit"] = int(limit_val)
            except ValueError:
                pass
                
        self.on_save_callback(self.file_path, new_settings)
        self.destroy()
        
    def _clear(self):
        self.on_save_callback(self.file_path, None)
        self.destroy()
