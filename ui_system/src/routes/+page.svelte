<script lang="ts" module>
	import Background from "$lib/components/Background.svelte";
	import Disks from "$lib/components/Disks.svelte";
	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import LiDARRange from "$lib/components/LiDARRange.svelte";
	import RobotStatus from "$lib/components/RobotStatus.svelte";
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { invoke } from "@tauri-apps/api/core";
	import { getMatches } from "@tauri-apps/plugin-cli";
	import { onMount } from "svelte";
</script>

<script lang="ts">
	let host = "localhost";

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

		invoke("state_request");
	});
</script>

<main>
	<Background />

	<div class="absolute w-full h-full">
		<ImageViewer {host} />
	</div>

	{#if $cameraIdStore == 0}
		<div class="absolute w-full h-full bottom-0">
			<LiDARRange />
		</div>
	{/if}

	<div class="absolute top-[30vh] w-[5vw] h-[20vh] left-[5vw]">
		<Disks id="left-disk" classes="" num={leftDiskStore} width={50} height={400} stroke={5} />
	</div>
	<div class="absolute top-[30vh] w-[5vw] h-[20vh] right-[5vw]">
		<div class="flex justify-end">
			<Disks id="right-disk" classes="" num={rightDiskStore} width={50} height={400} stroke={5} />
		</div>
	</div>
	<div class="absolute top-[15vh] left-1/2 -translate-x-1/2 flex items-center justify-center z-10">
		<RobotStatus />
	</div>
</main>
