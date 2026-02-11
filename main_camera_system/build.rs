// fn main() {
//     prost_build::compile_protos(
//         &[
//             // "../utils/proto/**/*.proto",
//             "../utils/proto/buf/validate/validate.proto",
//             "../utils/proto/roboapp/camera_port.proto",
//             "../utils/proto/roboapp/camera_switch.proto",
//             "../utils/proto/roboapp/damage_panel.proto",
//             "../utils/proto/roboapp/disks.proto",
//             "../utils/proto/roboapp/flap.proto",
//             "../utils/proto/roboapp/lidar_range.proto",
//             "../utils/proto/roboapp/lidar_vector.proto",
//             "../utils/proto/roboapp/robot_state.proto",
//         ],
//         &["../utils/proto", "src/"],
//     )
//     .unwrap();
// }

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=../utils/proto/");

    let proto_include_paths = &["../utils/proto"];
    let proto_files: Vec<_> = glob::glob("../utils/proto/**/*.proto")?
        .filter_map(Result::ok)
        .collect();

    let mut config = prost_build::Config::new();
    config.compile_well_known_types();

    config.compile_protos(&proto_files, proto_include_paths)?;

    Ok(())
}
