<script module lang="ts">
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { image_height, image_width } from "$lib/values/image";
	import { SvelteMap } from "svelte/reactivity";
</script>

<script lang="ts">
	let viewBox = `0 0 ${image_width} ${image_height}`;

	let dvs = new SvelteMap<number, number>();
	let near_distance = 150; // in mm

	lidarMessageStore.subscribe((value) => {
		dvs.clear();
		if (value === null) {
			return;
		}
		for (let i = 0; i < value.data.length; i++) {
			const message = value.data[i];
			const degree = (message.max_degree + message.min_degree) / 2 - 180;

			if (degree < 0) {
				continue;
			}

			dvs.set(
				degree / 180,
				(near_distance - Math.min(message.distance, near_distance)) / near_distance
			);
		}
	});
</script>

<div id="lidar-range" class="relative w-full aspect-video">
	<svg
		baseProfile="full"
		{viewBox}
		class="absolute top-0 left-0 pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		xmlns:xlink="http://www.w3.org/1999/xlink"
	>
		<defs>
			<linearGradient id="Gradient1">
				{#each dvs as [degree, value] (degree)}
					<stop offset="{degree * 100}%" style="stop-color: rgb(255,0,0); stop-opacity: {value};" />
				{/each}
			</linearGradient>
		</defs>
		<style>
			#rect1 {
				fill: url("#Gradient1");
			}
		</style>
		<polygon
			id="rect1"
			fill-opacity="0.5"
			points="
            0,{image_height}
            {image_width},{image_height}
            {image_width},{image_height / 2}
            {(image_width * 4) / 5},{(image_height * 3) / 4}
            {(image_width * 1) / 5},{(image_height * 3) / 4}
            0,{image_height / 2}
            0,{image_height}
            "
		/>
	</svg>
</div>
