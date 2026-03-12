<script lang="ts" module>
	import { max_disks } from "$lib/values/component_variable";
	import type { Writable } from "svelte/store";

	export type RobotStatusProps = {
		id: string;
		num: Writable<number>;
		stroke?: number;
	};
</script>

<script lang="ts">
	let { id, num, stroke = 2 }: RobotStatusProps = $props();

	// 親要素の実際のサイズを保持するリアクティブな変数
	let width = $state(0);
	let height = $state(0);

	// 親要素の高さに基づいた1ディスクあたりの高さを計算
	let inner_height = $derived(height - stroke);
	let step = $derived(inner_height / max_disks);

	// 現在の塗りつぶしの高さ（下から上へ）
	let current_fill_height = $derived(step * Math.min($num, max_disks));
</script>

<!-- bind:clientWidth/Height を使って親要素のサイズを取得 -->
<main {id} class="w-full h-full" bind:clientWidth={width} bind:clientHeight={height}>
	<svg
		viewBox="0 0 {width} {height}"
		width="100%"
		height="100%"
		version="1.1"
		xmlns="http://www.w3.org/2000/svg"
	>
		{#if $num === 0}
			<line x1={0} y1={0} x2={width} y2={height} stroke="red" stroke-width={stroke} />
			<line x1={0} y1={height} x2={width} y2={0} stroke="red" stroke-width={stroke} />
		{/if}
		<rect
			x={stroke / 2}
			y={height - stroke / 2 - current_fill_height}
			width={width - stroke}
			height={current_fill_height}
			fill={$num >= max_disks / 2 ? "green" : "orange"}
		/>
		<rect x="0" y="0" {width} {height} stroke="black" fill="transparent" stroke-width={stroke} />
	</svg>
</main>
