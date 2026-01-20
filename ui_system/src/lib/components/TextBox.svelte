<script lang="ts" module>
	import { listen } from "@tauri-apps/api/event";

	export type TextBoxProps = {
		pre: string;
		task_name: string;
		post: string;
	};
</script>

<script lang="ts">
	let { pre, task_name, post }: TextBoxProps = $props();

	let value: string = $state("");

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
	<p>{pre} {value} {post}</p>
</main>
