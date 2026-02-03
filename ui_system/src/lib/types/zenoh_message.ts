import { z } from "zod";

export type cameraID = number;

export const CameraSwitchSchema = z.object({
	camera_id: z.number()
});

export const RobotStateSchema = z.object({
	state: z.number(),
	color: z.string()
});

export const LiDARRangeSchema = z.object({
	left: z.number(),
	rear_left: z.number(),
	rear_right: z.number(),
	right: z.number()
});

export const DisksSchema = z.object({
	left: z.number(),
	right: z.number()
});

export const FlapSchema = z.object({
	pitch: z.number(),
	yaw: z.number()
});

export const TargetSchema = z.object({
	x: z.number(),
	y: z.number(),
	distance: z.number()
});

export const DamagePanelSchema = z.object({
	target: TargetSchema.nullable()
});

export type CameraSwitchMessage = z.infer<typeof CameraSwitchSchema>;
export type RobotStateMessage = z.infer<typeof RobotStateSchema>;
export type LiDARRange = z.infer<typeof LiDARRangeSchema>;
export type DisksMessage = z.infer<typeof DisksSchema>;
export type FlapMessage = z.infer<typeof FlapSchema>;
export type Target = z.infer<typeof TargetSchema>;
export type DamagePanelMessage = z.infer<typeof DamagePanelSchema>;
