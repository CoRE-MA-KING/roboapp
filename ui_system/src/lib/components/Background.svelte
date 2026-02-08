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
		let unlistenPromise = listen<Uint8Array>("cam/switch", (event) => {
			const msg = CameraSwitchMessage.decode(new Uint8Array(event.payload));
			console.log(msg);
			cameraIdStore.set(msg.cameraId);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("damagepanel", (event) => {
			const msg = DamagePanelMessage.decode(new Uint8Array(event.payload));

			damagePanelStore.set(msg.target ?? null);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("disks", (event) => {
			const msg = DisksMessage.decode(new Uint8Array(event.payload));
			console.log(msg);
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("flap", (event) => {
			const msg = FlapMessage.decode(new Uint8Array(event.payload));
			flapMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("lidar/range", (event) => {
			const msg = LiDARRange.decode(new Uint8Array(event.payload));
			lidarMessageStore.set(msg);
			console.log("LiDAR range message received", event.payload);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("robotstate", (event) => {
			const msg = RobotStateMessage.decode(new Uint8Array(event.payload));
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
