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
	right: number;
};

export type DisksMessage = {
	left: number;
	right: number;
};

export type FlapMessage = {
	pitch: number;
	yaw: number;
};

export type Target = {
	x: number;
	y: number;
	distance: number;
};

export type DamagePanelMessage = {
	target: Target | null;
};
