import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import fr from './locales/fr.json'

export type SupportedLocale = 'en' | 'fr'

export const SUPPORTED_LOCALES: SupportedLocale[] = ['en', 'fr']
export const DEFAULT_LOCALE: SupportedLocale = 'en'

// Get initial locale from localStorage or browser
function getInitialLocale(): SupportedLocale {
  const stored = localStorage.getItem('locale')
  if (stored && SUPPORTED_LOCALES.includes(stored as SupportedLocale)) {
    return stored as SupportedLocale
  }

  // Try browser language
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.includes(browserLang as SupportedLocale)) {
    return browserLang as SupportedLocale
  }

  return DEFAULT_LOCALE
}

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getInitialLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: {
    en,
    fr
  }
})

export default i18n

// Helper to change locale
export function setLocale(locale: SupportedLocale) {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}
