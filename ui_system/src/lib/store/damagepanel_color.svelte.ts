import { type Writable, writable } from "svelte/store";

export const damagePanelColorStore: Writable<string> = writable("black");
