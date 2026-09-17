# -*- coding: utf-8 -*-
"""見出し・本文を文節タグ <w-b> で包む（再実行すると貼り直す）

span ではなく専用のカスタム要素を使う。既存CSSの子孫セレクタ
（.xxx span{...}）に巻き込まれて色やサイズが変わるのを避けるため。
"""
import re, sys
from bs4 import BeautifulSoup
sys.path.insert(0, '.')
from _bunsetsu import split_bunsetsu

TAG = 'w-b'
# h1 は <span> で改行位置を作り込んであるので触らない
TARGET = ('h2,h3,p,summary,dd,dt,li,'
          '.intro-band span,.hero-caption span,.job-card h3>span,.entry-example')
SKIP_PARENT = {'a', 'script', 'style', 'button', 'title', 'h1'}
SKIP_CLASS = {'eyebrow', 'section-kicker', 'job-english', 'business-mark',
              'business-tags', 'theme-line', 'step-num', 'job-index'}
JA = re.compile(r'[぀-ヿ一-鿿]')

def has_skip_ancestor(node):
    for par in node.parents:
        if par.name in SKIP_PARENT:
            return True
        if set(par.get('class') or []) & SKIP_CLASS:
            return True
    return False

def main():
    soup = BeautifulSoup(open('index.html', encoding='utf-8').read(), 'html.parser')
    removed = 0
    for old in soup.find_all(TAG):
        old.unwrap(); removed += 1
    soup.smooth()

    wrapped = 0
    for el in soup.select(TARGET):
        for node in list(el.find_all(string=True)):
            text = str(node)
            if not JA.search(text) or not text.strip() or has_skip_ancestor(node):
                continue
            segs = split_bunsetsu(text.strip())
            if len(segs) <= 1:
                continue
            lead = text[:len(text) - len(text.lstrip())]
            tail = text[len(text.rstrip()):]
            frag = lead + ''.join(f'<{TAG}>{s}</{TAG}>' for s in segs) + tail
            node.replace_with(BeautifulSoup(frag, 'html.parser'))
            wrapped += 1
    open('index.html', 'w', encoding='utf-8', newline='\n').write(str(soup))
    print(f'古いタグ{removed}個を剥がし、{wrapped}箇所を文節に分割しました')

main()
