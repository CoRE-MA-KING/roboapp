use crate::config::get_config_path;
use zenoh::Wait;

pub fn create_zenoh_session() -> zenoh::Result<zenoh::Session> {
    let config = zenoh::config::Config::from_file(get_config_path().join("zenoh.json5"))?;
    zenoh::open(config).wait()
}
