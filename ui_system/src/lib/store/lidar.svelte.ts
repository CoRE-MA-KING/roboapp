import type { LiDARMessage } from "$lib/types/zenoh_message";
import { writable } from "svelte/store";

export const lidarMessageStore = writable<LiDARMessage | null>(null);
