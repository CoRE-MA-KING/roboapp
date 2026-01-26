<script lang="ts" module>
	import Background from "$lib/components/Background.svelte";
	import Disks from "$lib/components/Disks.svelte";
	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
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
	<div class="absolute top-[30vh] w-[5vw] h-[20vh] left-[5vw]">
		<Disks id="left-disk" classes="" num={leftDiskStore} width={50} height={400} stroke={5} />
	</div>
	<div class="absolute top-[30vh] w-[5vw] h-[20vh] right-[5vw]">
		<Disks id="right-disk" classes="" num={rightDiskStore} width={50} height={400} stroke={5} />
	</div>
</main>
