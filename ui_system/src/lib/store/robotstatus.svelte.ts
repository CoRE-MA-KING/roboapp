import type { RobotStateMessage } from "$lib/types/zenoh_message";
import { writable } from "svelte/store";

export const robotStatusStore = writable<RobotStateMessage | null>(null);
