<script lang="ts" module>
	import { RobotStatus } from "$lib/types/robot_status";
	import type { Writable } from "svelte/store";

	export type RobotStatusProps = {
		status: Writable<string>;
	};
</script>

<script lang="ts">
	let { status }: RobotStatusProps = $props();
</script>

<main>
	{#if !($status in RobotStatus)}
		<p>Unknown Status: {$status}</p>
	{:else if RobotStatus[$status] != "2"}
		<p>{RobotStatus[$status]}</p>
	{/if}
</main>
