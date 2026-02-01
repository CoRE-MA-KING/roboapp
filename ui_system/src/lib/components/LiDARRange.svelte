<script module lang="ts">
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { image_height, image_width } from "$lib/values/image";
	import { SvelteMap } from "svelte/reactivity";
</script>

<script lang="ts">
	let viewBox = `0 0 ${image_width} ${image_height}`;

	let near_distance = 1_000; // in mm
</script>

<div id="lidar-range" class="relative w-full aspect-video">
	<svg
		baseProfile="full"
		{viewBox}
		class="absolute top-0 left-0 pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		xmlns:xlink="http://www.w3.org/1999/xlink"
	>
		<!-- Left -->
		{#if $lidarMessageStore}
			<polygon
				color="red"
				fill-opacity={(0.8 * (near_distance - Math.min($lidarMessageStore.left, near_distance))) /
					near_distance}
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
		{/if}
	</svg>
</div>
