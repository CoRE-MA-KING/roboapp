from pathlib import Path

from prompt_toolkit.shortcuts import (
    input_dialog,
    radiolist_dialog,
)

from configurator.check import check, get_default_config_path
from configurator.systemd import (
    enable_systemd_service,
    place_systemd,
    run_systemd_services,
)

if __name__ == "__main__":
    tasks = (
        ("config", "設定ファイルの検証"),
        ("install", "起動設定のインストール"),
        ("start", "Roboappの起動・停止"),
        ("setup", "Roboappの自動起動の設定・解除"),
    )

    result = radiolist_dialog(
        title="Roboapp Configurator",
        text="実行内容を選んでください",
        values=tasks,
        default=tasks[0][0],
    ).run()

    match result:
        case "config":
            target: str | None = input_dialog(
                title="設定ファイルの検証",
                text="設定ファイルのパスを入力してください:",
                default=str(get_default_config_path()),
            ).run()
            if not target:
                exit(0)
            check(Path(target))
        case "install":
            place_systemd()
        case "start":
            res_start: bool | None = radiolist_dialog(
                title="Roboappの起動・停止",
                text="Roboappを起動しますか？",
                values=[(True, "起動"), (False, "停止")],
                default=True,
            ).run()
            if res_start is None:
                exit(0)

            run_systemd_services(res_start)
        case "setup":
            res_setup: bool | None = radiolist_dialog(
                title="Roboappの自動起動の設定・解除",
                text="Roboappの自動起動を設定しますか？",
                values=[(True, "設定"), (False, "解除")],
                default=True,
            ).run()
            if res_setup is None:
                exit(0)

            enable_systemd_service(res_setup)
        case _:
            pass
