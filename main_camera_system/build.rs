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

use protocheck_build::compile_protos_with_validators;
use tonic_prost_build::Config;

// ref: https://github.com/Rick-Phoenix/protocheck-tonic-svelte-example/blob/main/server/build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=proto/");

    let out_dir =
        std::path::PathBuf::from(std::env::var("OUT_DIR").expect("Could not find OUT_DIR"));
    let final_descriptor_path = out_dir.join("tonic_descriptor.bin");

    let mut config = Config::new();
    config
        .file_descriptor_set_path(final_descriptor_path.clone())
        .bytes(["."])
        .out_dir(out_dir.clone());

    let proto_include_paths = &["../utils/proto"];

    let proto_files = &[
        "../utils/proto/buf/validate/validate.proto",
        "../utils/proto/roboapp/camera_port.proto",
        "../utils/proto/roboapp/camera_switch.proto",
        "../utils/proto/roboapp/damage_panel.proto",
        "../utils/proto/roboapp/disks.proto",
        "../utils/proto/roboapp/flap.proto",
        "../utils/proto/roboapp/lidar_range.proto",
        "../utils/proto/roboapp/lidar_vector.proto",
        "../utils/proto/roboapp/robot_state.proto",
    ];

    compile_protos_with_validators(
        &mut config,
        proto_files,
        proto_include_paths,
        &["user.v1", "weather.v1"],
    )?;

    // Compile protos
    tonic_prost_build::configure()
        .build_client(false)
        .compile_with_config(config, proto_files, proto_include_paths)?;

    // Set the env for the file descriptor location
    println!(
        "cargo:rustc-env=PROTO_DESCRIPTOR_SET={}",
        final_descriptor_path.display()
    );

    Ok(())
}
