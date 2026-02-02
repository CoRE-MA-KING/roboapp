import type { LiDARRange } from "$lib/types/zenoh_message";
import { writable } from "svelte/store";

export const lidarMessageStore = writable<LiDARRange | null>(null);
