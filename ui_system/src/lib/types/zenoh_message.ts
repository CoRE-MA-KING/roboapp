import { z } from "zod";

export type cameraID = number;

export const CameraSwitchSchema = z.object({
	camera_id: z.number().int()
});

export const RobotStateSchema = z.object({
	state: z.number().int(),
	color: z.enum(["blue", "red"])
});

export const LiDARRangeSchema = z.object({
	left: z.number().min(0).max(10000),
	rear_left: z.number().min(0).max(10000),
	rear_right: z.number().min(0).max(10000),
	right: z.number().min(0).max(10000)
});

export const DisksSchema = z.object({
	left: z.number().int().min(0),
	right: z.number().int().min(0)
});

export const FlapSchema = z.object({
	pitch: z.number(),
	yaw: z.number()
});

export const TargetSchema = z.object({
	x: z.number().int().min(0).max(3840),
	y: z.number().int().min(0).max(2160),
	distance: z.number().int()
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
