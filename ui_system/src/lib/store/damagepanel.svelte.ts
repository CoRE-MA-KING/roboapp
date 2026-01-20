import { type DamagePanelMessage } from "$lib/types/zenoh_message";
import { type Writable, writable } from "svelte/store";

export const damagePanelStore: Writable<DamagePanelMessage | null> = writable(null);
