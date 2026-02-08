#![allow(clippy::all)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(unused_imports)]
#![allow(clippy::len_without_is_empty)]

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
