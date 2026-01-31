<script lang="ts" module>
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";

	export type RobotStatusProps = {
		classes?: string;
		stroke_color?: string;
		stroke_width?: number;
	};
</script>

<script lang="ts">
	let {
		classes = "text-9xl font-bold",
		stroke_color = "black",
		stroke_width = 6
	}: RobotStatusProps = $props();
</script>

<main>
	{#if $robotStatusStore}
		<p
			class:text-red-600={$robotStatusStore.color === "red"}
			class:text-blue-600={$robotStatusStore.color === "blue"}
			class="backdrop-blur bg-white/60 {classes}"
			style="-webkit-text-stroke: {stroke_width}px {stroke_color}; text-stroke: {stroke_width}px {stroke_color};"
		>
			{RobotStatus[$robotStatusStore.state]}
		</p>
	{/if}
</main>
