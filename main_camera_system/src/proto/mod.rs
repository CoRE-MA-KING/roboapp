pub mod roboapp {
    include!(concat!(env!("OUT_DIR"), "/roboapp.rs"));
}

pub mod buf {
    pub mod validate {
        include!(concat!(env!("OUT_DIR"), "/buf.validate.rs"));
    }
}

pub mod google {
    pub mod protobuf {
        include!(concat!(env!("OUT_DIR"), "/google.protobuf.rs"));
    }
}
