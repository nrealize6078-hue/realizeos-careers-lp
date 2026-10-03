# -*- coding: utf-8 -*-
"""スマホで見出しの改行を <br> の位置にそろえる data-fit を付ける（2026年10月3日）

FIT は 320px 幅で「<br> どおりの行数に収まる最大の文字サイズ」を二分探索で測り、
×0.97 ÷ 3.2 で vw にしたもの。上限（cap）は 430px 幅での元のサイズ。
縮小が 78% 未満になるもの（長い本文など）は対象外で、文節の折り返しに任せる。
文章を変えたら測り直すこと。CSS は末尾の [data-fit]。先に _apply_bunsetsu.py を実行する。
"""
from bs4 import BeautifulSoup
SEL = 'h1,h2,h3,p,dd,summary,figcaption'
# (要素の番号, 先頭の文字, vw, 上限px)
FIT = [[8, "相談を、実際の支", 6.25, 24], [11, "自分の人生を考え", 6.335, 24], [14, "あなたの得意が、", 8.487, 29], [15, "人と話す。考える", 4.619, 16], [26, "加盟してから。導", 4.15, 16], [35, "心が動くきっかけ", 4.686, 16], [59, "あなたの工夫が、", 5.786, 23], [65, "AIと人生支援を", 6.284, 23], [72, "会社の未来に、自", 7.866, 29], [75, "事業とお客様を知", 4.374, 16], [77, "担当する仕事を持", 4.756, 16], [79, "経験を仲間につな", 4.374, 16], [97, "仕事の合間にも、", 4.783, 16], [112, "広げる。育てる。", 4.165, 16]]
soup = BeautifulSoup(open('index.html', encoding='utf-8').read(), 'html.parser')
els = soup.select(SEL)
for el in els:
    if el.has_attr('data-fit'):
        del el['data-fit']; del el['style']
for idx, head, vw, cap in FIT:
    el = els[idx]
    assert el.get_text().strip().startswith(head), (idx, head, el.get_text()[:10])
    el['data-fit'] = ''
    el['style'] = f'--fit:{vw}vw;--fit-cap:{cap}px'
open('index.html', 'w', encoding='utf-8', newline=chr(10)).write(str(soup))
print(f'{len(FIT)}要素に data-fit を付けました')
