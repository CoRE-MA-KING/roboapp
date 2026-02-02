<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { damagePanelStore } from "$lib/store/damagepanel.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";
	import type {
		CameraSwitchMessage,
		DamagePanelMessage,
		DisksMessage,
		FlapMessage,
		LiDARMessage,
		RobotStateMessage
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
		let unlistenPromise = listen("damagepanel", (event) => {
			let msg = JSON.parse(event.payload as string) as DamagePanelMessage;
			damagePanelStore.set(msg.target);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("disks", (event) => {
			let msg = JSON.parse(event.payload as string) as DisksMessage;
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("flap", (event) => {
			flapMessageStore.set(JSON.parse(event.payload as string) as FlapMessage);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("lidar/range", (event) => {
			lidarMessageStore.set(JSON.parse(event.payload as string) as LiDARMessage);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("robotstate", (event) => {
			let msg = JSON.parse(event.payload as string) as RobotStateMessage;
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
