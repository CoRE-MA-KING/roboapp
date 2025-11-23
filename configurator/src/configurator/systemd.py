import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, field_validator


def get_service_template() -> list[Path]:
    return list(
        (Path(__file__).parents[2] / "template" / "systemd").glob("*.service.tmpl")
    )


def get_service_folder() -> Path:
    systemd_path = Path.home() / ".config" / "systemd" / "user"
    systemd_path.mkdir(parents=True, exist_ok=True)
    return systemd_path


def get_service() -> list[str]:
    return [
        f.stem.replace(".service", "")
        for f in get_service_folder().glob("roboapp-*.service")
    ]


class SystemdConfig(BaseModel):
    uv_path: Path = Field(Path().home() / ".local" / "bin" / "uv", alias="UV_PATH")
    app_folder: Path = Field((Path(__file__).parents[3]), alias="APP_FOLDER")

    @field_validator("uv_path")
    def set_uv_path(cls, v: Path) -> Path:
        if v.exists():
            return v

        if uv := shutil.which("uv"):
            return Path(uv)
        raise FileNotFoundError("uv not found")


def place_systemd() -> None:
    config = SystemdConfig()  # type:ignore

    systemd_path = get_service_folder()

    env = Environment(
        loader=FileSystemLoader((Path(__file__).parents[2] / "template" / "systemd")),
        autoescape=False,
    )
    for f in get_service_template():
        template = env.get_template(f.name)
        rendered = template.render(config.model_dump(by_alias=True))

        service_name = f.stem.replace(".service", "")
        service_file_path = systemd_path / f"{service_name}.service"

        with open(service_file_path, "w") as service_file:
            service_file.write(rendered)

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)


def run_systemd_services(start: bool = True) -> None:
    for service in get_service():
        cmd = ["systemctl", "--user", ("stop", "start")[start], "--now", service]
        print(f"Starting service: {service}, {cmd}")
        subprocess.run(cmd, check=True)


def enable_systemd_service(enable: bool) -> None:
    for service in get_service():
        cmd = ["systemctl", "--user", ("disable", "enable")[enable], "--now", service]
        print(f"Running command: {cmd}")
        subprocess.run(cmd, check=True)
