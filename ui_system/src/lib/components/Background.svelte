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
	function toUint8Array(payload: unknown): Uint8Array {
		if (payload instanceof Uint8Array) return payload;
		if (Array.isArray(payload)) return new Uint8Array(payload);
		if (payload && typeof payload === "object" && "data" in payload) {
			const data = (payload as { data: unknown }).data;
			if (Array.isArray(data) || data instanceof Uint8Array) {
				return new Uint8Array(data);
			}
		}
		return new Uint8Array(payload as ArrayLike<number> | ArrayBuffer);
	}

	$effect(() => {
		let unlistenPromise = listen<unknown>("cam/port", (event) => {
			const msg = CameraPortMessage.decode(toUint8Array(event.payload));
			cameraPortStore.set(msg.port);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("cam/switch", (event) => {
			const msg = CameraSwitchMessage.decode(toUint8Array(event.payload));
			cameraIdStore.set(msg.cameraId);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("damagepanel/color", (event) => {
			const msg = DamagePanelColorMessage.decode(toUint8Array(event.payload));

			damagePanelColorStore.set(msg.color);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("damagepanel/target", (event) => {
			const msg = DamagePanelTargetMessage.decode(toUint8Array(event.payload));
			damagePanelTargetStore.set(msg.target ?? null);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("disks", (event) => {
			const msg = DisksMessage.decode(toUint8Array(event.payload));
			leftDiskStore.set(msg.left);
			rightDiskStore.set(msg.right);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("flap", (event) => {
			const msg = FlapMessage.decode(toUint8Array(event.payload));
			flapMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("lidar/range", (event) => {
			const msg = LiDARRange.decode(toUint8Array(event.payload));
			lidarMessageStore.set(msg);
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen<unknown>("robotstate", (event) => {
			const msg = RobotStateMessage.decode(toUint8Array(event.payload));
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
