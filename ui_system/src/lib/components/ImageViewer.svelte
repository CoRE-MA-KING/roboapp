<script lang="ts" module>
	export type ImageViewerProps = {
		host: string | null;
		port: string | null;
	};
</script>

<script lang="ts">
	import { onMount } from "svelte";

	let { host, port }: ImageViewerProps = $props();

	let ws: WebSocket | null = $state(null);
	let imageUrl: string | null = $state(null);
	let imageView: HTMLImageElement;

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

<div>
	<img
		bind:this={imageView}
		src={imageUrl}
		width="1280"
		height="720"
		alt="受信した画像がここに表示されます"
	/>
</div>
