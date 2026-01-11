import { writable, type Writable } from "svelte/store";

export const leftDiskStore: Writable<number> = writable(0);
export const rightDiskStore: Writable<number> = writable(0);
