import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'

// French only - i18n infrastructure kept for potential future expansion
export type SupportedLocale = 'fr'
export const LOCALE: SupportedLocale = 'fr'

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: LOCALE,
  fallbackLocale: LOCALE,
  messages: {
    fr
  }
})

export default i18n

// Set HTML lang attribute on init
document.documentElement.lang = LOCALE
