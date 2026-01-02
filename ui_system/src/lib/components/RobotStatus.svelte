<script lang="ts" module>
	import { listen } from "@tauri-apps/api/event";

	import { RobotStatus } from "$lib/variables/robot_status";

	export type TextBoxProps = {
		task_name: string;
	};
</script>

<script lang="ts">
	let { task_name }: TextBoxProps = $props();

	let value: string = $state("1");

	$effect(() => {
		let unlistenPromise = listen(task_name, (event) => {
			console.log(`Received event for task ${task_name}:`, event.payload);
			value = event.payload as string;
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>

<main>
	{#if !(value in RobotStatus)}
		<p>Unknown Status: {value}</p>
	{:else if RobotStatus[value] != "2"}
		<p>{RobotStatus[value]}</p>
	{/if}
</main>
