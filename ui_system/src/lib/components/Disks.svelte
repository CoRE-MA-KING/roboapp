<script lang="ts" module>
	import { max_disks } from "$lib/values/component_variable";
	import type { Writable } from "svelte/store";

	export type RobotStatusProps = {
		id: string;
		classes: string;
		num: Writable<number>;
		width: number;
		height: number;
		stroke: number;
	};
</script>

<script lang="ts">
	let { id, classes, num, width, height, stroke = 5 }: RobotStatusProps = $props();

	let step = $derived((height - stroke / 2) / max_disks);
</script>

<main {id} class={classes}>
	<svg {width} {height} version="1.1" xmlns="http://www.w3.org/2000/svg">
		{#if $num === 0}
			<line x1={0} y1={0} x2={width} y2={height} stroke="red" stroke-width={stroke} />
			<line x1={0} y1={height} x2={width} y2={0} stroke="red" stroke-width={stroke} />
		{/if}
		<rect
			x={stroke / 2}
			y={height - step * Math.min($num, max_disks)}
			width={width - stroke}
			height={height - stroke}
			fill={$num >= max_disks / 2 ? "green" : "orange"}
		/>
		<rect x="0" y="0" {width} {height} stroke="black" fill="transparent" stroke-width={stroke} />
	</svg>
</main>
