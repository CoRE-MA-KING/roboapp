import { type Target } from "$lib/types/zenoh_message";
import { type Writable, writable } from "svelte/store";

export const damagePanelStore: Writable<Target | null> = writable(null);
