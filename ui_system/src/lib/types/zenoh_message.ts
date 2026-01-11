export type cameraID = number;

export type CameraSwitchMessage = {
	camera_id: cameraID;
};

export type LiDARMessage = {
	linear: number;
	angular: number;
};

export type DisksMessage = {
	left: number;
	right: number;
};

export type FlapMessage = {
	pitch: number;
	yaw: number;
};
