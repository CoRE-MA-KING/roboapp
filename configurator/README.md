# Configurator

roboapp の設定ファイルを検査・生成するツールです。

## 使い方

`uv run python3 check.py` で実行します。

### オプション

`-c` or `--config` : 設定ファイルのパスを指定します。省略した場合、`$XDG_CONFIG_HOME/roboapp/config.toml` or `$HOME/.config/roboapp/config.toml` を使用します。

正常実行できれば、設定ファイルは問題ありません。

エラーがでた場合、エラーメッセージに従って設定ファイルを修正してください。（Pydantic のバリデーションエラーが表示されます）
