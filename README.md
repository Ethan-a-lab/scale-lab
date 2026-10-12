# 权衡 Scale Lab · 我的手写项目

**权衡**（Scale Lab），副标题「金融伦理决策实验室」。

天平既是金融符号也是司法符号，「权衡」两个字字面就是"两难之间怎么选"——正好是本站核心
模块「伦理决策沙盘」在做的事。取这个名字是为了：申报材料里不用再解释站名，名字自己会说话。

> 上线网址（Publish 后生效）：`https://ethan-a-lab.github.io/scale-lab/`
> 仓库位置：`D:\Github\scale-lab`（已 `git init`，可用 GitHub Desktop 打开）
> 教材素材：`D:\读研文件\金融监管、金融伦理、职业道德智能体\`
> （《金融伦理与职业道德》《金融监管》两本 PDF —— 版权受限，**内容不随仓库分发**，只放本地参考，
> 站内只放你自己整理的知识点与公开案例）

## 一、目录约定（先按这个来，别乱放）

```
scale-lab/
├── index.html          # 全部页面结构（先写这一个）
├── static/
│   ├── style.css       # 全部样式
│   └── app.js          # 全部交互
├── assets/             # 图片之类（前期用不上）
├── check.py            # 自检脚本（老师给的工具，别改）
└── README.md
```

**为什么拆成 3 个文件？** ibank 是 221KB 的单文件，改个按钮要翻 1874 行。
你从一开始就把结构 / 样式 / 行为分开 —— 这一处你比 ibank 做得更对。

## 二、怎么预览

| 方式 | 操作 | 什么时候用 |
|---|---|---|
| 双击 | 直接双击 `index.html` | 快速看一眼 |
| Live Server（推荐） | VS Code 里右键 `index.html` → **Open with Live Server** | 写代码时，保存即自动刷新 |

## 三、怎么自检（写完就跑）

在项目目录里打开终端，运行（二选一，哪个能跑用哪个）：

```bash
python check.py
```

```bash
/c/Users/王爱民/.workbuddy/binaries/python/versions/3.13.12/python.exe check.py
```

输出里 `[✓]` 是通过，`[✗]` 是没做到，后面跟着该补什么。
**脚本只查结构和语法，不评判好不好看。** 如果你用了不同的类名导致误报 `[✗]`，
确认功能真的实现了就算过。

## 四、怎么存版本（每完成一个里程碑就做一次）

仓库已经初始化好了，直接提交就行：

```bash
git add .
git commit -m "M0 项目骨架完成"
```

用 **GitHub Desktop** 更省事：File → Add local repository → 选中 `D:\Github\scale-lab`，
左下角写 Summary → Commit to main。想备份到云端再点 Publish repository。

**如果误把教材 PDF 拖进来了**：`.gitignore` 已经拦住 `assets/` 和 `*.pdf`，
用 `git status` 应该看不到它们。**看到才说明拦住了** —— 一旦在 status 里露面，先别 commit，来问我。

**为什么每个里程碑都要提交？** 你会改坏它。有了 commit，随时能 `git checkout .` 回到上一个能跑的版本。
这是你敢大胆乱改的底气。

## 五、三条铁律

1. **手敲，不复制** —— 复制粘贴只练了鼠标。
2. **先让它坏，再让它对** —— 报错不可怕，看不懂报错才可怕。F12 → Console 是你老师。
3. **不污染 ibank** —— ibank 在申报中，改动只发生在这个目录里。
