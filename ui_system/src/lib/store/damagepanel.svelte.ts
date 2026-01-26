import { type Position } from "$lib/types/zenoh_message";
import { type Writable, writable } from "svelte/store";

export const damagePanelStore: Writable<Position | null> = writable(null);
