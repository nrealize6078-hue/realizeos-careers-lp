# -*- coding: utf-8 -*-
"""日本語を文節っぽい単位に切る（形態素解析なし・切らない側に倒す）"""
import re

KANJI = r'一-鿿々'
KATA  = r'ァ-ヶー'
# 助詞の直前に来てよい文字。ひらがなが続く途中では切らない（「ひとつ」の「と」対策）
PREV  = rf'[{KANJI}{KATA}0-9A-Za-z）」』】]'
JOSHI = r'(?:により|による|によって|として|について|に対して|からは|までは|には|へは|とは|では|から|まで|より|など|ほど|だけ|こそ|しか|[がをにへとはもでやかの])'
# 助詞の直後がこれらで始まるときは動詞・補助用言が続くとみなして切らない
NOCUT = ('される','されて','され','した','して','しま','する','すれ','しれ',
         'なる','なっ','なり','なろ','ない','なく','いう','いく','いる','いた',
         'おり','おい','よる','より','あり','ある','きる','つい','対し','関し','向け','言',
         'す','し','せ','そう','き','く','け')  # 「大丈夫で|すか？」のような助動詞の切断を防ぐ
CLOSERS = '」』）】"\''
PUNCT = '、。！？'
FOLLOW_NG = 'のはもがをにへとでやか'  # 切った直後がこの助詞なら切らない（「家族と|の接点へ」を防ぐ）

def split_bunsetsu(text):
    # 1) 句読点の後で切る（続く閉じ括弧は前に含める）
    parts, buf, i = [], '', 0
    while i < len(text):
        ch = text[i]; buf += ch; i += 1
        if ch in PUNCT:
            while i < len(text) and text[i] in CLOSERS:
                buf += text[i]; i += 1
            parts.append(buf); buf = ''
    if buf:
        parts.append(buf)
    # 2) 助詞の後で切る
    out = []
    for p in parts:
        segs, last = [], 0
        for m in re.finditer(rf'(?<={PREV}){JOSHI}', p):
            end = m.end()
            if end >= len(p) or p[end] in PUNCT or p[end] in CLOSERS:
                continue
            if p[end:].startswith(NOCUT) or p[end] in FOLLOW_NG:
                continue
            segs.append(p[last:end]); last = end
        segs.append(p[last:])
        out += [s for s in segs if s]
    # 3) 長すぎる文節は、ひらがなの直後でも切る緩いルールで割り直す
    LIMIT = 10
    relaxed = []
    for seg in out:
        if len(seg) <= LIMIT:
            relaxed.append(seg); continue
        sub, last = [], 0
        for m in re.finditer(JOSHI, seg):
            end = m.end()
            if end >= len(seg) or seg[end] in PUNCT or seg[end] in CLOSERS:
                continue
            if seg[end:].startswith(NOCUT) or seg[end] in FOLLOW_NG:
                continue
            if m.group(0) in 'かや':   # 「するか」「AやB」は単独で切ると不自然
                continue
            if end - last < 3:        # 細かく刻みすぎない
                continue
            sub.append(seg[last:end]); last = end
        sub.append(seg[last:])
        relaxed += [x for x in sub if x]
    out = relaxed
    # 4) 1文字の断片は前にくっつける
    merged = []
    for s in out:
        if merged and len(s.strip()) <= 1:
            merged[-1] += s
        else:
            merged.append(s)
    return merged
