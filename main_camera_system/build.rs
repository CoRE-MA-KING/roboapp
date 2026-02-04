// In your build.rs file
use prost_build::Config;
use protocheck_build::compile_protos_with_validators;
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("cargo:rerun-if-changed=proto/");

    let out_dir = PathBuf::from("src/proto");

    let descriptor_path = out_dir.join("file_descriptor_set.bin");

    let proto_include_paths = &["../message/proto"];

    // Use the helper to get all proto files recursively in a directory
    // let proto_files = get_proto_files_recursive("proto")?;
    let proto_files = [
        "../message/proto/roboapp/camera_port.proto",
        "../message/proto/roboapp/camera_switch.proto",
        // 必要なprotoファイル
    ];

    let mut config = Config::new();
    config
        .file_descriptor_set_path(&descriptor_path)
        // Enable the use of bytes::Bytes for `bytes` fields
        .bytes(["."])
        .out_dir(&out_dir);

    // Call the build helper
    compile_protos_with_validators(&mut config, &proto_files, proto_include_paths, &["roboapp"])?;

    // Compile protos
    config.compile_protos(&proto_files, proto_include_paths)?;

    // Set the env for the file descriptor location
    println!(
        "cargo:rustc-env=PROTO_DESCRIPTOR_SET={}",
        descriptor_path.display()
    );

    Ok(())
}

// use prost_build::Config;
// use protocheck_build::compile_protos_with_validators;

// fn main() {
//     let proto_files = [
//         "../message/proto/roboapp/camera_port.proto",
//         "../message/proto/roboapp/camera_switch.proto",
//         // 必要なprotoファイル
//     ];
//     let proto_include_paths = &["../message/proto"];

//     // validator対象のパッケージ名リスト
//     let validator_packages = &["roboapp"];

//     let mut config = Config::new();
//     config.out_dir("src/proto/roboapp");
//     compile_protos_with_validators(
//         &mut config,
//         &proto_files,
//         proto_include_paths,
//         validator_packages,
//     )
//     .expect("Failed to compile protos with protocheck_build");
// }
