# -*- coding: utf-8 -*-
"""日本語を文節に切る（BudouX ＋ 後処理）2026年10月3日

REALIZE OS 採用LP 3本（careers / 100years / future-careers）で共通。
BudouX（Google製・pip install budoux）で切ったあと、誤りやすい所を直す。
- 「万が|一」「と|いう」のように語の内側で切れたものを結合する
- 1文字だけの断片や、閉じカッコ・句読点で始まる断片は前に結合する
- 長すぎる断片は「 / 」・中黒・開きカッコで割る（スマホで1つの塊が収まらないため）
"""
import re
import budoux

_parser = budoux.load_default_japanese_parser()

# この語の内側では切らない
KEEP_WORDS = ('万が一', '手がかり', 'という', 'といった', 'とともに', 'として', 'ひとつなぎ', '一人ひとり',
              'ひとつひとつ', '一つひとつ', 'かもしれません', 'かもしれない', 'ではありません',
              '子どもたち', '私たち', '自分たち',
              'REALIZE OS', 'REALIZEOS', 'LIFE JOURNEY', 'LIFE Record', 'みお先生', 'AIみお先生',
              'OSMA', 'LINE運用', '100年後', '10秒')
HEAD_NG = '、。，．！？」』）】・ー々ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ'
LONG = 12


def _cuts_inside(text, pos):
    for w in KEEP_WORDS:
        start = 0
        while True:
            i = text.find(w, start)
            if i < 0:
                break
            if i < pos < i + len(w):
                return True
            start = i + 1
    return False


def _split_long(s):
    """長い断片を「 / 」→ 開きカッコの前 → 中黒の後 の順で割る"""
    if len(s) <= LONG:
        return [s]
    if ' / ' in s or '／' in s:
        parts = re.split(r'(?<=[/／] )|(?<=／)', s)
        parts = [p for p in parts if p]
        if len(parts) > 1:
            return [q for p in parts for q in _split_long(p)]
    i = max(s.find('『'), s.find('「'))
    if i >= 2:
        return _split_long(s[:i]) + _split_long(s[i:])
    if '・' in s[:-1]:
        out, buf = [], ''
        for ch in s:
            buf += ch
            if ch == '・' and len(buf) >= 4:
                out.append(buf); buf = ''
        if buf:
            if len(buf) <= 2 and out:
                out[-1] += buf
            else:
                out.append(buf)
        if len(out) > 1:
            return out
    return [s]


def split_bunsetsu(text):
    segs = _parser.parse(text)
    out, pos = [], 0
    for s in segs:
        if out and (_cuts_inside(text, pos) or s[0] in HEAD_NG or len(s.strip()) <= 1):
            out[-1] += s
        else:
            out.append(s)
        pos += len(s)
    # 先頭が1文字だけ（要素の直後の「が|ある。」）なら次に結合する
    if len(out) > 1 and len(out[0].strip()) <= 1:
        out[1] = out[0] + out[1]
        out = out[1:]
    final = []
    for s in out:
        final += _split_long(s)
    # 1文字・禁則文字で始まる断片が割り直しで出たら前へ
    res = []
    for s in final:
        if res and (s[0] in HEAD_NG or len(s.strip()) <= 1):
            res[-1] += s
        else:
            res.append(s)
    return res


if __name__ == '__main__':
    import sys
    for t in sys.argv[1:]:
        print('|'.join(split_bunsetsu(t)))
