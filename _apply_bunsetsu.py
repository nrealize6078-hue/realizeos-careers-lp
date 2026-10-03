# -*- coding: utf-8 -*-
"""index.html の日本語を文節タグ <w-b> で包む（再実行すると剥がして貼り直す）2026年10月3日

REALIZE OS 採用LP 3本で共通。使い方: このフォルダで python _apply_bunsetsu.py
CSS は base で w-b{display:inline}、スマホ幅だけ inline-block（PC表示は変わらない）。
span を使うと既存の子孫セレクタ（.xxx span）に巻き込まれるので専用のカスタム要素にする。

リンク・ボタンなど flex の中の文字は、w-b が1つずつ flex アイテムになって
語間が開くため、まとめて <w-l> で包んでから w-b に割る。
main.js に書かれた文言（future-careers のタブ）も同じ規則で包む。
"""
import os, re, sys
from bs4 import BeautifulSoup, NavigableString
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bunsetsu import split_bunsetsu

TAG, GROUP = 'w-b', 'w-l'
SKIP_TAGS = {'script', 'style', 'title', 'svg', 'head', 'textarea', 'option'}
SKIP_CLASS = {'brand', 'brand-main', 'brand-sub', 'skip'}
GROUP_PARENTS = {'a', 'button', 'label', 'summary'}
JA = re.compile(r'[　-〿぀-ヿ一-鿿＀-￯]')
HEAD_NG = '、。，．！？」』）】・ー々'


def skip(node):
    for par in node.parents:
        if par.name in SKIP_TAGS:
            return True
        if set(par.get('class') or []) & SKIP_CLASS:
            return True
    return False


def wrap_text(text):
    """テキストを w-b の HTML 片にする。包まないなら None"""
    stripped = text.strip()
    if not stripped or not JA.search(stripped):
        return None
    segs = split_bunsetsu(stripped)
    if len(segs) <= 1 and not (2 <= len(stripped) <= 16):
        return None
    lead = text[:len(text) - len(text.lstrip())]
    tail = text[len(text.rstrip()):]
    # 文節末の空白（「LMP加盟営業 / RC…」）はタグの外に出す。
    # inline-block の中の末尾空白は描画されず、「/RC」と詰まって見えるため
    out = ''
    for s in segs:
        body = s.rstrip()
        out += f'<{TAG}>{body}</{TAG}>' + s[len(body):]
    return lead + out + tail


def apply_html(path):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    removed = 0
    for old in soup.find_all([TAG, GROUP]):
        old.unwrap(); removed += 1
    soup.smooth()

    wrapped = 0
    for node in list(soup.body.find_all(string=True)):
        if skip(node):
            continue
        frag = wrap_text(str(node))
        if frag is None:
            continue
        new = BeautifulSoup(frag, 'html.parser')
        if node.parent.name in GROUP_PARENTS or 'button' in (node.parent.get('class') or []):
            g = soup.new_tag(GROUP)
            for c in list(new.contents):
                g.append(c)
            node.replace_with(g)
        else:
            node.replace_with(new)
        wrapped += 1

    # 行頭禁則の後始末: 「…</strong>」、」のように閉じカッコ・句読点が
    # 要素の外に残ると、その文字だけ次の行に落ちる。直前の要素ごと包む。
    merged = 0
    for w in list(soup.find_all(TAG)):
        t = w.get_text()
        if not t or t[0] not in HEAD_NG:
            continue
        prev = w.previous_sibling
        if prev is None or isinstance(prev, NavigableString) or prev.name in (TAG, 'br', GROUP):
            continue
        # 直前の要素（strong 等）の最後の w-b と、この w-b の先頭の禁則文字をつなぐ
        last = prev.find_all(TAG)
        if last:
            m = re.match('[' + re.escape(HEAD_NG) + ']+', t)
            head = m.group(0)
            last[-1].append(head)
            rest = t[len(head):]
            if rest:
                w.string = rest
            else:
                w.decompose()
            merged += 1
    # 強調の直後の助詞（<span class="gold">仕組み</span>がある。）で改行しないよう、
    # 短い強調ならその要素ごと1つの文節にまとめる
    HIRA = re.compile(r'^[ぁ-ゖ]')
    glued = 0
    for w in list(soup.find_all(TAG)):
        if w.parent is None:
            continue
        t = w.get_text()
        prev = w.previous_sibling
        if (not HIRA.match(t) or prev is None or isinstance(prev, NavigableString)
                or prev.name in (TAG, 'br', GROUP) or len(prev.get_text()) > 10):
            continue
        # 助詞の部分だけ（最初の文節）を連れていく
        holder = soup.new_tag(TAG)
        prev.insert_before(holder)
        holder.append(prev.extract())
        holder.append(w.extract())
        for inner in holder.find_all(TAG):
            inner.unwrap()
        glued += 1
    soup.smooth()
    print(f'  強調＋助詞 {glued}箇所をまとめました')
    open(path, 'w', encoding='utf-8', newline='\n').write(str(soup))
    print(f'{path}: 古いタグ{removed}個を剥がし、{wrapped}箇所を文節に分割、禁則{merged}箇所を前につなぎました')


def apply_js(path):
    """main.js の文言（'…' の日本語）を包む。<br> はそのまま残す"""
    src = open(path, encoding='utf-8').read()
    n = 0

    def rep(m):
        nonlocal n
        body = re.sub(r'</?w-[bl]>', '', m.group(2))
        if not JA.search(body) or len(body) < 6:
            return m.group(0)
        parts = re.split(r'(<br>)', body)
        out = ''.join(p if p == '<br>' else (wrap_text(p) or p) for p in parts)
        n += 1
        return m.group(1) + "'" + out + "'"
    key = re.compile(r"((?:title|description|question):)'([^']*)'")
    src = key.sub(rep, src)
    open(path, 'w', encoding='utf-8', newline='\n').write(src)
    print(f'{path}: {n}個の文言を包みました')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    apply_html('index.html')
    if os.path.exists('main.js'):
        apply_js('main.js')
