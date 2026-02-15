<script module lang="ts">
	import { pitch_to_pixel } from "$lib/functions/flap_calc";
	import { yaw_to_pixel } from "$lib/functions/flap_calc";
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { cameraPortStore } from "$lib/store/cameraport.svelte";
	import { damagePanelColorStore } from "$lib/store/damagepanel_color.svelte";
	import { damagePanelTargetStore } from "$lib/store/damagepanel_target.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { crosshair_size, image_height, image_width } from "$lib/values/image";
	import { onMount } from "svelte";
</script>

<script lang="ts">
	export type ImageViewerProps = {
		host: string | null;
	};

	let { host }: ImageViewerProps = $props();

	let ws: WebSocket | null = $state(null);
	let canvasView: HTMLCanvasElement;

	let viewBox = `0 0 ${image_width} ${image_height}`;

	let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
	let animationFrameId: number;
	let pendingBitmap: ImageBitmap | null = null;
	let isDecoding = false;

	function render() {
		if (pendingBitmap && canvasView) {
			const ctx = canvasView.getContext("2d");
			if (ctx) {
				ctx.drawImage(pendingBitmap, 0, 0, canvasView.width, canvasView.height);
			}
			pendingBitmap.close();
			pendingBitmap = null;
		}
		animationFrameId = requestAnimationFrame(render);
	}

	function connect() {
		ws = new WebSocket(`ws://${host ? host : "localhost"}:${$cameraPortStore}`);
		ws.binaryType = "arraybuffer";

		ws.onmessage = async (event) => {
			// 前のフレームがまだ描画待ち、またはデコード中ならこのフレームは捨てる
			if (pendingBitmap || isDecoding) return;

			isDecoding = true;
			try {
				const blob = new Blob([event.data], { type: "image/jpeg" });
				pendingBitmap = await createImageBitmap(blob);
			} catch (e) {
				console.error("Decode error:", e);
			} finally {
				isDecoding = false;
			}
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
		animationFrameId = requestAnimationFrame(render);

		return () => {
			if (reconnectTimer) clearTimeout(reconnectTimer);
			cancelAnimationFrame(animationFrameId);
			ws?.close();
			if (pendingBitmap) pendingBitmap.close();
		};
	});
</script>

<div class="relative w-full aspect-video">
	<canvas
		bind:this={canvasView}
		width={image_width}
		height={image_height}
		class="absolute top-0 left-0 w-full h-full object-contain"
		role="img"
		aria-label="受信した画像がここに表示されます"
	></canvas>
	{#if $cameraIdStore == 0}
		<svg
			baseProfile="full"
			{viewBox}
			class="absolute top-0 left-0 pointer-events-none"
			xmlns="http://www.w3.org/2000/svg"
			xmlns:xlink="http://www.w3.org/1999/xlink"
		>
			<!-- Damage Panel -->
			{#if $damagePanelTargetStore}
				<rect
					height={$damagePanelTargetStore.height}
					width={$damagePanelTargetStore.width}
					x={$damagePanelTargetStore.x - $damagePanelTargetStore.width / 2}
					y={$damagePanelTargetStore.y - $damagePanelTargetStore.height / 2}
					fill-opacity="0.0"
					stroke={$damagePanelColorStore}
					stroke-width="4"
				/>
			{/if}
			<!-- Center Crosshair -->
			<line
				x1={image_width / 2 - crosshair_size / 2}
				y1={image_height / 2}
				x2={image_width / 2 + crosshair_size / 2}
				y2={image_height / 2}
				stroke="gray"
				stroke-width="4"
			/>
			<line
				x1={image_width / 2}
				y1={image_height / 2 - crosshair_size / 2}
				x2={image_width / 2}
				y2={image_height / 2 + crosshair_size / 2}
				stroke="gray"
				stroke-width="4"
			/>
			<!-- Target Center Crosshair -->
			{#if $flapMessageStore}
				<line
					x1={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2 - crosshair_size / 2}
					x2={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2 + crosshair_size / 2}
					y1={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2}
					y2={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2}
					stroke="red"
					stroke-width="8"
				/>
				<line
					x1={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2}
					x2={yaw_to_pixel($flapMessageStore.yaw) + image_width / 2}
					y1={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2 - crosshair_size / 2}
					y2={-pitch_to_pixel($flapMessageStore.pitch) + image_height / 2 + crosshair_size / 2}
					stroke="red"
					stroke-width="8"
				/>
			{/if}
		</svg>
	{/if}
</div>
