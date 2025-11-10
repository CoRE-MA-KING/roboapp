<script lang="ts">
	import { onMount } from "svelte";
	import { invoke } from "@tauri-apps/api/core";

	let ws: WebSocket | null = $state(null);
	let imageUrl: string | null = $state(null);
	let imageView: HTMLImageElement;
	let reconnectTimer: number | null = null;

	function connect(host: string = "localhost", port: string = "8080") {
		ws = new WebSocket(`ws://${host}:${port}`);
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
		invoke("get_config_host").then((h) => {
			invoke("get_config_port").then((p) => {
				connect(h as string, p as string);
			});
		});

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
