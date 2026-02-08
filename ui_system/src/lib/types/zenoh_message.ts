import { CameraSwitchMessageSchema } from "./proto/roboapp/camera_switch_pb.js";
import { DamagePanelMessageSchema, TargetSchema } from "./proto/roboapp/damage_panel_pb.js";
import { DisksMessageSchema } from "./proto/roboapp/disks_pb.js";
import { FlapMessageSchema } from "./proto/roboapp/flap_pb.js";
import { LiDARRangeSchema } from "./proto/roboapp/lidar_range_pb.js";
import { RobotStateMessageSchema } from "./proto/roboapp/robot_state_pb.js";
import { fromBinary as protobufFromBinary } from "@bufbuild/protobuf";

// Type re-exports
export type { CameraSwitchMessage } from "./proto/roboapp/camera_switch_pb";
export type { DamagePanelMessage, Target } from "./proto/roboapp/damage_panel_pb";
export type { DisksMessage } from "./proto/roboapp/disks_pb";
export type { FlapMessage } from "./proto/roboapp/flap_pb";
export type { LiDARRange } from "./proto/roboapp/lidar_range_pb";
export type { RobotStateMessage } from "./proto/roboapp/robot_state_pb";
export type cameraID = number;

// Message deserialization helpers
export const messageHelpers = {
	CameraSwitchMessage: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(CameraSwitchMessageSchema, data)
	},
	DamagePanelMessage: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(DamagePanelMessageSchema, data)
	},
	Target: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(TargetSchema, data)
	},
	DisksMessage: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(DisksMessageSchema, data)
	},
	FlapMessage: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(FlapMessageSchema, data)
	},
	LiDARRange: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(LiDARRangeSchema, data)
	},
	RobotStateMessage: {
		fromBinary: (data: Uint8Array) => protobufFromBinary(RobotStateMessageSchema, data)
	}
};
