import {
  getOfferCtaText,
  getOfferDisplayDescription,
  getOfferDisplayName,
  getOfferLogoStyle,
  getOfferPoints,
  getOrderedSelectedOffers,
} from './constructorDefaults'
import type { ShowcaseConfig, ShowcaseOffer } from './constructorDefaults'

export type PreviewMode = 'mobile' | 'desktop'

export type PreviewResult = {
  html: string
  containerClass: string
}

function esc(value: unknown): string {
  return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const PREVIEW_CSS = `
.landing-preview {
  border-radius: 14px;
  border: none;
  background: #ffffff;
  padding: 16px 14px 14px;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0 auto;
  width: 100%;
  max-width: 420px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #111827;
  font-size: 13px;
  line-height: 1.4;
  box-sizing: border-box;
}
.landing-preview *, .landing-preview *::before, .landing-preview *::after { box-sizing: border-box; }
.landing-preview, .landing-preview * { overflow-wrap: anywhere; word-break: normal; min-width: 0; }
.landing-preview .offer-card-cta { white-space: normal; max-width: 100%; }
.landing-preview.preview-desktop { max-width: 900px; }

/* Variants */
.landing-preview.landing-variant1 { background: linear-gradient(to bottom, #eff6ff, #ffffff 26%); }
.landing-preview.landing-variant2 { background: linear-gradient(to right, #ecfdf5, #ffffff 35%); }
.landing-preview.landing-variant3 { background: radial-gradient(circle at top, #0f172a, #020617 45%, #020617 100%); color: #e5e7eb; }
.landing-preview.landing-variant3 .landing-header-subtitle { color: #9ca3af; }
.landing-preview.landing-variant3 .offer-card { background: #020617; border-color: #1f2937; }
.landing-preview.landing-variant3 .landing-footer { border-top-color: #1f2937; color: #9ca3af; }
.landing-preview.landing-variant3 .offer-card-points, .landing-preview.landing-variant3 .offer-card-points li::marker { color: #ffffff; }
.landing-preview.landing-variant3 .landing-points { color: #ffffff; }
.landing-preview.landing-variant4 { background: #f3f4f6; }

/* Variant accents */
.landing-preview.landing-variant1 .offer-card.is-accent { background: #ede9fe; border-color: #c4b5fd; }
.landing-preview.landing-variant2 .offer-card.is-accent { background: #fef9c3; border-color: #fde68a; }
.landing-preview.landing-variant3 .offer-card.is-accent { border-color: #91d217; background: linear-gradient(to right, #1f6915 0%, #020617 70%); }

/* Variant4 header hero */
.landing-preview.landing-variant4 .landing-header-hero {
  display: flex; flex-direction: row; align-items: flex-start; justify-content: space-between; gap: 20px;
  padding: 20px 16px 24px; background: #ffffff; border-radius: 14px; margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.landing-preview.landing-variant4.preview-mobile .landing-header-hero { flex-direction: column; align-items: stretch; }
.landing-preview.landing-variant4.preview-mobile .landing-header-hero-img { width: 100%; height: 200px; align-self: stretch; }
.landing-preview.landing-variant4.preview-mobile .landing-footer { font-size: 10px; }
.landing-preview.landing-variant4.preview-mobile .offer-card { flex-direction: column; align-items: stretch; gap: 12px; }
.landing-preview.landing-variant4.preview-mobile .offer-card-logo { width: 100%; height: 100px; margin-right: 0; margin-bottom: 4px; }
.landing-preview.landing-variant4.preview-mobile .offer-card-text { margin-right: 0; }
.landing-preview.landing-variant4.preview-mobile .offer-card-cta { margin-left: 0; align-self: flex-start; }
.landing-preview.landing-variant4 .landing-header-hero-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
.landing-preview.landing-variant4 .landing-header-hero-text .landing-header-title { font-size: 30px; font-weight: 700; color: #111827; margin-bottom: 0; }
.landing-preview.landing-variant4 .landing-header-hero-text .landing-header-subtitle { font-size: 20px; color: #6b7280; line-height: 1.45; }
.landing-preview.landing-variant4 .landing-header-hero-img {
  flex-shrink: 0; width: 100px; height: 100px; border-radius: 14px;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%);
  display: flex; align-items: center; justify-content: center;
}
.landing-preview.landing-variant4 .offer-card { background: #ffffff; border: none; border-radius: 14px; padding: 14px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); min-height: 88px; }
.landing-preview.landing-variant4 .offer-card-text { flex: 1; min-width: 0; margin-right: 22px; }
.landing-preview.landing-variant4 .offer-card-logo { margin-right: 18px; }
.landing-preview.landing-variant4 .offer-card-cta { margin-left: auto; background: #f97316; color: #fff; }
.landing-preview.landing-variant4 .offer-card-meta { white-space: normal; }
.landing-preview.landing-variant4 .offer-card.is-accent { border: 1px solid #07810c; background: linear-gradient(to right, #76f370 0%, #ffffff 65%); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.landing-preview.landing-variant4 .landing-footer { border-top-color: #e5e7eb; color: #6b7280; }
.landing-preview.landing-variant4.preview-desktop .landing-footer { font-size: 16px; }
.landing-preview.landing-variant4 .landing-points { margin-top: 16px; padding-left: 34px; font-size: 18px; line-height: 1.45; }
.landing-preview.landing-variant4 .landing-points li { margin: 0 0 14px; }

/* Header */
.landing-preview .landing-header { display: flex; flex-direction: column; gap: 6px; }
.landing-preview .landing-header-title { font-size: 20px; font-weight: 700; }
.landing-preview .landing-header-subtitle { font-size: 13px; color: #6b7280; }

/* Offers grid */
.landing-preview .landing-offers-grid { margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; }
.landing-preview.preview-desktop.offers-two-col-desktop .landing-offers-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

/* Offer card */
.landing-preview .offer-card { border-radius: 10px; border: 1px solid #e5e7eb; background: rgba(255,255,255,0.8); padding: 10px 10px 12px; font-size: 12px; display: flex; flex-direction: row; align-items: center; gap: 12px; min-height: 72px; }
.landing-preview .offer-card-logo { width: 44px; height: 44px; flex-shrink: 0; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.landing-preview .offer-card-logo-icon { color: #fff; font-size: 18px; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.landing-preview .offer-card-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.landing-preview .offer-card-title { font-weight: 600; margin-bottom: 0; }
.landing-preview .offer-card-meta { font-size: 11px; color: #6b7280; }
.landing-preview .offer-card-cta { flex-shrink: 1; min-width: 0; max-width: 40%; padding: 6px 12px; font-size: 12px; border-radius: 999px; border: none; background: #2563eb; color: #ffffff; cursor: default; white-space: normal; overflow-wrap: anywhere; text-align: center; }
.landing-preview.preview-mobile .offer-card-cta { max-width: 50%; }
.landing-preview .offer-card-points { margin: 6px 0 0; padding-left: 26px; color: #111827; font-size: 11px; line-height: 1.35; list-style: disc; }
.landing-preview .offer-card-points li { margin: 0 0 4px; }
.landing-preview .offer-card-points li::marker { color: #111827; }

/* Landing points */
.landing-preview .landing-points { margin: 6px 0 0; padding-left: 26px; color: #111827; font-size: inherit; line-height: 1.35; list-style: disc; }
.landing-preview .landing-points li { margin: 0 0 4px; }
.landing-preview .landing-points li::marker { color: #f97316; }
.landing-preview.landing-variant1 .landing-points li::marker,
.landing-preview.landing-variant2 .landing-points li::marker,
.landing-preview.landing-variant3 .landing-points li::marker { color: #2563eb; }

/* Footer */
.landing-preview .landing-footer { margin-top: 16px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #6b7280; line-height: 1.4; white-space: pre-line; }
`

export { PREVIEW_CSS }

export default function buildPreviewHtml(
  config: ShowcaseConfig,
  offers: ShowcaseOffer[],
  previewMode: PreviewMode,
): PreviewResult {
  const selectedOffers = getOrderedSelectedOffers(offers, config)
  const designVariant = config.designVariant || 'variant1'
  const variantNum = designVariant.slice(-1)
  const title = esc(config.title || '')
  const description = esc(config.description || '')
  const legalInfo = esc(config.legalInfo || '').replace(/\n/g, '<br>')
  const landingPoints = (config.landingPoints || []).slice(0, 3)
  const twoCol = config.offersTwoColDesktop
  const accentedIds = config.accentedOfferIds || []

  const classes = ['landing-preview', `landing-variant${variantNum}`]
  if (previewMode === 'desktop') {
    classes.push('preview-desktop')
    if (twoCol) classes.push('offers-two-col-desktop')
  } else {
    classes.push('preview-mobile')
  }

  const landingPointsHtml = landingPoints
    .map((point) => `<li>${esc(point)}</li>`)
    .join('')

  const offersHtml = selectedOffers
    .map((offer, index) => {
      const displayName = getOfferDisplayName(offer, config)
      const descriptionText = getOfferDisplayDescription(offer, config)
      const ctaText = getOfferCtaText(offer, config)
      const points = getOfferPoints(offer, config).slice(0, 3)
      const isAccented = accentedIds.includes(offer.id)
      const gradient = getOfferLogoStyle(index)
      const letter = (displayName || 'O').charAt(0).toUpperCase()
      const pointsHtml = points.map((point) => `<li>${esc(point)}</li>`).join('')

      return `<div class="offer-card${isAccented ? ' is-accent' : ''}">
                <div class="offer-card-logo" style="background:${gradient}"><span class="offer-card-logo-icon">${letter}</span></div>
                <div class="offer-card-text">
                    <div class="offer-card-title">${esc(displayName)}</div>
                    ${descriptionText ? `<div class="offer-card-meta">${esc(descriptionText)}</div>` : ''}
                    ${pointsHtml ? `<ul class="offer-card-points">${pointsHtml}</ul>` : ''}
                </div>
                <button type="button" class="offer-card-cta">${esc(ctaText)}</button>
            </div>`
    })
    .join('')

  const headerContent = designVariant === 'variant4'
    ? `<header class="landing-header-hero">
            <div class="landing-header-hero-text">
                <div class="landing-header-title">${title || 'Без названия'}</div>
                <div class="landing-header-subtitle">${description || 'Описание лендинга не задано.'}</div>
                ${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ''}
            </div>
            <div class="landing-header-hero-img" aria-hidden="true"></div>
           </header>`
    : `<header class="landing-header">
            <div class="landing-header-title">${title || 'Без названия'}</div>
            <div class="landing-header-subtitle">${description || 'Описание лендинга не задано.'}</div>
            ${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ''}
           </header>`

  const html = `${headerContent}
        <div class="landing-offers-grid">${offersHtml}</div>
        <div class="landing-footer">${legalInfo}</div>`

  return { html, containerClass: classes.join(' ') }
}
