<script module lang="ts">
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
</script>

<script lang="ts">
	let image_width = $state(0);
	let image_height = $state(0);

	const side_top = 0.1;
	const side_height = 0.3;
	const side_width = 0.1;

	const button_height = 0.15;

	const opacity_multiplier = 0.8;

	let near_distance = 500; // in mm
	let far_distance = 3_000; // in mm

	function farlogic(distance: number) {
		if (distance < near_distance) {
			return 1.0;
		} else if (distance > far_distance) {
			return 0.0;
		} else {
			return (far_distance - distance) / (far_distance - near_distance);
		}
	}
</script>

<div
	id="lidar-range"
	class="relative w-full h-full"
	bind:clientWidth={image_width}
	bind:clientHeight={image_height}
>
	<svg
		baseProfile="full"
		viewBox={`0 0 ${image_width} ${image_height}`}
		class="absolute top-0 left-0 pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		xmlns:xlink="http://www.w3.org/1999/xlink"
	>
		{#if $lidarMessageStore}
			<!-- Left -->
			<polygon
				fill="red"
				fill-opacity={opacity_multiplier * farlogic($lidarMessageStore.left)}
				points="
            0,{image_height * side_top}
            0,{image_height}
            {image_width * side_width},{image_height * (1 - button_height)}
            {image_width * side_width},{image_height * side_height}
            0,{image_height * side_top}
            "
			/>

			<!-- Rear Left -->
			<polygon
				fill="red"
				fill-opacity={opacity_multiplier * farlogic($lidarMessageStore.rearLeft)}
				points="
            0,{image_height}
            {image_width * 0.5},{image_height}
            {image_width * 0.5},{image_height * (1 - button_height)}
            {image_width * side_width},{image_height * (1 - button_height)}
            0,{image_height}
            "
			/>

			<!-- Rear Right -->
			<polygon
				fill="red"
				fill-opacity={opacity_multiplier * farlogic($lidarMessageStore.rearRight)}
				points="
            {image_width},{image_height}
            {image_width * 0.5},{image_height}
            {image_width * 0.5},{image_height * (1 - button_height)}
            {image_width * (1 - side_width)},{image_height * (1 - button_height)}
            {image_width},{image_height}
            "
			/>

			<!-- Right -->
			<polygon
				fill="red"
				fill-opacity={opacity_multiplier * farlogic($lidarMessageStore.right)}
				points="
            {image_width},{image_height * side_top}
            {image_width},{image_height}
            {image_width * (1 - side_width)},{image_height * (1 - button_height)}
            {image_width * (1 - side_width)},{image_height * side_height}
            {image_width},{image_height * side_top}
            "
			/>
		{/if}
	</svg>
</div>
