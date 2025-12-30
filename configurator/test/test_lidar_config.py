import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from configurator.config import Config


@pytest.fixture
def get_resource_path() -> Path:
    return Path(__file__).parent / "resources"


def test_lidar_config_default_success(get_resource_path: Path) -> None:
    """デフォルト設定(random)は成功する"""
    config_file = get_resource_path / "lidar_config_default.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))

    assert config.lidar is not None
    dev = config.lidar.devices.get("random")
    assert dev is not None
    assert dev.backend == "random"
    assert dev.x == 0
    assert dev.y == 0
    assert dev.device is None


def test_lidar_device_config_random_success(get_resource_path: Path) -> None:
    """Randomバックエンドの設定確認"""
    config_file = get_resource_path / "lidar_device_config_random.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))

    dev = config.lidar.devices["random"]
    assert dev.backend == "random"


def test_lidar_device_config_rplidar_with_device_success(
    get_resource_path: Path,
) -> None:
    """rplidarでdevice指定ありなら成功"""
    config_file = get_resource_path / "lidar_device_config_rplidar_with_device.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))

    dev = config.lidar.devices["rplidar"]
    assert dev.backend == "rplidar"
    assert dev.device == "/dev/ttyUSB0"
    # x, y はデフォルト0
    assert dev.x == 0
    assert dev.y == 0


def test_lidar_device_config_rplidar_with_no_device_raises_error(
    get_resource_path: Path,
) -> None:
    """rplidarバックエンドでdeviceがない場合はエラー"""
    config_file = get_resource_path / "lidar_device_config_rplidar_with_no_device.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError) as excinfo:
            Config.model_validate(tomllib.load(f))

    # エラーメッセージに "RPLIDAR backend requires a device path" が含まれるか確認
    assert "RPLIDAR backend requires a device path" in str(excinfo.value)


def test_lidar_config_extra_field_raises_error(get_resource_path: Path) -> None:
    """未定義のフィールドがあるためエラー"""
    config_file = get_resource_path / "lidar_config_robot_length.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError) as excinfo:
            Config.model_validate(tomllib.load(f))

    errors = excinfo.value.errors()
    # extra_forbidden エラーを確認
    # LidarConfigに robot_length というフィールドはないのでエラーになるはず
    extra_fields = {e["loc"][-1] for e in errors if e["type"] == "extra_forbidden"}
    assert "robot_length" in extra_fields


def test_lidar_config_robot_width_raises_error(get_resource_path: Path) -> None:
    """robot_widthフィールドは未定義のためエラー"""
    config_file = get_resource_path / "lidar_config_robot_width.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError) as excinfo:
            Config.model_validate(tomllib.load(f))

    errors = excinfo.value.errors()
    extra_fields = {e["loc"][-1] for e in errors if e["type"] == "extra_forbidden"}
    assert "robot_width" in extra_fields


def test_lidar_config_influence_range_raises_error(get_resource_path: Path) -> None:
    """influence_rangeフィールドは未定義のためエラー"""
    config_file = get_resource_path / "lidar_config_influence_range.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError) as excinfo:
            Config.model_validate(tomllib.load(f))

    errors = excinfo.value.errors()
    extra_fields = {e["loc"][-1] for e in errors if e["type"] == "extra_forbidden"}
    assert "influence_range" in extra_fields


def test_lidar_config_repulsive_gain_raises_error(get_resource_path: Path) -> None:
    """repulsive_gainフィールドは未定義のためエラー"""
    config_file = get_resource_path / "lidar_config_repulsive_gain.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError) as excinfo:
            Config.model_validate(tomllib.load(f))

    errors = excinfo.value.errors()
    extra_fields = {e["loc"][-1] for e in errors if e["type"] == "extra_forbidden"}
    assert "repulsive_gain" in extra_fields


def test_lidar_device_config_random_rotate_success(get_resource_path: Path) -> None:
    """rotateパラメータの指定が正常に読み込めることの確認"""
    config_file = get_resource_path / "lidar_device_config_random_rotate.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))

    assert config.lidar is not None
    dev = config.lidar.devices["random"]
    assert dev.rotate == 45


def test_lidar_config_valid_dict() -> None:
    """正常な設定データを用いたテスト(Dict入力)"""
    valid_data = {
        "lidar": {
            "devices": {
                "front": {
                    "device": "/dev/ttyUSB0",
                    "backend": "rplidar",
                    "x": 100,
                    "y": 0,
                    "min_degree": 90,
                    "max_degree": 270,
                    "max_distance": 2000,
                }
            }
        }
    }
    config = Config.model_validate(valid_data)
    assert config.lidar is not None
    assert config.lidar.devices["front"].device == "/dev/ttyUSB0"
    assert config.lidar.devices["front"].x == 100