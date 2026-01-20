<script module lang="ts">
	import { pitch_to_pixel } from "$lib/functions/flap_calc";
	import { yaw_to_pixel } from "$lib/functions/flap_calc";
	import { damagePanelStore } from "$lib/store/damagepanel.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import {
		crosshair_size,
		image_height,
		image_width,
		target_height,
		target_width
	} from "$lib/values/image";
	import { onMount } from "svelte";
</script>

<script lang="ts">
	export type ImageViewerProps = {
		host: string | null;
		port: string | null;
	};

	let { host, port }: ImageViewerProps = $props();

	let ws: WebSocket | null = $state(null);
	let imageUrl: string | null = $state(null);
	let imageView: HTMLImageElement;

	let viewBox = `0 0 ${image_width} ${image_height}`;

	let reconnectTimer: number | null = null;

	function connect() {
		ws = new WebSocket(`ws://${host ? host : "localhost"}:${port ? port : "8080"}`);
		ws.binaryType = "arraybuffer";

		ws.onmessage = (event) => {
			const blob = new Blob([event.data], { type: "image/jpeg" });
			if (imageUrl) URL.revokeObjectURL(imageUrl);
			imageUrl = URL.createObjectURL(blob);
		};

		ws.onclose = () => {
			if (reconnectTimer) clearTimeout(reconnectTimer);
			reconnectTimer = setTimeout(connect, 3000);
		};

		ws.onerror = (error) => {
			console.error("WebSocket error:", error);
			ws?.close();
		};
	}

	onMount(() => {
		connect();

		return () => {
			if (reconnectTimer) clearTimeout(reconnectTimer);
			ws?.close();
			if (imageUrl) URL.revokeObjectURL(imageUrl);
		};
	});
</script>

<div class="relative w-full aspect-video">
	<img
		bind:this={imageView}
		src={imageUrl}
		class="absolute top-0 left-0 w-full h-full object-contain"
		alt="受信した画像がここに表示されます"
	/>
	<svg
		baseProfile="full"
		{viewBox}
		class="absolute top-0 left-0 pointer-events-none"
		xmlns="http://www.w3.org/2000/svg"
		xmlns:xlink="http://www.w3.org/1999/xlink"
	>
		<!-- Damage Panel -->
		{#if $damagePanelStore}
			<rect
				height={target_height}
				width={target_width}
				x={$damagePanelStore.target_x - target_width / 2}
				y={$damagePanelStore.target_y - target_height / 2}
				fill-opacity="0.0"
				stroke="red"
				stroke-width="10"
			/>
		{/if}
		<!-- Center Crosshair -->
		<line
			x1={image_width / 2 - crosshair_size / 2}
			y1={image_height / 2}
			x2={image_width / 2 + crosshair_size / 2}
			y2={image_height / 2}
			stroke="gray"
		/>
		<line
			x1={image_width / 2}
			y1={image_height / 2 - crosshair_size / 2}
			x2={image_width / 2}
			y2={image_height / 2 + crosshair_size / 2}
			stroke="gray"
		/>
		<!-- Target Center Crosshair -->
		{#if $flapMessageStore}
			<line
				x1={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2 - crosshair_size / 2}
				x2={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2 + crosshair_size / 2}
				y1={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2}
				y2={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2}
				stroke="red"
			/>
			<line
				x1={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2}
				x2={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2}
				y1={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2 - crosshair_size / 2}
				y2={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2 + crosshair_size / 2}
				stroke="red"
			/>
		{/if}
	</svg>
</div>
