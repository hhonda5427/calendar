# 実行ファイル（exe）のビルド方法

## requirements.txt の作り方

### 方法1: 手動で書く（推奨）
プロジェクトで使うパッケージを 1 行に 1 つずつ書きます。バージョンも指定できます。

```
パッケージ名
パッケージ名==1.2.3
パッケージ名>=1.0.0
```

### 方法2: 現在の環境から書き出す
いま入っているパッケージをそのまま書き出します。プロジェクト専用の venv を作ってから使うと便利です。

```bash
pip freeze > requirements.txt
```

※ 全パッケージが列挙されるため、本当に必要なものだけ残すように編集することが多いです。

### インストールするとき
```bash
pip install -r requirements.txt
```

---

## 必要なもの
- Python 3 がインストールされた PC（ビルド時のみ）
- 初回のみ: `pip install pyinstaller`

## 手順

### 方法1: バッチファイルでビルド（Windows）
```bash
build.bat
```
完了後、`dist\HolidayCalendar.exe` が作成されます。

### 方法2: 手動でコマンド実行
```bash
cd c:\Users\hhond\source\repos\calendar
pip install pyinstaller
pyinstaller --onefile --windowed --name "HolidayCalendar" --clean holiday_calendar_app.py
```

- `dist\HolidayCalendar.exe` … 単体で配布できる実行ファイル（1ファイル）
- `--windowed` … コンソール窓を出さない（GUIのみ）

## 配布のしかた
- **HolidayCalendar.exe** をそのまま渡せば、Python が入っていない PC でも実行できます。
- 同じフォルダに **tokai-calendar.csv** を置くと、起動時に自動読み込みします。
- CSV の保存・読み込みの初期フォルダは、exe があるフォルダになります。

## 注意
- exe は **Windows 用**です。Mac で使う場合は Mac 上で同じ手順でビルドしてください。
- ウイルス対策ソフトが「初回実行の不明な exe」として警告することがあります。その場合は「許可」するか、配布前にデジタル署名を検討してください。
