# 🌙 ArtéMis CERS

**Cultural Experience Record System**

Notionをバックエンドにした、鑑賞/体験記録の管理アプリです。  
映画・ドラマ・アニメ・書籍・漫画・音楽アルバム・ゲーム・演奏会・展示会・ライブ/ショー・演奏曲に対応しています。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://artemis-cers.streamlit.app)

---

## 📘 User Guide

操作マニュアルは以下を参照してください。

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)

アプリ画面のサイドバーからも閲覧できます（`📘 操作ガイド`）。

---

## ✨ Features

- 媒体ごとのメタデータ検索（TMDB / AniList / Rakuten / OpenLibrary / iTunes / IGDB / MusicBrainz）
- Notionカバー更新とDriveバックアップ
- 複数件カート登録（一括登録）
- ロケーション検索とNotion place保存
- 既存データのリフレッシュ同期
- 演奏会（出演）と演奏曲のリレーション連携

---

## ⚠️ Schema Notes

- 現行仕様の媒体判定は `媒体` を基準にしています。
- `MEDIA_TYPE` は運用から外し、Notion側でも削除予定/削除済みの前提です。

---

## 🛠 Setup (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

必要なSecretsは `.streamlit/secrets.toml` に設定してください。

