<script lang="ts" module>
	import type { Writable } from "svelte/store";

	export type RobotStatusProps = {
		num: Writable<number>;
		width: number;
		height: number;
		stroke: number;
		max_number: number;
	};
</script>

<script lang="ts">
	let { num, width, height, stroke = 5, max_number }: RobotStatusProps = $props();

	let step = (height - stroke / 2) / max_number;
</script>

<main>
	<svg {width} {height} version="1.1" xmlns="http://www.w3.org/2000/svg">
		<rect
			x={stroke / 2}
			y={height - step * $num}
			width={width - stroke}
			height={height - stroke}
			fill={$num >= max_number / 2 ? "green" : "orange"}
		/>
		<rect x="0" y="0" {width} {height} stroke="black" fill="transparent" stroke-width={stroke} />
	</svg>
</main>
