# REALIZE OS 採用LP

「あなたの一歩が、この会社の未来になる。」

- 公開URL: https://nrealize6078-hue.github.io/realizeos-careers-lp/
- 元サイト: https://realizeos-careers.uminchu-t0422.chatgpt.site/ （ChatGPT製。2026年9月17日に複製して自前管理へ移行）
- ローカルプレビュー: `.claude/launch.json` の `careers-lp`（ポート8972）

## 構成

| ファイル | 中身 |
|---|---|
| `index.html` | 本文・見出し・全セクションの文言 |
| `styles.css` | 配色・余白・レイアウト（`:root` にCSS変数） |
| `script.js` | スクロール連動などの動作 |
| `assets/` | ヒーロー画像・ジム写真 |

## 編集方法

1. このフォルダのファイルを直接編集する
2. `git commit` して `git push` すると、1〜2分でGitHub Pagesに反映される

元サイト（chatgpt.site）とは**別物**。こちらを直しても元サイトは変わらない。

## 複製時の変更点

- 絶対パス（`/styles.css` 等）を相対パスへ変更
- `canonical` と `og:url` を公開先URLへ変更
