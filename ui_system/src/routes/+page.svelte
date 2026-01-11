<script lang="ts" module>
	import Background from "$lib/components/Background.svelte";
	import Disks from "$lib/components/Disks.svelte";
	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { max_disks } from "$lib/values/component_variable";
	import { invoke } from "@tauri-apps/api/core";
	import { getMatches } from "@tauri-apps/plugin-cli";
	import { onMount } from "svelte";
</script>

<script lang="ts">
	let host = "localhost";
	let port = "8080";

	onMount(async () => {
		const matches = await getMatches();
		const args = matches.args;

		if (
			args.address?.value &&
			typeof args.address?.value === "string" &&
			args.address.value.trim() !== ""
		) {
			host = args.address.value;
		}

		if (args.port?.value && typeof args.port?.value === "string" && args.port.value.trim() !== "") {
			port = args.port.value;
		}

		invoke("state_request");
	});
</script>

<main>
	<Background />
	<ImageViewer {host} {port} />

	<p>
		"Camera ID: {$cameraIdStore}"
	</p>
	<Disks num={leftDiskStore} width={50} height={400} stroke={5} max_number={max_disks} />

	<p>a</p>
	<Disks num={rightDiskStore} width={50} height={400} stroke={5} max_number={max_disks} />
</main>
