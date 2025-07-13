<script lang="ts">
	import { getMatches } from "@tauri-apps/plugin-cli";

	let host = "localhost";
	let port = "8080";

	onMount(async () => {
		const matches = await getMatches();
		const args = matches.args;

		if (args.host?.value && typeof args.host?.value === "string" && args.host.value.trim() !== "") {
			host = args.host.value;
		}

		if (args.port?.value && typeof args.port?.value === "string" && args.port.value.trim() !== "") {
			port = args.port.value;
		}
	});

	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import { onMount } from "svelte";
</script>

<main class="container">
	<ImageViewer {host} {port} />
</main>
