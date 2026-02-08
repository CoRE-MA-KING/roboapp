<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { damagePanelStore } from "$lib/store/damagepanel.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";
	import { messageHelpers } from "$lib/types/zenoh_message";
	import { listen } from "@tauri-apps/api/event";
</script>

<script lang="ts">
	const toUint8Array = (payload: unknown): Uint8Array => {
		if (payload instanceof Uint8Array) {
			return payload;
		}
		if (payload instanceof ArrayBuffer) {
			return new Uint8Array(payload);
		}
		if (Array.isArray(payload)) {
			return Uint8Array.from(payload);
		}
		throw new Error("Unsupported payload type");
	};

	$effect(() => {
		let unlistenPromise = listen("cam/switch", (event) => {
			const msg = messageHelpers.CameraSwitchMessage.fromBinary(toUint8Array(event.payload));
			cameraIdStore.set(msg.cameraId);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("damagepanel", (event) => {
			const msg = messageHelpers.DamagePanelMessage.fromBinary(toUint8Array(event.payload));
			damagePanelStore.set(msg.target ?? null);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("disks", (event) => {
			const msg = messageHelpers.DisksMessage.fromBinary(toUint8Array(event.payload));
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("flap", (event) => {
			const msg = messageHelpers.FlapMessage.fromBinary(toUint8Array(event.payload));
			flapMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("lidar/range", (event) => {
			const msg = messageHelpers.LiDARRange.fromBinary(toUint8Array(event.payload));
			lidarMessageStore.set(msg);
			console.log("LiDAR range message received", event.payload);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("robotstate", (event) => {
			const msg = messageHelpers.RobotStateMessage.fromBinary(toUint8Array(event.payload));
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
