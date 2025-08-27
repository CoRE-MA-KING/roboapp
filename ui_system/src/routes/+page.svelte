<script lang="ts">
	import { getMatches } from "@tauri-apps/plugin-cli";

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

	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import { onMount } from "svelte";
	import TextBox from "$lib/components/TextBox.svelte";
	import { invoke } from "@tauri-apps/api/core";
</script>

<main class="container">
	<h2>Image</h2>
	<ImageViewer {host} {port} />

	<h2>Robot State</h2>
	<TextBox pre="video_id : " task_name="video_id" post="" />
	<TextBox pre="pitch_deg : " task_name="pitch_deg" post="" />
	<TextBox pre="muzzle_velocity : " task_name="muzzle_velocity" post="" />
	<TextBox pre="reloaded_left_disks : " task_name="reloaded_left_disks" post="" />
	<TextBox pre="reloaded_right_disks : " task_name="reloaded_right_disks" post="" />
	<TextBox pre="state_id : " task_name="state_id" post="" />
	<TextBox pre="target_panel : " task_name="target_panel" post="" />
	<TextBox pre="auto_aim : " task_name="auto_aim" post="" />
	<TextBox pre="record_video : " task_name="record_video" post="" />
	<TextBox pre="ready_to_fire : " task_name="ready_to_fire" post="" />

	<h2>Robot Command</h2>
	<TextBox pre="target_x : " task_name="target_x" post="" />
	<TextBox pre="target_y : " task_name="target_y" post="" />
	<TextBox pre="target_distance : " task_name="target_distance" post="" />
</main>
