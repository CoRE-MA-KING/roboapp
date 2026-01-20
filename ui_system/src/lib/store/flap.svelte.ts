import type { FlapMessage } from "$lib/types/zenoh_message";
import { writable } from "svelte/store";

export const flapMessageStore = writable<FlapMessage | null>(null);
