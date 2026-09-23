# Low Tide

A mobile-friendly bilging puzzle game with a paper-and-ink harbor aesthetic. Choose Lily, Alex, Steven, or Hana, complete jobs, earn coins and experience, and improve your pumps and hull seals.

## Run locally

This is a static HTML/CSS/JavaScript application. No build step or npm dependencies are required.

```sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000 in a browser. Serve over HTTP rather than opening index.html directly because the game uses JavaScript modules.

## Current game files

- `dist/index.html`: application structure
- `dist/rpg.mjs`: gameplay, input, timers, dialogs, and local saves
- `dist/rpg-model.mjs`: crew perks, jobs, ranks, rewards, and upgrades
- `dist/engine.mjs`: matching, refills, and special-piece mechanics
- `dist/pieces.mjs`: pattern and special-piece artwork
- `dist/rpg.css`: responsive interface and full-screen puzzle layout
- `dist/assets/ink-crew.webp` and `dist/assets/ink-scenes.webp`: current artwork

Other styles, modules, and images in `dist/` are retained from earlier prototypes; the current entry point does not load them.

## Playing

Swap horizontally adjacent pieces to match three or more colors and patterns across or down. Clears advance the job and remove water. Complete the work target before flooding. Successful jobs earn coins and XP; equipment upgrades and character specialties change how you handle the water. The emergency pump recharges on swaps that clear pieces.

Progress is stored in browser localStorage on the current device. Job progress pauses when the game is hidden. The puzzle fills the browser viewport; hiding browser controls depends on Fullscreen API support.

## Hosting

Any static host can serve `dist/`. The existing live version is https://pocket-bilge.vee-tat.chatgpt.site. Uploading this source to GitHub does not automatically change or synchronize that deployment.
