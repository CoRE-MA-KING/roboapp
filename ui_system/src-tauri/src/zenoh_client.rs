use zenoh::Wait;

use crate::config::get_config_path;

pub fn create_zenoh_session() -> zenoh::Session {
    let config = zenoh::config::Config::from_file(get_config_path().join("zenoh.json5"))
        .expect("Failed to load zenoh.json5 configuration file.");
    zenoh::open(config).wait().unwrap()
}
