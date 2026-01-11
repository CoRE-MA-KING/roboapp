<script lang="ts">
	import { image_height, image_width, target_height, target_width } from "$lib/values/image";
	import { onMount } from "svelte";

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
		<rect
			height={target_height}
			width={target_width}
			x={(image_width - target_width) / 2}
			y={(image_height - target_height) / 2}
			fill-opacity="0.0"
			stroke="red"
			stroke-width="10"
		/>
	</svg>
</div>
