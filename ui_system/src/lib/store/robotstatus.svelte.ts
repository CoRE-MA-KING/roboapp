import { writable } from "svelte/store";

export const robotStatusStore = writable<string | null>(null);
