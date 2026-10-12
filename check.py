#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融伦理智慧课堂 · 里程碑自检脚本（自动批改）

用法：
  1) 在本项目目录（ethics-site）里打开终端
  2) 运行：python check.py
  3) 看输出：[✓] 是通过，[✗] 是没做到，按提示改完再跑

说明：脚本只做「结构与语法」层面的检查，不评判你的设计好不好看。
     有些项你用了不同的命名（比如卡片类名不叫 case），脚本可能误报 [✗]，
     那种情况你自己确认功能真的实现了，就算过。
"""
import os
import re
import sys
import glob
import tempfile
import subprocess
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
VOID = {'meta', 'link', 'br', 'hr', 'img', 'input', 'source', 'area',
        'base', 'col', 'embed', 'param', 'track', 'wbr'}

# node.exe 候选路径：优先系统 PATH，其次 WorkBuddy 托管版本
NODE_CANDIDATES = [
    'node',
    r'C:\Users\王爱民\.workbuddy\binaries\node\versions\22.22.2-6\node.exe',
    r'D:\nodejs\node.exe',
]
_NODE = None


def find_node():
    global _NODE
    if _NODE:
        return _NODE
    for c in NODE_CANDIDATES:
        try:
            r = subprocess.run([c, '-v'], capture_output=True, text=True)
            if r.returncode == 0:
                _NODE = c
                return c
        except Exception:
            continue
    return None


class TagChecker(HTMLParser):
    """检查 HTML 标签是否成对闭合"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errs = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errs.append(f'多出一个 </{tag}>（第 {self.getpos()[0]} 行）')
            return
        t, line = self.stack.pop()
        if t != tag:
            self.errs.append(f'<{t}>（第 {line} 行）被 </{tag}>（第 {self.getpos()[0]} 行）关掉了，不匹配')


def read(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def html_ok(text):
    """剥离 script/pre/textarea 内容后检查标签平衡"""
    s = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.S)
    s = re.sub(r'<pre[^>]*>.*?</pre>', '', s, flags=re.S)
    s = re.sub(r'<textarea[^>]*>.*?</textarea>', '', s, flags=re.S)
    p = TagChecker()
    p.feed(s)
    if p.errs:
        return False, '；'.join(p.errs[:3])
    if p.stack:
        return False, '未闭合：' + ', '.join(f'<{t}>（第 {l} 行）' for t, l in p.stack[:3])
    return True, ''


