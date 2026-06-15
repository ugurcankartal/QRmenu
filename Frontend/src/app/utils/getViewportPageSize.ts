export function getViewportPageSize(): number {
  if (typeof window === "undefined") {
    return 6;
  }

  const width = window.innerWidth;
  const height = window.innerHeight;
  const columns = width >= 1024 ? 3 : width >= 640 ? 2 : 1;
  const gridWidth = Math.min(1280, width - 32);
  const cardWidth = gridWidth / columns;
  const cardHeight = cardWidth * 0.75 + 108;
  const visibleRows = Math.max(1, Math.ceil((height * 0.6) / cardHeight));

  return Math.min(30, Math.max(3, columns * visibleRows));
}
