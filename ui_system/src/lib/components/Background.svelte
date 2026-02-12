<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { cameraPortStore } from "$lib/store/cameraport.svelte";
	import { damagePanelColorStore } from "$lib/store/damagepanel_color.svelte";
	import { damagePanelTargetStore } from "$lib/store/damagepanel_target.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";
	import {
		CameraPortMessage,
		CameraSwitchMessage,
		DamagePanelColorMessage,
		DamagePanelTargetMessage,
		DisksMessage,
		FlapMessage,
		LiDARRange,
		RobotStateMessage
	} from "$lib/types/zenoh_message";
	import { listen } from "@tauri-apps/api/event";
</script>

<script lang="ts">
	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("cam/port", (event) => {
			const msg = CameraPortMessage.decode(event.payload);
			cameraPortStore.set(msg.port);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("cam/switch", (event) => {
			const msg = CameraSwitchMessage.decode(event.payload);
			cameraIdStore.set(msg.cameraId);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("damagepanel/color", (event) => {
			const msg = DamagePanelColorMessage.decode(event.payload);

			damagePanelColorStore.set(msg.color);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("damagepanel/target", (event) => {
			const msg = DamagePanelTargetMessage.decode(event.payload);

			damagePanelTargetStore.set(msg.target ?? null);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("disks", (event) => {
			const msg = DisksMessage.decode(event.payload);
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
			const msg = FlapMessage.decode(event.payload);
			flapMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("lidar/range", (event) => {
			const msg = LiDARRange.decode(event.payload);
			lidarMessageStore.set(msg);
			console.log("LiDAR range message received", event.payload);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<Uint8Array>("robotstate", (event) => {
			const msg = RobotStateMessage.decode(event.payload);
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
