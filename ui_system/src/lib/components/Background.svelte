<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import type {
		CameraSwitchMessage,
		DisksMessage,
		FlapMessage,
		LiDARMessage
	} from "$lib/types/zenoh_message";
	import { listen } from "@tauri-apps/api/event";
</script>

<script lang="ts">
	$effect(() => {
		let unlistenPromise = listen("cam/switch", (event) => {
			cameraIdStore.set((JSON.parse(event.payload as string) as CameraSwitchMessage).camera_id);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("disks", (event) => {
			let msg = JSON.parse(event.payload as string) as DisksMessage;
			console.log("Disks message received:", msg, msg.left, msg.right);
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("lidar/force_vector", (event) => {
			lidarMessageStore.set(event.payload as LiDARMessage);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("flap", (event) => {
			flapMessageStore.set(event.payload as FlapMessage);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>
