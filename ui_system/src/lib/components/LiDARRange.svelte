<script module lang="ts">
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { image_height, image_width } from "$lib/values/image";
</script>

<script lang="ts">
	let viewBox = `0 0 ${image_width} ${image_height}`;

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

<div id="lidar-range" class="relative w-full aspect-video">
	<svg
		baseProfile="full"
		{viewBox}
		class="absolute top-0 left-0 pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		xmlns:xlink="http://www.w3.org/1999/xlink"
	>
		{#if $lidarMessageStore}
			<!-- Left -->
			<polygon
				fill="red"
				fill-opacity={0.9 * farlogic($lidarMessageStore.left)}
				points="
            0,{image_height * 0.1}
            0,{image_height}
            {image_width * 0.15},{image_height * 0.8}
            {image_width * 0.15},{image_height * 0.3}
            0,{image_height * 0.1}
            "
			/>

			<!-- Rear Left -->
			<polygon
				fill="red"
				fill-opacity={0.9 * farlogic($lidarMessageStore.rear_left)}
				points="
            0,{image_height}
            {image_width * 0.5},{image_height}
            {image_width * 0.5},{image_height * 0.8}
            {image_width * 0.15},{image_height * 0.8}
            0,{image_height}
            "
			/>

			<!-- Rear Right -->
			<polygon
				fill="red"
				fill-opacity={0.9 * farlogic($lidarMessageStore.rear_right)}
				points="
            {image_width},{image_height}
            {image_width * 0.5},{image_height}
            {image_width * 0.5},{image_height * 0.8}
            {image_width * 0.85},{image_height * 0.8}
            {image_width},{image_height}
            "
			/>

			<!-- Right -->
			<polygon
				fill="red"
				fill-opacity={0.9 * farlogic($lidarMessageStore.right)}
				points="
            {image_width},{image_height * 0.1}
            {image_width},{image_height}
            {image_width * 0.85},{image_height * 0.8}
            {image_width * 0.85},{image_height * 0.3}
            {image_width},{image_height * 0.1}
            "
			/>
		{/if}
	</svg>
</div>
