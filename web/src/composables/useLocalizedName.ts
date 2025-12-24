import { useI18n } from 'vue-i18n'

interface LocalizedItem {
  name_en: string
  name_fr: string
}

export function useLocalizedName() {
  const { locale } = useI18n()

  function getName(item: LocalizedItem): string {
    return locale.value === 'fr' ? item.name_fr || item.name_en : item.name_en || item.name_fr
  }

  return { getName }
}