def js_ok(code):
    """把 JS 交给 node --check 验语法"""
    node = find_node()
    if not node:
        return None, '没找到 node，跳过语法检查（装 Node.js 后会生效）'
    fd, tmp = tempfile.mkstemp(suffix='.js', text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
        r = subprocess.run([node, '--check', tmp], capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            msg = (r.stderr or '').strip().splitlines()
            return False, msg[-1] if msg else '语法错误'
        return True, ''
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass


def collect_js():
    """收集项目里所有 JS：内联 + 外部文件"""
    out = []
    html = read(os.path.join(ROOT, 'index.html'))
    for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, flags=re.S):
        out.append(('index.html 内联脚本', m.group(1)))
    for p in glob.glob(os.path.join(ROOT, '**', '*.js'), recursive=True):
        if 'node_modules' in p:
            continue
        code = read(p)
        if code.strip():
            out.append((os.path.relpath(p, ROOT), code))
    return out


def count(text, *patterns):
    """任一模式命中即算有"""
    return any(re.search(p, text, flags=re.I | re.S) for p in patterns)


# ============ 里程碑定义 ============
# 每项：(说明, 判定函数返回 bool/None, 失败提示)
def build_milestones(ctx):
    html, css, js_all = ctx['html'], ctx['css'], ctx['js_all']
    files = ctx['files']
    has = lambda name: name in files

    M = []

    M.append(('M0 · 项目骨架', [
        ('index.html 已创建', has('index.html'), '先建 index.html'),
        ('声明了 <!DOCTYPE html>', count(html, r'<!DOCTYPE\s+html>'), '第一行写 <!DOCTYPE html>'),
        ('有导航栏 <nav>', count(html, r'<nav[\s>]'), '用 <nav> 包住导航按钮'),
        ('有 3 个以上页面区块 class="page"',
         len(re.findall(r'class="[^"]*\bpage\b', html)) >= 3, '每个页面一个 <section class="page" id="p-xxx">'),
        ('按钮上贴了 data-page',
         count(html, r'data-page='), '给导航按钮加 data-page="p-xxx"（第 1 课讲过）'),
        ('CSS 单独放一个文件并用 <link> 引入',
         has('style.css') and count(html, r'<link[^>]+stylesheet'), '建 static/style.css，用 <link rel="stylesheet"> 引'),
        ('CSS 里定义了 :root 变量', count(css, r':root\s*\{'), '把颜色写成变量（第 1 课讲过为什么）'),
        ('写了 .page / .page.active 显隐规则',
         count(css, r'\.page[^{]*\{[^}]*display\s*:\s*none') and count(css, r'\.page\.active'),
         '只显示带 active 的页面'),
        ('JS 文件已引入并监听点击',
         has('app.js') and count(js_all, r"addEventListener\(\s*['\"]click"), '用 addEventListener 而不是 onclick='),
        ('HTML 标签全部闭合', ctx['html_ok'][0], ctx['html_ok'][1] or '标签没配对，看 F12 Console'),
        ('JS 语法无错误', ctx['js_ok'][0] is not False, ctx['js_ok'][1] or '语法错误'),
    ]))

    M.append(('M1 · 布局与响应式', [
        ('用了 flex 或 grid 排版', count(css, r'display\s*:\s*(flex|grid)'), '第 2 课内容：卡片用 grid 排'),
        ('有 @media 响应式断点', count(css, r'@media'), '窄屏时改成单列'),
        ('容器限定了最大宽度', count(css, r'max-width'), '内容区 max-width: 1100px 左右'),
    ]))

    M.append(('M2 · 深色模式', [
        ('CSS 里有 body.dark 变量覆盖', count(css, r'body\.dark'), '只换变量值，不换规则'),
        ('JS 里用了 classList.toggle', count(js_all, r'classList\.toggle'), '切 body 上的 dark 类'),
        ('选择被 localStorage 记住', count(js_all, r'localStorage\.setItem'), '刷新后主题还在才算完成'),
    ]))

    M.append(('M3 · 内容填充', [
        ('页面区块达到 5 个以上',
         len(re.findall(r'class="[^"]*\bpage\b', html)) >= 5, '按你的教材目录补齐章节页'),
        ('有章节标题结构（h2/h3）', count(html, r'<h[23][\s>]'), '每个章节一个标题'),
        ('有案例或知识点区块', count(html, r'class="[^"]*(case|chapter|card)'), '案例卡 / 章节卡'),
    ]))

    M.append(('M4 · 交互功能', [
        ('有搜索或筛选输入框', count(html, r'<input[^>]+type="(text|search)"'), '案例库搜索框'),
        ('监听了 input 事件', count(js_all, r"addEventListener\(\s*['\"]input"), '输入即筛'),
        ('用了 querySelectorAll 批量操作',
         count(js_all, r'querySelectorAll'), '别一个个 getElementById'),
    ]))

    M.append(('M5 · 数据与表单', [
        ('有 <form> 表单', count(html, r'<form[\s>]'), '做题 / 反馈表单'),
        ('JS 里存了 JSON 数据', count(js_all, r'JSON\.(parse|stringify)'), '对象数组 + JSON 持久化'),
        ('读取了 localStorage 做恢复', count(js_all, r'localStorage\.getItem'), '关掉再开数据还在'),
    ]))

    M.append(('M6 · 图表与题库', [
        ('出现 <svg> 或 <canvas>', count(html, r'<(svg|canvas)[\s>]'), '手画一张图（雷达/柱状）'),
        ('JS 里定义了 5 个以上函数',
         len(re.findall(r'function\s+\w+|=>\s*\{', js_all)) >= 5, '把逻辑拆成小函数'),
        ('有判分或统计逻辑', count(js_all, r'(score|correct|right|统计|判分)'), '题库要能判对错'),
    ]))

    return M


def main():
    html = read(os.path.join(ROOT, 'index.html'))
    css = read(os.path.join(ROOT, 'static', 'style.css'))
    if not css:
        css = read(os.path.join(ROOT, 'style.css'))

    files = set()
    for p in glob.glob(os.path.join(ROOT, '**', '*'), recursive=True):
        if os.path.isfile(p):
            files.add(os.path.relpath(p, ROOT).replace('\\', '/'))
            files.add(os.path.basename(p))

    js_all = '\n'.join(c for _, c in collect_js())

    print('=' * 56)
    print(' 金融伦理智慧课堂 · 里程碑自检')
    print('=' * 56)

    if not html:
        print('\n还没找到 index.html —— 先按任务书完成 M0 再回来跑我。\n')
        return

    print('\n--- 基础检查 ---')
    ok, msg = html_ok(html)
    print(f'[{"✓" if ok else "✗"}] index.html 结构{"正常" if ok else "有问题： " + msg}')
    jok, jmsg = js_ok(js_all) if js_all.strip() else (None, '还没有 JS')
    if jok is True:
        print('[✓] JS 语法全部通过')
    elif jok is None:
        print(f'[-] {jmsg}')
    else:
        print(f'[✗] JS 语法错误：{jmsg}')

    ctx = {'html': html, 'css': css, 'js_all': js_all, 'files': files,
           'html_ok': (ok, msg), 'js_ok': (jok, jmsg)}

    milestones = build_milestones(ctx)
    done_level = -1
    print('\n--- 里程碑 ---')
    for i, (name, items) in enumerate(milestones):
        passed = 0
        fails = []
        for desc, ok_, tip in items:
            if ok_ is None or ok_ is True:
                passed += 1
            else:
                fails.append((desc, tip))
        total = len(items)
        flag = '✓ 达成' if passed == total else (f'{passed}/{total}')
        print(f'\n{name}  [{flag}]')
        for d, t in fails:
            print(f'   [✗] {d}  →  {t}')
        if passed == total:
            done_level = i

    print('\n' + '=' * 56)
    if done_level < 0:
        nxt = milestones[0][0]
        print('还没达成任何里程碑。先把 M0 做完。')
    elif done_level == len(milestones) - 1:
        print('全部里程碑达成 —— 这个站可以拿去申报了。')
    else:
        nxt = milestones[done_level + 1][0]
        print(f'最高达成：{milestones[done_level][0]}')
        print(f'下一个目标：{nxt}')
    print('=' * 56 + '\n')


if __name__ == '__main__':
    main()
