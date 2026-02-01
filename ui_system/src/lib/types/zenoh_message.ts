export type cameraID = number;

export type RobotStateMessage = {
	state: number;
	color: string;
};

export type CameraSwitchMessage = {
	camera_id: cameraID;
};

export type LiDARRange = {
	left: number;
	rear_left: number;
	rear_right: number;
	rear: number;
};


export type DisksMessage = {
	left: number;
	right: number;
};

export type FlapMessage = {
	pitch: number;
	yaw: number;
};

export type DamagePanelMessage = {
	target_x: number;
	target_y: number;
	target_distance: number;
};
