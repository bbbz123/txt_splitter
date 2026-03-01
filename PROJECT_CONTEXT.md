# PROJECT CONTEXT (代码快照归档)

## 1. 项目结构树状图 (Project Tree)
```text
txt_splitter/
├── core/
│   └── parser.py            # 核心引擎：负责编码识别和正则拆分逻辑
├── gui/
│   └── app.py               # 图形界面：包含 CustomTkinter 拖拽组件和逻辑调度
├── tests/
│   ├── dummy_novel.txt      # 测试用的虚拟文本
│   ├── test_parser.py       # core/parser 单元测试
│   └── test_real_files.py   # 真实例子测试脚本
├── main.py                  # 程序启动入口
├── split_user_files.py      # 用于之前后台静态执行真实文本拆分的脚本
└── requirements.txt         # 依赖列表
```

## 2. 代码审计报告 (Code Audit Report)

### 2.1 重复的函数 (Duplicated Functions)
经扫描发现，项目中存在一处明显的职能重复（代码重复）：
- **`gui.app.GUI._scan_thread()` 和 `core.parser.TextParser.parse_chapters()`**：
  在 `gui/app.py` 中的 `_scan_thread` (第 182-228 行) 是为了在界面上预览章节而实现的，但它在内部独自通过 `re.compile()` 重新实现了一遍扫描逻辑，这与 `parser.py` 里专门用于抽取章节的 `parse_chapters` 函数存在高度重复。长期来看，应该让 GUI 直接调用 `parser.parse_chapters` 来获取预览列表，而不是把正则循环写在视图层中。

### 2.2 未使用的变量 (Unused Variables)
经扫描局部作用域，发现以下未使用变量：
- **`gui/app.py` -> `_split_thread()`**
  在第 252 行声明了 `total = len(self.parsed_chapters)`，但紧接着在下方的嵌套函数 `def update_progress(current, total):` 存在参数作用域覆盖，导致外层的 `total` 变量实际上从未被使用。虽然不会报错，但属于无用的遗留变量赋初值。

## 3. 维护操作
- 已扫描并自动删除了 `gui/app.py` 中的部分过期及占位注释（如 `# --- NEW: Options ---` 标签和 `# 2. Parse Chapters (Fix logic here)` 中的 TODO 标记）。
