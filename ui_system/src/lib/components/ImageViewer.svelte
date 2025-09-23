<script lang="ts" module>
	export type ImageViewerProps = {
		host: string | null;
		port: string | null;
		cropX?: number;
		cropY?: number;
		cropW?: number;
		cropH?: number;
	};
</script>

<script lang="ts">
	import { onMount } from "svelte";

	let {
		host,
		port,
		cropX = 100,
		cropY = 100,
		cropW = 128,
		cropH = 72
	}: ImageViewerProps = $props();

	let ws: WebSocket | null = $state(null);
	let canvasEl: HTMLCanvasElement;
	const width = 1280;
	const height = 720;

	function drawImageFromBlob(blob: Blob) {
		const img = new window.Image();
		img.onload = () => {
			const ctx = canvasEl.getContext("2d");
			if (ctx) {
				console.time("func"); // 計測終了
				ctx.clearRect(0, 0, width, height);
				// cropX, cropY, cropW, cropH の範囲をトリミングしてcanvas全体に描画
				ctx.drawImage(
					img,
					cropX,
					cropY,
					cropW,
					cropH, // 元画像から切り出す範囲
					0,
					0,
					width,
					height // canvas上の描画範囲
				);
			}
			console.timeEnd("func"); // 計測終了
			URL.revokeObjectURL(img.src);
		};

		img.src = URL.createObjectURL(blob);
	}

	let reconnectTimer: number | null = null;

	function connect() {
		ws = new WebSocket(`ws://${host ? host : "localhost"}:${port ? port : "8080"}`);
		ws.binaryType = "arraybuffer";

		ws.onmessage = (event) => {
			const blob = new Blob([event.data], { type: "image/jpeg" });
			drawImageFromBlob(blob);
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
		};
	});
</script>

<div>
	<canvas bind:this={canvasEl} {width} {height} style="background: #222;">
		受信した画像がここに表示されます
	</canvas>
</div>
