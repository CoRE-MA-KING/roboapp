export type cameraID = number;

export type RobotStateMessage = {
	state: number;
	color: string;
};

export type CameraSwitchMessage = {
	camera_id: cameraID;
};

export type LiDARRange = {
	min_degree: number;
	max_degree: number;
	distance: number;
};

export type LiDARMessage = {
	data: LiDARRange[];
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
