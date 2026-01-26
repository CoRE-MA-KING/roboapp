import { type cameraID } from "$lib/types/zenoh_message";
import { type Writable, writable } from "svelte/store";

export const cameraIdStore: Writable<cameraID> = writable(0);
