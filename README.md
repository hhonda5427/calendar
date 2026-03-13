# calendar

## 休日カレンダーアプリ（holiday_calendar_app.py）

日付・休日名の入ったCSVを作成するデスクトップアプリです。

### 機能
- カレンダー表示（月の前後移動）
- 日付をクリックして休日名を入力・編集・削除
- 登録した休日一覧の表示・選択削除
- **CSVに保存**：日付と休日名の2列CSVを出力（UTF-8 BOM付き）
- **CSVを読み込み**：既存のCSVから休日を読み込み

### 実行方法
```bash
python holiday_calendar_app.py
```
Python 3 のみ使用（Tkinter は標準ライブラリのため追加インストール不要）
