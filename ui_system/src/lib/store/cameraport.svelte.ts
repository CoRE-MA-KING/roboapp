import { type Writable, writable } from "svelte/store";

export const cameraPortStore: Writable<number> = writable(4120);
