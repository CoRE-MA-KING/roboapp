export type cameraID = number;

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

export type DamagePanelMessage = {
	target_x: number;
	target_y: number;
	target_distance: number;
};
