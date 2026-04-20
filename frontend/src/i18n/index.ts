import { createI18n } from 'vue-i18n'

import en from '@/locales/en'
import ru from '@/locales/ru'

export type AppLocale = 'ru' | 'en'

const LOCALE_STORAGE_KEY = 'vitriona-locale'
const SUPPORTED_LOCALES: AppLocale[] = ['ru', 'en']

function isAppLocale(value: string | null | undefined): value is AppLocale {
  return Boolean(value && SUPPORTED_LOCALES.includes(value as AppLocale))
}

function getBrowserLocale(): AppLocale {
  const browserLocale = navigator.language.toLowerCase()
  return browserLocale.startsWith('ru') ? 'ru' : 'en'
}

export function getInitialLocale(): AppLocale {
  const savedLocale = localStorage.getItem(LOCALE_STORAGE_KEY)

  if (isAppLocale(savedLocale)) {
    return savedLocale
  }

  return getBrowserLocale()
}

function setDocumentLang(locale: AppLocale): void {
  document.documentElement.lang = locale
}

const initialLocale = getInitialLocale()

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'ru',
  messages: {
    ru,
    en,
  },
})

setDocumentLang(initialLocale)

export function setLocale(locale: AppLocale): void {
  i18n.global.locale.value = locale
  localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  setDocumentLang(locale)
}