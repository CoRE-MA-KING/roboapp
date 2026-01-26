import {
	min_flap_pitch_degree,
	max_flap_pitch_degree,
	min_flap_pitch_pixel,
	min_flap_yaw_degree,
	min_flap_yaw_pixel,
	max_flap_pitch_pixel,
	max_flap_yaw_degree,
	max_flap_yaw_pixel
} from "$lib/values/flap";

export function yaw_to_pixel(yaw_degree: number): number {
	if (yaw_degree < min_flap_yaw_degree) yaw_degree = min_flap_yaw_degree;
	if (yaw_degree > max_flap_yaw_degree) yaw_degree = max_flap_yaw_degree;

	const flapPosition =
		(yaw_degree - min_flap_yaw_degree) / (max_flap_yaw_degree - min_flap_yaw_degree);
	const pixel = min_flap_yaw_pixel + flapPosition * (max_flap_yaw_pixel - min_flap_yaw_pixel);
	return pixel;
}

export function pitch_to_pixel(pitch_degree: number): number {
	if (pitch_degree < min_flap_pitch_degree) pitch_degree = min_flap_pitch_degree;
	if (pitch_degree > max_flap_pitch_degree) pitch_degree = max_flap_pitch_degree;

	const flapPosition =
		(pitch_degree - min_flap_pitch_degree) / (max_flap_pitch_degree - min_flap_pitch_degree);
	const pixel = min_flap_pitch_pixel + flapPosition * (max_flap_pitch_pixel - min_flap_pitch_pixel);
	return pixel;
}
