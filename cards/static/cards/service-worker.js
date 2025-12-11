self.addEventListener("install", event => {
  // Hier könnte man Assets cachen – für den Anfang reicht ein leerer SW
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  // Cleanup / zukünftige Cache-Strategien
});

self.addEventListener("fetch", event => {
  // Standard: alles normal durch das Netz
});

