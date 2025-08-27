use zenoh::Wait;

pub fn create_zenoh_session() -> zenoh::Session {
    let config = zenoh::Config::default();
    zenoh::open(config).wait().unwrap()
}
