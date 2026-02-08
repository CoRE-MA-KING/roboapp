<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { damagePanelStore } from "$lib/store/damagepanel.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";
	import {
		CameraSwitchMessage,
		DamagePanelMessage,
		DisksMessage,
		FlapMessage,
		LiDARRange,
		RobotStateMessage
	} from "$lib/types/zenoh_message";
	import { listen } from "@tauri-apps/api/event";
</script>

<script lang="ts">
	$effect(() => {
		let unlistenPromise = listen("cam/switch", (event) => {
			const msg = CameraSwitchMessage.fromJSON(JSON.parse(event.payload as string));
			cameraIdStore.set(msg.cameraId);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("damagepanel", (event) => {
			const msg = DamagePanelMessage.fromJSON(JSON.parse(event.payload as string));
			damagePanelStore.set(msg.target ?? null);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("disks", (event) => {
			const msg = DisksMessage.fromJSON(JSON.parse(event.payload as string));
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("flap", (event) => {
			const msg = FlapMessage.fromJSON(JSON.parse(event.payload as string));
			flapMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("lidar/range", (event) => {
			const msg = LiDARRange.fromJSON(JSON.parse(event.payload as string));
			lidarMessageStore.set(msg);
			console.log("LiDAR range message received", event.payload as string);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("robotstate", (event) => {
			const msg = RobotStateMessage.fromJSON(JSON.parse(event.payload as string));
			if (msg.state in RobotStatus) {
				robotStatusStore.set(msg);
			} else {
				robotStatusStore.set(null);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>
