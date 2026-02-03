<script lang="ts" module>
	import { cameraIdStore } from "$lib/store/cameraid.svelte";
	import { damagePanelStore } from "$lib/store/damagepanel.svelte";
	import { leftDiskStore, rightDiskStore } from "$lib/store/disks.svelte";
	import { flapMessageStore } from "$lib/store/flap.svelte";
	import { lidarMessageStore } from "$lib/store/lidar.svelte";
	import { robotStatusStore } from "$lib/store/robotstatus.svelte";
	import { RobotStatus } from "$lib/types/robot_status";
	import {
		CameraSwitchSchema,
		DamagePanelSchema,
		DisksSchema,
		FlapSchema,
		LiDARRangeSchema,
		RobotStateSchema
	} from "$lib/types/zenoh_message";
	import { listen } from "@tauri-apps/api/event";
</script>

<script lang="ts">
	$effect(() => {
		let unlistenPromise = listen("cam/switch", (event) => {
			const result = CameraSwitchSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				cameraIdStore.set(result.data.camera_id);
			} else {
				console.error("Validation failed for cam/switch:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("damagepanel", (event) => {
			const result = DamagePanelSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				damagePanelStore.set(result.data.target);
			} else {
				console.error("Validation failed for damagepanel:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("disks", (event) => {
			const result = DisksSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				leftDiskStore.set(result.data.left);
				rightDiskStore.set(result.data.right);
			} else {
				console.error("Validation failed for disks:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("flap", (event) => {
			const result = FlapSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				flapMessageStore.set(result.data);
			} else {
				console.error("Validation failed for flap:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("lidar/range", (event) => {
			const result = LiDARRangeSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				lidarMessageStore.set(result.data);
				console.log("LiDAR range message received", event.payload as string);
			} else {
				console.error("Validation failed for lidar/range:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});

	$effect(() => {
		let unlistenPromise = listen("robotstate", (event) => {
			const result = RobotStateSchema.safeParse(JSON.parse(event.payload as string));
			if (result.success) {
				const msg = result.data;
				if (msg.state in RobotStatus) {
					robotStatusStore.set(msg);
				} else {
					robotStatusStore.set(null);
				}
			} else {
				console.error("Validation failed for robotstate:", result.error);
			}
		});
		return () => {
			unlistenPromise.then((unlisten) => unlisten());
		};
	});
</script>
