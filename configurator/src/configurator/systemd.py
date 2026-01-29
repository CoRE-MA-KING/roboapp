import subprocess
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from configurator.check import get_default_config_path
from configurator.config import Config


def get_service_template() -> tuple[list[Path], Path]:
    prefix = Path(__file__).parents[2] / "template" / "systemd"
    return (
        [
            prefix / "roboapp-lidar-processor.service.tmpl",
            prefix / "roboapp-main-camera-system.service.tmpl",
            prefix / "roboapp-uart-bridge.service.tmpl",
            prefix / "roboapp-ui-system.service.tmpl",
            prefix / "roboapp-zenohd.service.tmpl",
        ],
        prefix / "roboapp-lidar-sender.service.tmpl",
    )


def get_service_folder() -> Path:
    systemd_path = Path.home() / ".config" / "systemd" / "user"
    systemd_path.mkdir(parents=True, exist_ok=True)
    return systemd_path


def get_service() -> list[str]:
    ret = [
        f.stem.replace(".service", "")
        for f in get_service_folder().glob("roboapp-*.service")
    ]

    return ret


class SystemdConfig(BaseModel):
    app_folder: Path = Field(default=Path(__file__).parents[3], alias="APP_FOLDER")
    lidar_name: str = Field(default="lidar", alias="LIDAR_NAME")


def place_systemd() -> None:
    systemd_paths, lidar_sender_path = get_service_template()

    env = Environment(
        loader=FileSystemLoader((Path(__file__).parents[2] / "template" / "systemd")),
        autoescape=False,
    )

    lidar_devices: list[str] = []

    with open(get_default_config_path(), "rb") as cf:
        c = Config.model_validate(tomllib.load(cf))
        if c.lidar:
            lidar_devices = list(c.lidar.devices.keys())

    def place_single(config: SystemdConfig, file: Path, post_fix: str = "") -> None:
        template = env.get_template(file.name)
        rendered = template.render(config.model_dump(by_alias=True))

        service_name = file.stem.replace(".service", "")
        service_file_path = get_service_folder() / f"{service_name}{post_fix}.service"

        with open(service_file_path, "w") as service_file:
            service_file.write(rendered)

    config = SystemdConfig()
    for f in systemd_paths:
        place_single(config, f)

    for ln in lidar_devices:
        config_lidar = SystemdConfig(LIDAR_NAME=ln)
        place_single(config_lidar, lidar_sender_path, post_fix=f"-{ln}")

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)


def run_systemd_services(start: bool = True) -> None:
    action = "start" if start else "stop"
    for service in get_service():
        cmd = ["systemctl", "--user", action, service]
        print(f"{'Starting' if start else 'Stopping'} service: {service}, {cmd}")
        subprocess.run(cmd, check=True)


def enable_systemd_service(enable: bool) -> None:
    action = "enable" if enable else "disable"
    for service in get_service():
        cmd = ["systemctl", "--user", action, service]
        print(f"{'Enabling' if enable else 'Disabling'} service: {service}, {cmd}")
        subprocess.run(cmd, check=True)
