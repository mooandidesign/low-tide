// Deliberately drawn UI symbols: one viewBox, two-unit strokes, no font dependency.
const drawings=[
 '<circle cx="16" cy="16" r="10"/><circle cx="16" cy="16" r="4" fill="currentColor" stroke="none"/>',
 '<path d="M4 10q6-6 12 0t12 0M4 16q6-6 12 0t12 0M4 22q6-6 12 0t12 0"/>',
 '<path d="m16 3 6 9-6 4-6-4zm0 13 6 4-6 9-6-9zM3 16l9-6 4 6-4 6zm13 0 4-6 9 6-9 6z" fill="currentColor" stroke="none"/>',
 '<path d="M3 25 12 7l6 12 4-8 7 14Z" fill="currentColor" stroke="none"/><path d="m9 13 3-6 3 6" stroke="var(--tile-paper)"/>',
 '<rect x="6" y="6" width="20" height="20" rx="1"/><rect x="12" y="12" width="8" height="8" fill="currentColor" stroke="none"/>',
 '<path d="M8 4v24M24 4v24M4 8h24M4 24h24" stroke-width="3"/>',
 '<path d="M16 3 29 16 16 29 3 16Z"/><path d="m10 16 6-6 6 6-6 6z" fill="currentColor" stroke="none"/>',
 '<ellipse cx="16" cy="19" rx="8" ry="6" fill="currentColor"/><path d="m9 17-5-5-2-5m21 10 5-5 2-5M8 20l-5 4m21-4 5 4M12 13v-3m8 3v-3"/><circle cx="11" cy="9" r="2" fill="currentColor"/><circle cx="21" cy="9" r="2" fill="currentColor"/>',
 '<circle cx="16" cy="16" r="8"/><path d="M16 2v3m0 22v3M2 16h3m22 0h3M6 6l2 2m16 16 2 2M6 26l2-2M24 8l2-2"/><circle cx="13" cy="14" r="1" fill="currentColor"/><circle cx="19" cy="14" r="1" fill="currentColor"/>',
 '<path d="M6 17a10 10 0 0 1 20 0Z" fill="currentColor"/><path d="M10 19v3q-3 3 0 7m6-10v10m6-10v3q3 3 0 7"/>'
];
export const pieceNames=['coral red piece','turquoise piece','gold piece','olive piece','purple piece','peach piece','blue piece','crab: drain water to release','pufferfish: burst clears nearby pieces','jellyfish: sweep clears one color'];
const specials=[
 '<path d="M8 16q8-8 16 0v8H8Z" fill="currentColor"/><path d="M8 17 3 12M24 17l5-5M8 22l-5 5m21-5 5 5M13 11V6m6 5V6"/><circle cx="13" cy="18" r="1" fill="var(--tile-paper)" stroke="none"/><circle cx="19" cy="18" r="1" fill="var(--tile-paper)" stroke="none"/>',
 '<path d="M5 18q0-11 11-11t11 11q0 10-11 10T5 18Z" fill="currentColor"/><path d="M7 9 4 5m10 2-2-5m11 8 4-4m1 13 3 2M6 24l-4 3"/><circle cx="12" cy="16" r="1.5" fill="var(--tile-paper)" stroke="none"/><circle cx="20" cy="16" r="1.5" fill="var(--tile-paper)" stroke="none"/><path d="m13 22 3 2 3-2" stroke="var(--tile-paper)"/>',
 '<path d="M5 17a11 11 0 0 1 22 0Z" fill="currentColor"/><path d="M8 20q-3 3 0 7m5-7q3 5 0 9m5-9q-2 4 1 8m5-8q3 4 0 8"/><circle cx="11" cy="11" r="1" fill="var(--tile-paper)" stroke="none"/><circle cx="21" cy="11" r="1" fill="var(--tile-paper)" stroke="none"/>'
];
export const pieceSVG=i=>i<7?'':`<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${specials[i-7]}</svg>`;
