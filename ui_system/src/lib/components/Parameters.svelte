<script module lang="ts">
	import { writable, type Writable } from "svelte/store";

	export const host: Writable<string> = writable("localhost");
	export const port: Writable<string> = writable("8080");
</script>

<script lang="ts">
	import { listen } from "@tauri-apps/api/event";

	$effect(() => {
		let unlistenPromise = listen("host", (event) => {
			console.log(`Received event for task host`, event.payload);
			$host = event.payload as string;
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("port", (event) => {
			console.log(`Received event for task port`, event.payload);
			$port = event.payload as string;
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>
