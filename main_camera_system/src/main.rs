use clap::Parser;

use v4l::Device;
use v4l::FourCC;
use v4l::buffer::Type;
use v4l::io::mmap::Stream;
use v4l::io::traits::CaptureStream;
use v4l::video::Capture;
use zenoh;

#[derive(Parser, Debug)]
struct Args {
    #[arg(short, long, default_value = "0")]
    camera_id: usize,
    #[arg(short, long, default_value = "")]
    prefix: String,

    #[arg(short, long, action)]
    raw: bool,

    #[arg(short, long, action)]
    jpg: bool,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    // Create a new capture device with a few extra parameters
    let mut dev = Device::new(args.camera_id).expect("Failed to open device");

    // Let's say we want to explicitly request another format
    let mut fmt = dev.format().expect("Failed to read format");
    fmt.width = 1280;
    fmt.height = 720;
    fmt.fourcc = FourCC::new(b"MJPG");
    // fmt.fourcc = FourCC::new(b"YUYV");
    let fmt = dev.set_format(&fmt).expect("Failed to write format");

    println!("Format in use:\n{}", fmt);

    let mut stream = Stream::with_buffers(&mut dev, Type::VideoCapture, 4)
        .expect("Failed to create buffer stream");

    // Initialize Zenoh client

    let zenoh = zenoh::open(zenoh::config::Config::default()).await.unwrap();

    let prefix: String = if !args.prefix.is_empty() {
        format!("{}/{}", args.prefix.clone(), "cam")
    } else {
        "cam".to_string()
    };

    let jpg_publisher: Option<zenoh::pubsub::Publisher> = if args.jpg {
        Some(
            zenoh
                .declare_publisher(format!("{}/jpg", prefix))
                .await
                .unwrap(),
        )
    } else {
        None
    };

    let raw_publisher: Option<zenoh::pubsub::Publisher> = if args.raw {
        Some(
            zenoh
                .declare_publisher(format!("{}/raw", prefix))
                .await
                .unwrap(),
        )
    } else {
        None
    };

    loop {
        let (buf, meta) = stream.next().unwrap();
        println!(
            "Buffer size: {}, seq: {}, timestamp: {}",
            buf.len(),
            meta.sequence,
            meta.timestamp
        );

        if let Some(jpg_publisher) = &jpg_publisher {
            jpg_publisher
                .put(buf)
                .await
                .expect("Failed to publish JPEG buffer");
        }

        // Publish the buffer data to Zenoh
        if let Some(raw_publisher) = &raw_publisher {
            let result = match turbojpeg::decompress(buf, turbojpeg::PixelFormat::RGB).ok() {
                Some(image) => image.pixels,
                None => continue,
            };
            raw_publisher
                .put(result)
                .await
                .expect("Failed to publish raw buffer");
        }
    }
}
