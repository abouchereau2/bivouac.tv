interface LocalizedItem {
  name: string
}

/**
 * Composable for getting item names (French-only version).
 * Kept for backward compatibility.
 */
export function useLocalizedName() {
  function getName(item: LocalizedItem): string {
    return item.name
  }

  return { getName }
}
