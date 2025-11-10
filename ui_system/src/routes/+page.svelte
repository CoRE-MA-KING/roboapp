<script lang="ts">
	import ImageViewer from "$lib/components/ImageViewer.svelte";
	import TextBox from "$lib/components/TextBox.svelte";
</script>

<main class="container">
	<h2>Image</h2>
	<ImageViewer />

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
