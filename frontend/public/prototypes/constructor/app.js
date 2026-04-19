// Простое состояние приложения
const state = {
  title: "Займы онлайн со ставкой от 0%",
  description: "Подобрали предложения с одобрением заявки за 15 минут!",
  designVariant: "variant1",
  ctaText: "Оформить",
  previewMode: "mobile",
  offers: [],
  selectedOfferIds: new Set(),
  accentedOfferIds: new Set(),
  pendingDeleteOfferIds: new Set(),
  filterGeo: "",
  filterSource: "",
  sortMetric: "none",
  offerIdQuery: "",
  rankingMode: "auto",
  trackingLink: "pxlsync.su",
  customJs: "",
  domainType: "system",
  systemDomain: "smart-1.smartconstruct.app",
  customDomain: "",
  showcaseOrder: [],
  pinnedOfferIds: new Set(),
  permanentTags: [],
  legalInfo:
    "Компания не является банком и не принимает решения о займах. Мы используем файлы cookie для того, чтобы предоставить пользователям больше возможностей при посещении сайта. Оставаясь на сайте, Вы соглашаетесь на обработку файлов cookie.",
  offerDisplayNames: {},
  offerDisplayDescriptions: {},
  offerCtaTexts: {},
  offerPoints: {},
  landingPoints: [],
  offersTwoColDesktop: true,
  trafficBackMode: "none",
  trafficBackCustomUrl: "",
  trafficBackOfferId: ""
};

function getOfferDisplayName(offer) {
  return state.offerDisplayNames[offer.id] ?? offer.name;
}

const DEFAULT_OFFER_DESCRIPTION = "Оформите займ с одобрением за 5 минут";

function getOfferDisplayDescription(offer) {
  if (Object.prototype.hasOwnProperty.call(state.offerDisplayDescriptions, offer.id)) {
    return state.offerDisplayDescriptions[offer.id] ?? "";
  }
  return DEFAULT_OFFER_DESCRIPTION;
}

function getOfferCtaText(offer) {
  return state.offerCtaTexts[offer.id] ?? state.ctaText ?? "Подать заявку";
}

const DEFAULT_OFFER_POINT = "Ставка от 0%";

function getOfferPoints(offer) {
  const points = state.offerPoints[offer.id];
  return Array.isArray(points) ? points : [];
}

function getLandingPoints() {
  return Array.isArray(state.landingPoints) ? state.landingPoints : [];
}

const DESCRIPTION_MAX = 500;

const OFFER_LOGO_GRADIENTS = [
  "linear-gradient(135deg, #f59e0b 0%, #7c3aed 100%)",
  "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
  "linear-gradient(135deg, #10b981 0%, #059669 100%)",
  "linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)",
  "linear-gradient(135deg, #f97316 0%, #eab308 100%)",
  "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
  "linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)",
  "linear-gradient(135deg, #84cc16 0%, #22c55e 100%)"
];

function getOfferLogoStyle(offerId) {
  return OFFER_LOGO_GRADIENTS[(offerId - 1) % OFFER_LOGO_GRADIENTS.length];
}

// Таймеры подтверждения удаления (id -> { endAt })
const pendingDelete = new Map();
let pendingDeleteTicker = null;

// Фиктивные офферы
const OFFERS = [
  { id: 1, publicId: "7734", name: "Crypto Lead Gen EU", geo: "DE", source: "Facebook", epc: 2.3, cr: 1.8, score: 780 },
  { id: 2, publicId: "482915", name: "Nutra Trial USA", geo: "US", source: "Google", epc: 1.7, cr: 2.1, score: 650 },
  { id: 3, publicId: "90512", name: "Dating App Tier-2", geo: "BR", source: "TikTok", epc: 0.9, cr: 3.6, score: 540 },
  { id: 4, publicId: "610843", name: "Sweepstakes Mobile", geo: "RU", source: "Push", epc: 0.6, cr: 4.2, score: 430 },
  { id: 5, publicId: "34019", name: "iGaming CPL", geo: "PL", source: "Native", epc: 1.3, cr: 2.7, score: 710 },
  { id: 6, publicId: "598204", name: "Finance Lead US", geo: "US", source: "Facebook", epc: 2.9, cr: 1.2, score: 910 },
  { id: 7, publicId: "41706", name: "Utilities Desktop", geo: "IN", source: "Push", epc: 0.4, cr: 5.0, score: 320 },
  { id: 8, publicId: "268950", name: "Adult Dating", geo: "UA", source: "Native", epc: 1.0, cr: 3.1, score: 590 }
];

// Инициализация
document.addEventListener("DOMContentLoaded", () => {
  state.offers = OFFERS;
  OFFERS.slice(0, 3).forEach(o => state.selectedOfferIds.add(o.id));
  state.accentedOfferIds.add(OFFERS[1].id);
  syncShowcaseOrderFromRanking();
  state.offerPoints[OFFERS[0].id] = state.offerPoints[OFFERS[0].id] || [DEFAULT_OFFER_POINT];

  bindStepTabs();
  bindDesignStep();
  bindPreviewModeToggle();
  setupOfferFilters();
  bindAnalyticsStep();
  bindSelectAllOffers();
  bindOfferIdSearch();
  bindOpenResultLanding();
  bindRankingModeToggle();
  bindPermanentTags();
  bindLegalInfo();
  bindTrafficBack();
  bindLandingPoints();

  renderOffersTable();
  renderPreview();
  renderPermanentTagsRows();
  syncRankingToggleAvailability();
});

function bindOfferIdSearch() {
  const input = document.getElementById("offer-id-search");
  if (!input) return;
  input.value = state.offerIdQuery || "";
  input.addEventListener("input", () => {
    const digits = input.value.replace(/\D/g, "");
    if (digits !== input.value) input.value = digits;
    state.offerIdQuery = digits;
    renderOffersTable();
  });
}

// Открытие итогового лендинга в новой вкладке
function bindOpenResultLanding() {
  const btn = document.getElementById("open-result-landing");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const landingHtml = buildResultLandingHtml();
    const newWin = window.open("", "_blank");
    if (!newWin) return;
    newWin.document.write(landingHtml);
    newWin.document.close();
  });
}

function buildResultLandingHtml() {
  const selectedOffers = getShowcaseOrderedOffers();

  const baseHref = (window?.location?.href || "").replace(/[^/]*$/, "");
  const landingPointsHtml = getLandingPoints()
    .slice(0, 3)
    .map(p => `<li>${String(p).replace(/</g, "&lt;").replace(/>/g, "&gt;")}</li>`)
    .join("");
  const offersHtml = selectedOffers
    .map(
      o => {
        const logoGradient = getOfferLogoStyle(o.id);
        const logoLetter = (getOfferDisplayName(o)).charAt(0).toUpperCase();
        const desc = getOfferDisplayDescription(o);
        const pointsHtml = getOfferPoints(o)
          .slice(0, 3)
          .map(p => `<li>${String(p).replace(/</g, "&lt;").replace(/>/g, "&gt;")}</li>`)
          .join("");
        return `
        <div class="offer-card ${state.accentedOfferIds.has(o.id) ? "is-accent" : ""}">
          <div class="offer-card-logo" style="background:${logoGradient}"><span class="offer-card-logo-icon">${logoLetter}</span></div>
          <div class="offer-card-text">
            <div class="offer-card-title">${getOfferDisplayName(o)}</div>
            ${desc
              ? `<div class="offer-card-meta">${desc.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>`
              : ""}
            ${pointsHtml ? `<ul class="offer-card-points">${pointsHtml}</ul>` : ""}
          </div>
          <button type="button" class="offer-card-cta">${getOfferCtaText(o).replace(/</g, "&lt;").replace(/>/g, "&gt;")}</button>
        </div>`;
      }
    )
    .join("");

  return `<!DOCTYPE html>
  <html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <title>${state.title || "Лендинг"}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    ${baseHref ? `<base href="${baseHref}">` : ""}
    <style>
      *, *::before, *::after { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #020617;
        color: #e5e7eb;
      }
      body.result-variant1 {
        background: #eff6ff;
        color: #111827;
      }
      body.result-variant2 {
        background: #ecfdf5;
        color: #111827;
      }
      body.result-variant4 {
        background: #f3f4f6;
        color: #111827;
      }
      html, body { overflow-x: hidden; }
      .page-wrap {
        min-height: 100vh;
        padding: 24px 16px 32px;
        display: flex;
        justify-content: stretch;
        max-width: 100%;
        min-width: 0;
      }
      .landing-shell {
        width: 100%;
        max-width: 100%;
        min-width: 0;
        border-radius: 20px;
        background: radial-gradient(circle at top, #0b1120, #020617 55%, #020617 100%);
        padding: 24px 20px 20px;
        border: none;
      }
      .landing-header {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .landing-header-title {
        font-size: 24px;
        font-weight: 700;
      }
      .landing-header-subtitle {
        font-size: 14px;
        color: #9ca3af;
      }
      .landing-offers-title {
        margin-top: 18px;
        font-size: 14px;
        font-weight: 600;
      }
      .landing-offers-grid {
        margin-top: 10px;
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        gap: 10px;
      }
      .offer-card {
        border-radius: 12px;
        border: 1px solid #1f2937;
        background: rgba(15, 23, 42, 0.9);
        padding: 10px 12px;
        font-size: 13px;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 10px;
      }
      .offer-card-logo {
        width: 44px;
        height: 44px;
        flex-shrink: 0;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .offer-card-logo-icon {
        color: #fff;
        font-size: 18px;
        font-weight: 700;
      }
      .offer-card-text {
        flex: 1;
        min-width: 0;
      }
      .offer-card .offer-card-title { margin-bottom: 2px; }
      .offer-card .offer-card-meta { font-size: 12px; color: #9ca3af; }
      .landing-variant3 .offer-card.is-accent {
        border-color: #91d217;
        background: linear-gradient(to right, #1f6915 0%, #020617 70%);
      }
      .landing-shell.landing-variant1 {
        background: linear-gradient(to bottom, #eff6ff, #ffffff 26%);
        color: #111827;
      }
      .landing-shell.landing-variant1 .landing-header-title {
        color: #111827;
        font-size: 54px;
      }
      .landing-shell.landing-variant1 .landing-header-subtitle {
        color: #6b7280;
        font-size: 24px;
      }
      .landing-shell.landing-variant1 .landing-header {
        gap: 16px;
      }
      .landing-shell.landing-variant1 .offer-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
      }
      .landing-shell.landing-variant1 .offer-card.is-accent {
        background: #ede9fe;
        border-color: #c4b5fd;
      }
      .landing-shell.landing-variant1 .offer-card-title {
        color: #111827;
        font-size: 22px;
        margin-bottom: 12px;
      }
      .landing-shell.landing-variant1 .offer-card-meta {
        color: #6b7280;
        font-size: 14px;
      }
      .landing-shell.landing-variant1 .landing-footer {
        color: #6b7280;
        border-top-color: #e5e7eb;
      }
      .landing-shell.landing-variant2 {
        background: linear-gradient(to right, #ecfdf5, #ffffff 35%);
        color: #111827;
      }
      .landing-shell.landing-variant2 .landing-header-title {
        color: #111827;
        font-size: 54px;
      }
      .landing-shell.landing-variant2 .landing-header-subtitle {
        color: #6b7280;
        font-size: 24px;
      }
      .landing-shell.landing-variant2 .landing-header {
        gap: 16px;
      }
      .landing-shell.landing-variant2 .offer-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
      }
      .landing-shell.landing-variant2 .offer-card.is-accent {
        background: #fef9c3;
        border-color: #fde68a;
      }
      .landing-shell.landing-variant2 .offer-card-title {
        color: #111827;
        font-size: 22px;
        margin-bottom: 12px;
      }
      .landing-shell.landing-variant2 .offer-card-meta {
        color: #6b7280;
        font-size: 14px;
      }
      .landing-shell.landing-variant2 .landing-footer {
        color: #6b7280;
        border-top-color: #e5e7eb;
      }
      .landing-shell.landing-variant3 .landing-header-title {
        font-size: 54px;
      }
      .landing-shell.landing-variant3 .landing-header-subtitle {
        font-size: 24px;
      }
      .landing-shell.landing-variant3 .landing-header {
        gap: 16px;
      }
      .landing-shell.landing-variant3 .offer-card-title {
        font-size: 22px;
        margin-bottom: 12px;
      }
      .landing-shell.landing-variant3 .offer-card-meta {
        font-size: 14px;
      }
      .landing-shell.landing-variant1 > section,
      .landing-shell.landing-variant2 > section,
      .landing-shell.landing-variant3 > section {
        margin-top: 60px;
      }
      .landing-shell.landing-variant1 .landing-points,
      .landing-shell.landing-variant2 .landing-points,
      .landing-shell.landing-variant3 .landing-points {
        margin-top: 12px;
        font-size: 20px;
      }
      .landing-shell.landing-variant1 .landing-points li,
      .landing-shell.landing-variant2 .landing-points li,
      .landing-shell.landing-variant3 .landing-points li {
        margin-bottom: 8px;
      }
      .landing-shell.landing-variant4 {
        background: #f3f4f6;
        color: #111827;
      }
      .landing-shell.landing-variant4 .landing-header {
        flex-direction: row;
        align-items: flex-start;
        justify-content: space-between;
        gap: 20px;
        padding: 20px 24px 24px;
        background: #fff;
        border-radius: 14px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      }
      .landing-shell.landing-variant4 .landing-header-hero-text {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      @media (max-width: 640px) {
        .landing-shell.landing-variant4 .landing-header {
          flex-direction: column;
          align-items: stretch;
          min-width: 0;
        }
        .landing-shell.landing-variant4 .landing-header-hero-text {
          min-width: 0;
        }
        .landing-shell.landing-variant4 .landing-header-hero-img {
          width: 100%;
          max-width: 100%;
          height: 340px;
          min-height: 200px;
          align-self: stretch;
          flex-shrink: 0;
          border-radius: 14px;
          background-image:
            url("assets/header-hero.png"),
            linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%);
          background-size: cover, cover;
          background-position: center, center;
          background-repeat: no-repeat, no-repeat;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .landing-shell.landing-variant4 .landing-header-hero-text .landing-header-title {
          font-size: 22px;
        }
        .landing-shell.landing-variant4 .landing-header-hero-text .landing-header-subtitle {
          font-size: 16px;
        }
        .landing-shell.landing-variant4 .offer-card {
          padding: 16px 18px;
          min-height: 0;
          min-width: 0;
          flex-direction: column;
          align-items: stretch;
          gap: 12px;
          background: #fff;
          border: none;
          border-radius: 14px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .landing-shell.landing-variant4 .offer-card.is-accent {
          border: 1px solid #07810c;
          background: linear-gradient(to right, #76f370 0%, #ffffff 65%);
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .landing-shell.landing-variant4 .offer-card-logo {
          width: 100%;
          height: 100px;
          margin-right: 0;
          margin-bottom: 4px;
        }
        .landing-shell.landing-variant4 .offer-card-logo-icon {
          font-size: 40px;
        }
        .landing-shell.landing-variant4 .offer-card-text {
          margin-right: 0;
          min-width: 0;
        }
        .landing-shell.landing-variant4 .offer-card-cta {
          margin-left: 0;
          align-self: flex-start;
          padding: 8px 14px;
          font-size: 14px;
        }
        .landing-shell.landing-variant4 .offer-card-title {
          font-size: 16px;
        }
        .landing-shell.landing-variant4 .offer-card-meta {
          font-size: 13px;
        }
        .landing-shell.landing-variant4 .landing-offers-grid {
          min-width: 0;
        }
        .landing-shell.landing-variant4 .landing-footer {
          font-size: 10px;
          min-width: 0;
        }
      }
      @media (min-width: 641px) {
        .landing-shell.landing-variant4 .landing-header-title {
          font-size: 30px;
          color: #111827;
        }
        .landing-shell.landing-variant4 .landing-header-hero-text .landing-header-title {
          margin-bottom: 0;
        }
        .landing-shell.landing-variant4 .landing-header-subtitle {
          color: #6b7280;
          font-size: 20px;
        }
        .landing-shell.landing-variant4 .landing-header-hero-img {
          width: 560px;
          height: 290px;
          border-radius: 18px;
          background-image:
            url("assets/header-hero.png"),
            linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%);
          background-size: cover, cover;
          background-position: center, center;
          background-repeat: no-repeat, no-repeat;
          flex-shrink: 0;
        }
        .landing-shell.landing-variant4 .offer-card {
          background: #fff;
          border: none;
          border-radius: 14px;
          padding: 28px 32px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
          width: 100%;
          min-height: 171px;
          margin: 0 auto;
        }
        .landing-shell.landing-variant4 .offer-card-cta {
          background: #f97316;
          padding: 9px 18px;
          font-size: 18px;
          align-self: center;
        }
        .landing-shell.landing-variant4 .offer-card-logo {
          width: 260px;
          height: 170px;
          border-radius: 18px;
          margin-right: 18px;
        }
        .landing-shell.landing-variant4 .offer-card-logo-icon {
          font-size: 54px;
        }
        .landing-shell.landing-variant4 .offer-card-title {
          font-size: 24px;
          line-height: 1.2;
        }
        .landing-shell.landing-variant4 .offer-card-meta {
          font-size: 16px;
          line-height: 1.35;
        }
        .landing-shell.landing-variant4 .offer-card-content {
          gap: 0;
        }
        .landing-shell.landing-variant4 .offer-card-text {
          flex: 1;
          min-width: 0;
          margin-right: 22px;
        }
        .landing-shell.landing-variant4 .offer-card-cta {
          margin-left: auto;
        }
        .landing-shell.landing-variant4 .offer-card-meta {
          white-space: normal;
        }
        .landing-shell.landing-variant4 .offer-card.is-accent {
          border: 1px solid #07810c;
          background: linear-gradient(to right, #76f370 0%, #ffffff 65%);
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .landing-shell.landing-variant4 .landing-footer {
          border-top-color: #e5e7eb;
          color: #6b7280;
          font-size: 20px;
        }
      }
      .offer-card-title {
        font-weight: 600;
        margin-bottom: 4px;
      }
      .offer-card-meta {
        font-size: 12px;
        color: #9ca3af;
      }
      .offer-card-points {
        margin: 12px 0 0;
        padding-left: 26px;
        color: #111827;
        font-size: 16px;
        line-height: 1.35;
      }
      .offer-card-points li { margin: 0 0 4px; }
      .offer-card-points li::marker { color: #111827; }
      .landing-variant3 .offer-card-points,
      .landing-variant3 .offer-card-points li::marker {
        color: #ffffff;
      }
      .landing-points {
        margin: 6px 0 0;
        padding-left: 26px;
        color: #111827;
        font-size: inherit;
        line-height: 1.35;
      }
      .landing-points li { margin: 0 0 4px; }
      .landing-points li::marker { color: #f97316; }
      .landing-variant1 .landing-points li::marker,
      .landing-variant2 .landing-points li::marker,
      .landing-variant3 .landing-points li::marker {
        color: #2563eb;
      }
      .landing-variant3 .landing-points { color: #ffffff; }
      .landing-shell.landing-variant4 .landing-points {
        margin-top: 16px;
        padding-left: 34px;
        font-size: 18px;
        line-height: 1.45;
      }
      .landing-shell.landing-variant4 .landing-points li {
        margin: 0 0 14px;
      }
      .offer-card-cta {
        margin-left: auto;
        display: block;
        padding: 8px 14px;
        font-size: 13px;
        border-radius: 999px;
        border: none;
        background: #2563eb;
        color: #ffffff;
        cursor: default;
      }
      .note {
        margin-top: 16px;
        font-size: 11px;
        color: #6b7280;
      }
      .tech {
        margin-top: 20px;
        font-size: 12px;
        color: #9ca3af;
      }
      .tech strong {
        color: #e5e7eb;
      }
      .landing-footer {
        margin-top: 18px;
        padding-top: 12px;
        border-top: 1px solid #1f2937;
        font-size: 11px;
        color: #9ca3af;
        line-height: 1.4;
      }
      @media (min-width: 641px) {
        body.result-offers-two-col-desktop .landing-offers-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 12px;
        }
        body.result-offers-two-col-desktop .landing-shell.landing-variant4 .offer-card-logo {
          width: 160px;
          height: 140px;
        }
        .landing-shell.landing-variant1 .offer-card-logo,
        .landing-shell.landing-variant2 .offer-card-logo,
        .landing-shell.landing-variant3 .offer-card-logo {
          width: 94px;
          height: 64px;
        }
        .landing-shell.landing-variant1 .offer-card,
        .landing-shell.landing-variant2 .offer-card,
        .landing-shell.landing-variant3 .offer-card {
          gap: 30px;
        }
        .landing-shell.landing-variant1 .landing-footer,
        .landing-shell.landing-variant2 .landing-footer,
        .landing-shell.landing-variant3 .landing-footer {
          font-size: 14px;
        }
        .landing-shell.landing-variant1 > section,
        .landing-shell.landing-variant2 > section,
        .landing-shell.landing-variant3 > section {
          margin-top: 40px;
        }
      }
      @media (max-width: 640px) {
        .page-wrap { padding: 12px 10px 20px; }
        .landing-shell {
          border-radius: 0;
          max-width: 100%;
          min-width: 0;
          padding: 16px 12px 20px;
          border-left: none;
          border-right: none;
        }
        .landing-shell.landing-variant4 .landing-header {
          padding-left: 16px;
          padding-right: 16px;
        }
        .landing-header-title {
          font-size: 20px;
        }
        .landing-shell .landing-footer {
          font-size: 10px;
        }
        .landing-shell.landing-variant1 .landing-header-title,
        .landing-shell.landing-variant2 .landing-header-title,
        .landing-shell.landing-variant3 .landing-header-title {
          font-size: 34px;
        }
        .landing-shell.landing-variant1 .landing-header-subtitle,
        .landing-shell.landing-variant2 .landing-header-subtitle,
        .landing-shell.landing-variant3 .landing-header-subtitle {
          font-size: 20px;
        }
        .landing-shell.landing-variant1 .landing-footer,
        .landing-shell.landing-variant2 .landing-footer,
        .landing-shell.landing-variant3 .landing-footer {
          font-size: 12px;
        }
        .landing-shell.landing-variant1 .offer-card,
        .landing-shell.landing-variant2 .offer-card,
        .landing-shell.landing-variant3 .offer-card {
          flex-direction: column;
          align-items: stretch;
          gap: 12px;
        }
        .landing-shell.landing-variant1 .offer-card-logo,
        .landing-shell.landing-variant2 .offer-card-logo,
        .landing-shell.landing-variant3 .offer-card-logo {
          width: 100%;
        }
        .landing-shell.landing-variant1 .offer-card-text,
        .landing-shell.landing-variant2 .offer-card-text,
        .landing-shell.landing-variant3 .offer-card-text {
          width: 100%;
        }
        .landing-shell.landing-variant1 .offer-card-cta,
        .landing-shell.landing-variant2 .offer-card-cta,
        .landing-shell.landing-variant3 .offer-card-cta {
          margin-left: 0;
          align-self: flex-start;
        }
        .landing-shell.landing-variant1 .offer-card-title,
        .landing-shell.landing-variant2 .offer-card-title,
        .landing-shell.landing-variant3 .offer-card-title {
          font-size: 16px;
        }
        .landing-shell.landing-variant1 .offer-card-points,
        .landing-shell.landing-variant2 .offer-card-points,
        .landing-shell.landing-variant3 .offer-card-points {
          font-size: 14px;
        }
      }
    </style>
  </head>
  <body class="${[
    state.designVariant === "variant1"
      ? "result-variant1"
      : state.designVariant === "variant2"
        ? "result-variant2"
        : state.designVariant === "variant4"
          ? "result-variant4"
          : "",
    state.offersTwoColDesktop ? "result-offers-two-col-desktop" : ""
  ]
    .filter(Boolean)
    .join(" ")}">
    <div class="page-wrap">
      <main class="landing-shell landing-variant${state.designVariant.slice(-1)}">
        <header class="landing-header${state.designVariant === "variant4" ? " landing-header-hero" : ""}">
          ${state.designVariant === "variant4"
    ? `<div class="landing-header-hero-text"><div class="landing-header-title">${state.title || "Без названия"}</div><div class="landing-header-subtitle">${state.description || "Описание лендинга не задано."}</div>${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ""}</div><div class="landing-header-hero-img" aria-hidden="true"></div>`
    : `<div class="landing-header-title">${state.title || "Без названия"}</div><div class="landing-header-subtitle">${state.description || "Описание лендинга не задано."}</div>${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ""}` }
        </header>
        <section>
          <div class="landing-offers-grid">
            ${offersHtml || ""}
          </div>
        </section>
        <div class="landing-footer">${(state.legalInfo || "").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>")}</div>
      </main>
    </div>
  </body>
  </html>`;
}

// Чекбокс "выбрать все" для текущего списка
function bindSelectAllOffers() {
  const headerCheckbox = document.getElementById("offers-select-all");
  if (!headerCheckbox) return;

  headerCheckbox.addEventListener("change", () => {
    const filtered = getFilteredAndSortedOffers();
    if (headerCheckbox.checked) {
      filtered.forEach(o => {
        state.selectedOfferIds.add(o.id);
        syncShowcaseOrderOnSelectionChange(o.id, null);
      });
    } else {
      filtered.forEach(o => {
        state.selectedOfferIds.delete(o.id);
        syncShowcaseOrderOnSelectionChange(null, o.id);
      });
    }
    renderOffersTable();
    renderPreview();
  });
}

// Переключение шагов
function bindStepTabs() {
  const tabs = document.querySelectorAll(".step-tab");
  const panels = {
    design: document.getElementById("step-design"),
    content: document.getElementById("step-content"),
    analytics: document.getElementById("step-analytics")
  };

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const step = tab.dataset.step;
      tabs.forEach(t => t.classList.toggle("active", t === tab));
      Object.entries(panels).forEach(([name, panel]) => {
        panel.classList.toggle("hidden", name !== step);
      });
    });
  });
}

// Шаг "Дизайн"
function bindDesignStep() {
  const titleInput = document.getElementById("landing-title");
  const descInput = document.getElementById("landing-description");
  const descCounter = document.getElementById("landing-description-counter");
  const variantInputs = document.querySelectorAll('input[name="design-variant"]');
  const twoColCheckbox = document.getElementById("offers-two-col-desktop");

  // Установим начальные значения
  syncDesignInputsFromState();

  titleInput.addEventListener("input", () => {
    state.title = titleInput.value || "Без названия";
    renderPreview();
  });

  descInput.addEventListener("input", () => {
    if (descInput.value.length > DESCRIPTION_MAX) {
      descInput.value = descInput.value.slice(0, DESCRIPTION_MAX);
    }
    state.description = descInput.value || "";
    updateDescriptionCounter(descInput, descCounter);
    renderPreview();
  });

  variantInputs.forEach(input => {
    input.addEventListener("change", () => {
      state.designVariant = input.value;
      renderPreview();
    });
  });

  if (twoColCheckbox) {
    twoColCheckbox.addEventListener("change", () => {
      state.offersTwoColDesktop = !!twoColCheckbox.checked;
      renderPreview();
    });
  }

  updateDescriptionCounter(descInput, descCounter);
}

// Переключение формата превью (моб./десктоп)
function bindPreviewModeToggle() {
  const buttons = document.querySelectorAll(".preview-mode-btn");
  const preview = document.getElementById("landing-preview");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode === "desktop" ? "desktop" : "mobile";
      state.previewMode = mode;

      buttons.forEach(b => b.classList.toggle("active", b === btn));

      if (preview) {
        preview.classList.remove("preview-mobile", "preview-desktop", "offers-two-col-desktop");
        preview.classList.add(mode === "desktop" ? "preview-desktop" : "preview-mobile");
        if (mode === "desktop" && state.offersTwoColDesktop) {
          preview.classList.add("offers-two-col-desktop");
        }
      }
    });
  });
}

// Настройка фильтров и сортировки офферов
function setupOfferFilters() {
  const geoSelect = document.getElementById("filter-geo");
  const sourceSelect = document.getElementById("filter-source");
  const sortSelect = document.getElementById("sort-metric");

  // Заполним уникальные значения
  const geos = Array.from(new Set(OFFERS.map(o => o.geo))).sort();
  const sources = Array.from(new Set(OFFERS.map(o => o.source))).sort();

  geos.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g;
    opt.textContent = g;
    geoSelect.appendChild(opt);
  });

  sources.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    sourceSelect.appendChild(opt);
  });

  geoSelect.addEventListener("change", () => {
    state.filterGeo = geoSelect.value;
    renderOffersTable();
    renderPreview();
  });

  sourceSelect.addEventListener("change", () => {
    state.filterSource = sourceSelect.value;
    renderOffersTable();
    renderPreview();
  });

  sortSelect.addEventListener("change", () => {
    state.sortMetric = sortSelect.value;
    syncShowcaseOrderFromRanking();
    renderOffersTable();
    renderPreview();
    syncRankingToggleAvailability();
  });
}

function syncRankingToggleAvailability() {
  const optTableLabel = document.getElementById("rank-opt-table");
  const optTableInput = document.querySelector('input[name="ranking-mode"][value="table"]');
  const optAutoInput = document.querySelector('input[name="ranking-mode"][value="auto"]');

  const disabled = state.sortMetric === "none";
  if (optTableInput) optTableInput.disabled = disabled;
  if (optTableLabel) optTableLabel.classList.toggle("is-disabled", disabled);

  if (disabled && state.rankingMode === "table") {
    state.rankingMode = "auto";
    if (optAutoInput) optAutoInput.checked = true;
  }
}

function bindRankingModeToggle() {
  const inputs = document.querySelectorAll('input[name="ranking-mode"]');
  if (!inputs.length) return;

  inputs.forEach(input => {
    input.addEventListener("change", () => {
      const next = input.value === "table" ? "table" : "auto";
      if (next === "table" && state.sortMetric === "none") {
        syncRankingToggleAvailability();
        return;
      }
      state.rankingMode = next;
      syncShowcaseOrderFromRanking();
      renderPreview();
    });
  });
}

function getFilteredAndSortedOffers() {
  let filtered = [...OFFERS];

  if (state.offerIdQuery) {
    if (state.offerIdQuery.length > 6) {
      filtered = [];
    } else {
      filtered = filtered.filter(o => String(o.publicId || "").startsWith(state.offerIdQuery));
    }
  }

  if (state.filterGeo) {
    filtered = filtered.filter(o => o.geo === state.filterGeo);
  }
  if (state.filterSource) {
    filtered = filtered.filter(o => o.source === state.filterSource);
  }

  if (state.sortMetric === "epc") {
    filtered.sort((a, b) => b.epc - a.epc);
  } else if (state.sortMetric === "cr") {
    filtered.sort((a, b) => b.cr - a.cr);
  } else if (state.sortMetric === "score") {
    filtered.sort((a, b) => b.score - a.score);
  }

  return filtered;
}

function getRankedSelectedOffersForShowcase() {
  const selected = OFFERS.filter(o => state.selectedOfferIds.has(o.id));

  if (state.rankingMode === "table" && state.sortMetric !== "none") {
    const list = [...selected];
    if (state.sortMetric === "epc") {
      list.sort((a, b) => b.epc - a.epc);
    } else if (state.sortMetric === "cr") {
      list.sort((a, b) => b.cr - a.cr);
    } else if (state.sortMetric === "score") {
      list.sort((a, b) => b.score - a.score);
    }
    return list;
  }

  return [...selected].sort((a, b) => b.score - a.score);
}

function syncShowcaseOrderFromRanking() {
  const ranked = getRankedSelectedOffersForShowcase();
  const rankedIds = ranked.map(o => o.id);
  const current = state.showcaseOrder.filter(id => state.selectedOfferIds.has(id));
  const slots = current.map((id, i) => ({ id, i, pinned: state.pinnedOfferIds.has(id) }));
  const toPlace = rankedIds.filter(id => !state.pinnedOfferIds.has(id));
  const newOrder = [];
  let j = 0;
  for (const slot of slots) {
    if (slot.pinned) {
      newOrder.push(slot.id);
    } else {
      newOrder.push(j < toPlace.length ? toPlace[j++] : slot.id);
    }
  }
  const added = rankedIds.filter(id => !current.includes(id));
  state.showcaseOrder = [...newOrder, ...added];
}

function syncShowcaseOrderOnSelectionChange(addedId, removedId) {
  if (removedId != null) {
    state.showcaseOrder = state.showcaseOrder.filter(id => id !== removedId);
    state.pinnedOfferIds.delete(removedId);
  }
  if (addedId != null) {
    state.showcaseOrder.push(addedId);
  }
}

function getShowcaseOrderedOffers() {
  const order = state.showcaseOrder.filter(id => state.selectedOfferIds.has(id));
  const byId = new Map(OFFERS.map(o => [o.id, o]));
  return order.map(id => byId.get(id)).filter(Boolean);
}

function isMoveValidForShowcase(offerId, toIndex) {
  const list = state.showcaseOrder.filter(id => state.selectedOfferIds.has(id));
  const fromIndex = list.indexOf(offerId);
  if (fromIndex === -1 || toIndex === fromIndex || toIndex < 0 || toIndex >= list.length) return false;
  const newOrder = list.slice();
  newOrder.splice(fromIndex, 1);
  newOrder.splice(toIndex, 0, offerId);
  for (const pinnedId of state.pinnedOfferIds) {
    if (list.indexOf(pinnedId) !== newOrder.indexOf(pinnedId)) return false;
  }
  return true;
}

function moveOfferInShowcase(offerId, toIndex) {
  if (!isMoveValidForShowcase(offerId, toIndex)) return;
  const list = state.showcaseOrder.filter(id => state.selectedOfferIds.has(id));
  const fromIndex = list.indexOf(offerId);
  const arr = [...list];
  arr.splice(fromIndex, 1);
  arr.splice(toIndex, 0, offerId);
  state.showcaseOrder = state.showcaseOrder.filter(id => !state.selectedOfferIds.has(id));
  arr.forEach(id => state.showcaseOrder.push(id));
}

function togglePinned(offerId) {
  if (state.pinnedOfferIds.has(offerId)) {
    state.pinnedOfferIds.delete(offerId);
  } else {
    state.pinnedOfferIds.add(offerId);
  }
}

function setupDragHandle(dragBtn, offerId) {
  let lastIndex = -1;

  const onMove = (e) => {
    const y = e.touches ? e.touches[0].clientY : e.clientY;
    const grid = document.getElementById("landing-preview")?.querySelector(".landing-offers-grid");
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll(".offer-card[data-offer-id]"));
    if (!cards.length) return;
    let targetIndex = 0;
    for (let i = 0; i < cards.length; i++) {
      const r = cards[i].getBoundingClientRect();
      if (y >= r.top && y <= r.bottom) {
        targetIndex = i;
        break;
      }
      if (y < r.top) {
        targetIndex = i;
        break;
      }
      targetIndex = i + 1;
    }
    targetIndex = Math.min(targetIndex, cards.length - 1);
    if (targetIndex !== lastIndex && isMoveValidForShowcase(offerId, targetIndex)) {
      lastIndex = targetIndex;
      moveOfferInShowcase(offerId, targetIndex);
      renderPreview();
    }
  };

  const onEnd = () => {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onEnd);
    document.removeEventListener("touchmove", onMove, { passive: true });
    document.removeEventListener("touchend", onEnd);
  };

  const onStart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const orderedIds = state.showcaseOrder.filter(id => state.selectedOfferIds.has(id));
    lastIndex = orderedIds.indexOf(offerId);
    startY = e.touches ? e.touches[0].clientY : e.clientY;
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onEnd);
    document.addEventListener("touchmove", onMove, { passive: true });
    document.addEventListener("touchend", onEnd);
  };

  dragBtn.addEventListener("mousedown", onStart);
  dragBtn.addEventListener("touchstart", onStart, { passive: false });
}

function isTouchLike() {
  return window.matchMedia && window.matchMedia("(hover: none)").matches;
}

function toggleAccent(offerId) {
  if (state.accentedOfferIds.has(offerId)) {
    state.accentedOfferIds.delete(offerId);
  } else {
    state.accentedOfferIds.add(offerId);
  }
}

function startDeleteConfirmation(offerId) {
  state.pendingDeleteOfferIds.add(offerId);
  const endAt = Date.now() + 5000;
  pendingDelete.set(offerId, { endAt });
  ensurePendingDeleteTicker();
}

function restoreFromDeleteConfirmation(offerId) {
  state.pendingDeleteOfferIds.delete(offerId);
  pendingDelete.delete(offerId);
  cleanupPendingDeleteTickerIfNeeded();
}

function finalizeDelete(offerId) {
  state.pendingDeleteOfferIds.delete(offerId);
  pendingDelete.delete(offerId);
  state.accentedOfferIds.delete(offerId);
  state.selectedOfferIds.delete(offerId);
  state.showcaseOrder = state.showcaseOrder.filter(id => id !== offerId);
  state.pinnedOfferIds.delete(offerId);
}

function ensurePendingDeleteTicker() {
  if (pendingDeleteTicker) return;
  pendingDeleteTicker = setInterval(() => {
    const now = Date.now();
    let changed = false;

    for (const [offerId, info] of pendingDelete.entries()) {
      const remaining = info.endAt - now;
      const progress = Math.max(0, Math.min(1, 1 - remaining / 5000));

      const bar = document.querySelector(`.restore-progress[data-offer-id="${offerId}"]`);
      if (bar) bar.style.width = `${Math.round(progress * 100)}%`;

      if (remaining <= 0) {
        finalizeDelete(offerId);
        changed = true;
      }
    }

    if (changed) {
      renderOffersTable();
      renderPreview();
    }

    cleanupPendingDeleteTickerIfNeeded();
  }, 50);
}

function cleanupPendingDeleteTickerIfNeeded() {
  if (pendingDeleteTicker && pendingDelete.size === 0) {
    clearInterval(pendingDeleteTicker);
    pendingDeleteTicker = null;
  }
}

// Рендер таблицы офферов
function renderOffersTable() {
  const tbody = document.getElementById("offers-body");
  tbody.innerHTML = "";

  const filtered = getFilteredAndSortedOffers();
  const headerCheckbox = document.getElementById("offers-select-all");

  if (headerCheckbox) {
    if (!filtered.length) {
      headerCheckbox.checked = false;
    } else {
      headerCheckbox.checked = filtered.every(o => state.selectedOfferIds.has(o.id));
    }
  }

  if (!filtered.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 8;
    td.style.padding = "14px 10px";
    td.style.color = "var(--text-muted)";
    td.style.fontSize = "12px";
    td.textContent =
      state.offerIdQuery && state.offerIdQuery.length > 6
        ? "Таких офферов нет — измените параметры поиска"
        : "Нет офферов по заданным параметрам";
    tr.appendChild(td);
    tbody.appendChild(tr);
    updateTrafficBackSelect();
    return;
  }

  filtered.forEach(offer => {
    const tr = document.createElement("tr");

    const tdSelect = document.createElement("td");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = state.selectedOfferIds.has(offer.id);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        state.selectedOfferIds.add(offer.id);
        syncShowcaseOrderOnSelectionChange(offer.id, null);
      } else {
        state.selectedOfferIds.delete(offer.id);
        state.accentedOfferIds.delete(offer.id);
        restoreFromDeleteConfirmation(offer.id);
        syncShowcaseOrderOnSelectionChange(null, offer.id);
      }
      renderOffersTable();
      renderPreview();
    });
    tdSelect.appendChild(checkbox);

    const tdPublicId = document.createElement("td");
    tdPublicId.textContent = String(offer.publicId || "");

    const tdName = document.createElement("td");
    tdName.textContent = offer.name;

    const tdGeo = document.createElement("td");
    tdGeo.textContent = offer.geo;

    const tdSource = document.createElement("td");
    tdSource.textContent = offer.source;

    const tdEpc = document.createElement("td");
    tdEpc.textContent = offer.epc.toFixed(2);

    const tdCr = document.createElement("td");
    tdCr.textContent = offer.cr.toFixed(1);
    const tdScore = document.createElement("td");
    tdScore.textContent = offer.score.toString();

    tr.append(tdSelect, tdPublicId, tdName, tdGeo, tdSource, tdEpc, tdCr, tdScore);
    tbody.appendChild(tr);
  });

  updateTrafficBackSelect();
}

// Шаг "Аналитика"
function bindAnalyticsStep() {
  const trackingSelect = document.getElementById("tracking-link");
  const jsTextarea = document.getElementById("custom-js");
  const domainTypeInputs = document.querySelectorAll('input[name="domain-type"]');
  const systemSelect = document.getElementById("system-domain");
  const customInput = document.getElementById("custom-domain");
  const systemBlock = document.getElementById("domain-system-block");
  const customBlock = document.getElementById("domain-custom-block");

  trackingSelect.addEventListener("change", () => {
    state.trackingLink = trackingSelect.value;
  });

  jsTextarea.addEventListener("input", () => {
    state.customJs = jsTextarea.value;
  });

  domainTypeInputs.forEach(input => {
    input.addEventListener("change", () => {
      state.domainType = input.value;
      if (state.domainType === "system") {
        systemBlock.classList.remove("hidden");
        customBlock.classList.add("hidden");
      } else {
        systemBlock.classList.add("hidden");
        customBlock.classList.remove("hidden");
      }
    });
  });

  systemSelect.addEventListener("change", () => {
    state.systemDomain = systemSelect.value;
  });

  customInput.addEventListener("input", () => {
    state.customDomain = customInput.value;
  });
}

const PERMANENT_TAG_KEYS = ["sub1", "sub2", "sub3", "sub4", "sub5"];

function bindPermanentTags() {
  const addBtn = document.getElementById("permanent-tags-add");
  if (addBtn) {
    addBtn.addEventListener("click", () => {
      state.permanentTags.push({ key: PERMANENT_TAG_KEYS[0], value: "" });
      renderPermanentTagsRows();
    });
  }
}

function bindLegalInfo() {
  const el = document.getElementById("legal-info");
  if (!el) return;
  el.value = state.legalInfo;
  el.addEventListener("input", () => {
    state.legalInfo = el.value;
    renderPreview();
  });
}

function bindTrafficBack() {
  const input = document.getElementById("trafficback-url-input");
  const select = document.getElementById("trafficback-url-select");
  const radios = document.querySelectorAll('input[name="trafficback-mode"]');
  if (!input || !select || !radios.length) return;

  const urlWrap = input.closest(".trafficback-url-wrap");
  function setMode(mode) {
    state.trafficBackMode = mode;
    if (mode === "none") {
      if (urlWrap) urlWrap.classList.add("hidden");
    } else {
      if (urlWrap) urlWrap.classList.remove("hidden");
      if (mode === "custom") {
        input.classList.remove("hidden");
        input.removeAttribute("aria-hidden");
        select.classList.add("hidden");
        select.setAttribute("aria-hidden", "true");
      } else {
        input.classList.add("hidden");
        input.setAttribute("aria-hidden", "true");
        select.classList.remove("hidden");
        select.removeAttribute("aria-hidden");
        fillTrafficBackSelect();
      }
    }
  }

  function fillTrafficBackSelect() {
    const offers = getFilteredAndSortedOffers();
    const current = select.value;
    select.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Выберите оффер из списка";
    select.appendChild(placeholder);
    offers.forEach(o => {
      const opt = document.createElement("option");
      opt.value = String(o.id);
      opt.textContent = `${o.publicId || ""}, ${o.name}`;
      select.appendChild(opt);
    });
    if (offers.some(o => String(o.id) === current)) select.value = current;
    else state.trafficBackOfferId = "";
  }

  input.value = state.trafficBackCustomUrl || "";
  input.addEventListener("input", () => {
    state.trafficBackCustomUrl = input.value;
  });

  select.addEventListener("change", () => {
    state.trafficBackOfferId = select.value || "";
  });

  radios.forEach(r => {
    r.addEventListener("change", () => {
      setMode(r.value);
    });
  });

  setMode(state.trafficBackMode);
  if (state.trafficBackMode === "custom") {
    input.value = state.trafficBackCustomUrl || "";
  } else if (state.trafficBackMode === "offer") {
    fillTrafficBackSelect();
    select.value = state.trafficBackOfferId || "";
  }
}

function updateTrafficBackSelect() {
  if (state.trafficBackMode !== "offer") return;
  const select = document.getElementById("trafficback-url-select");
  if (!select || select.classList.contains("hidden")) return;
  const offers = getFilteredAndSortedOffers();
  const current = select.value;
  select.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Выберите оффер из списка";
  select.appendChild(placeholder);
  offers.forEach(o => {
    const opt = document.createElement("option");
    opt.value = String(o.id);
    opt.textContent = `${o.publicId || ""}, ${o.name}`;
    select.appendChild(opt);
  });
  if (offers.some(o => String(o.id) === current)) select.value = current;
  else state.trafficBackOfferId = "";
}

function bindLandingPoints() {
  const rows = document.getElementById("landing-points-rows");
  const addBtn = document.getElementById("landing-points-add");
  if (!rows || !addBtn) return;

  function syncAddDisabled() {
    addBtn.disabled = getLandingPoints().length >= 3;
    addBtn.classList.toggle("is-disabled", addBtn.disabled);
  }

  function reindexRows() {
    Array.from(rows.querySelectorAll(".offer-points-row")).forEach((rowEl, i) => {
      rowEl.dataset.index = String(i);
    });
  }

  function renderRows() {
    rows.innerHTML = "";
    getLandingPoints()
      .slice(0, 3)
      .forEach((p, idx) => {
        const row = document.createElement("div");
        row.className = "offer-points-row";
        row.dataset.index = String(idx);
        const input = document.createElement("input");
        input.type = "text";
        input.value = p;
        input.addEventListener("input", () => {
          const i = Number(row.dataset.index);
          const list = getLandingPoints().slice();
          list[i] = input.value;
          state.landingPoints = list;
          renderPreview();
        });
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "offer-points-remove";
        removeBtn.setAttribute("aria-label", "Удалить пойнт");
        removeBtn.innerHTML =
          '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 3h6l1 2h5v2H3V5h5l1-2Zm1 7h2v9h-2v-9Zm4 0h2v9h-2v-9ZM6 10h2v9H6v-9Z" fill="currentColor"/></svg>';
        removeBtn.addEventListener("click", () => {
          const i = Number(row.dataset.index);
          const list = getLandingPoints().slice();
          list.splice(i, 1);
          state.landingPoints = list;
          row.remove();
          reindexRows();
          syncAddDisabled();
          renderPreview();
        });
        row.append(input, removeBtn);
        rows.appendChild(row);
      });
    syncAddDisabled();
  }

  addBtn.addEventListener("click", () => {
    const list = getLandingPoints().slice();
    if (list.length >= 3) return;
    list.push(DEFAULT_OFFER_POINT);
    state.landingPoints = list;
    renderRows();
    renderPreview();
  });

  renderRows();
}

function renderPermanentTagsRows() {
  const container = document.getElementById("permanent-tags-rows");
  if (!container) return;

  container.innerHTML = "";
  state.permanentTags.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "permanent-tags-row";

    const keySelect = document.createElement("select");
    keySelect.className = "permanent-tags-key-select";
    PERMANENT_TAG_KEYS.forEach(k => {
      const opt = document.createElement("option");
      opt.value = k;
      opt.textContent = k;
      if (item.key === k) opt.selected = true;
      keySelect.appendChild(opt);
    });
    if (!PERMANENT_TAG_KEYS.includes(item.key)) {
      keySelect.value = PERMANENT_TAG_KEYS[0];
      state.permanentTags[index].key = PERMANENT_TAG_KEYS[0];
    }
    keySelect.addEventListener("change", () => {
      state.permanentTags[index].key = keySelect.value;
    });

    const eq = document.createElement("span");
    eq.className = "permanent-tags-eq";
    eq.textContent = "=";

    const valueWrap = document.createElement("div");
    valueWrap.className = "permanent-tags-value-wrap";
    const valueInput = document.createElement("input");
    valueInput.type = "text";
    valueInput.placeholder = "Название метки";
    valueInput.value = item.value;
    valueInput.addEventListener("input", () => {
      state.permanentTags[index].value = valueInput.value;
    });

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "permanent-tags-remove";
    removeBtn.setAttribute("aria-label", "Удалить");
    removeBtn.textContent = "×";
    removeBtn.addEventListener("click", () => {
      state.permanentTags.splice(index, 1);
      renderPermanentTagsRows();
    });

    valueWrap.append(valueInput, removeBtn);
    row.append(keySelect, eq, valueWrap);
    container.appendChild(row);
  });
}

// Синхронизация полей шага "Дизайн" с состоянием
function syncDesignInputsFromState() {
  const titleInput = document.getElementById("landing-title");
  const descInput = document.getElementById("landing-description");
  const descCounter = document.getElementById("landing-description-counter");
  const twoColCheckbox = document.getElementById("offers-two-col-desktop");

  if (titleInput) titleInput.value = state.title;
  if (descInput) descInput.value = (state.description || "").slice(0, DESCRIPTION_MAX);
  if (twoColCheckbox) twoColCheckbox.checked = !!state.offersTwoColDesktop;
  if (descInput) updateDescriptionCounter(descInput, descCounter);
}

function updateDescriptionCounter(descInput, counterEl) {
  if (!counterEl || !descInput) return;
  const len = descInput.value.length;
  counterEl.textContent = `${len}/${DESCRIPTION_MAX}`;
  counterEl.classList.toggle("is-limit", len >= DESCRIPTION_MAX);
}

// Debounce-помощник для inline-редактирования
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function attachEditable(el, field) {
  el.contentEditable = "true";
  el.classList.add("landing-editable");

  const save = () => {
    const raw = el.textContent ?? "";
    const value = raw.trim();
    if (field === "title") {
      state.title = value || "Без названия";
    } else if (field === "description") {
      const clipped = raw.slice(0, DESCRIPTION_MAX);
      if (raw.length !== clipped.length) el.textContent = clipped;
      state.description = clipped.trim();
    } else if (field === "ctaText") {
      state.ctaText = value || "Перейти к офферам";
    }
    syncDesignInputsFromState();
  };

  const debouncedSave = debounce(save, 1000);

  el.addEventListener("input", debouncedSave);
  el.addEventListener("blur", save);

  // Разрешаем пробел внутри кнопки (по умолчанию Space нажимает кнопку)
  if (field === "ctaText") {
    el.addEventListener("keydown", event => {
      if (event.key === " ") {
        event.preventDefault();
        // Вставляем пробел в текущую позицию курсора
        document.execCommand("insertText", false, " ");
      }
    });
  }
}

// Рендер превью лендинга
function renderPreview() {
  const preview = document.getElementById("landing-preview");
  preview.classList.remove("landing-variant1", "landing-variant2", "landing-variant3", "landing-variant4");
  preview.classList.add("landing-" + state.designVariant);

  preview.classList.remove("preview-mobile", "preview-desktop", "offers-two-col-desktop");
  preview.classList.add(state.previewMode === "desktop" ? "preview-desktop" : "preview-mobile");
  if (state.previewMode === "desktop" && state.offersTwoColDesktop) {
    preview.classList.add("offers-two-col-desktop");
  }

  const selectedOffers = getShowcaseOrderedOffers();

  preview.innerHTML = "";

  const header = document.createElement("div");
  header.className = "landing-header";
  if (state.designVariant === "variant4") {
    header.classList.add("landing-header-hero");
    const textWrap = document.createElement("div");
    textWrap.className = "landing-header-hero-text";
    const titleEl = document.createElement("div");
    titleEl.className = "landing-header-title";
    titleEl.textContent = state.title || "Без названия";
    const subtitleEl = document.createElement("div");
    subtitleEl.className = "landing-header-subtitle";
    subtitleEl.textContent =
      state.description || "Добавьте описание лендинга на шаге «Дизайн»";
    attachEditable(titleEl, "title");
    attachEditable(subtitleEl, "description");
    textWrap.append(titleEl, subtitleEl);
    const points = getLandingPoints().slice(0, 3);
    if (points.length) {
      const ul = document.createElement("ul");
      ul.className = "landing-points";
      points.forEach(p => {
        const li = document.createElement("li");
        li.textContent = p;
        ul.appendChild(li);
      });
      textWrap.appendChild(ul);
    }
    const imgWrap = document.createElement("div");
    imgWrap.className = "landing-header-hero-img";
    imgWrap.setAttribute("aria-hidden", "true");
    header.append(textWrap, imgWrap);
  } else {
    const titleEl = document.createElement("div");
    titleEl.className = "landing-header-title";
    titleEl.textContent = state.title || "Без названия";
    const subtitleEl = document.createElement("div");
    subtitleEl.className = "landing-header-subtitle";
    subtitleEl.textContent =
      state.description || "Добавьте описание лендинга на шаге «Дизайн»";
    attachEditable(titleEl, "title");
    attachEditable(subtitleEl, "description");
    header.appendChild(titleEl);
    header.appendChild(subtitleEl);
    const points = getLandingPoints().slice(0, 3);
    if (points.length) {
      const ul = document.createElement("ul");
      ul.className = "landing-points";
      points.forEach(p => {
        const li = document.createElement("li");
        li.textContent = p;
        ul.appendChild(li);
      });
      header.appendChild(ul);
    }
  }

  preview.appendChild(header);

  if (selectedOffers.length) {
    const grid = document.createElement("div");
    grid.className = "landing-offers-grid";

    selectedOffers.forEach(o => {
      const card = document.createElement("div");
      card.className = "offer-card";
      card.dataset.offerId = o.id.toString();

      const isPending = state.pendingDeleteOfferIds.has(o.id);
      if (isPending) card.classList.add("is-pending-delete", "is-dim");
      if (state.accentedOfferIds.has(o.id)) card.classList.add("is-accent");

      const content = document.createElement("div");
      content.className = "offer-card-content";

      const logo = document.createElement("div");
      logo.className = "offer-card-logo";
      logo.style.background = getOfferLogoStyle(o.id);
      const logoIcon = document.createElement("span");
      logoIcon.className = "offer-card-logo-icon";
      logoIcon.textContent = o.name.charAt(0).toUpperCase();
      logo.appendChild(logoIcon);

      const textBlock = document.createElement("div");
      textBlock.className = "offer-card-text";

      const name = document.createElement("div");
      name.className = "offer-card-title";
      name.textContent = getOfferDisplayName(o);

      const desc = getOfferDisplayDescription(o);
      textBlock.appendChild(name);
      if (desc) {
        const meta = document.createElement("div");
        meta.className = "offer-card-meta";
        meta.textContent = desc;
        textBlock.appendChild(meta);
      }

      const points = getOfferPoints(o).slice(0, 3);
      if (points.length) {
        const ul = document.createElement("ul");
        ul.className = "offer-card-points";
        points.forEach(p => {
          const li = document.createElement("li");
          li.textContent = p;
          ul.appendChild(li);
        });
        textBlock.appendChild(ul);
      }

      const ctaBtn = document.createElement("button");
      ctaBtn.type = "button";
      ctaBtn.className = "offer-card-cta";
      ctaBtn.textContent = getOfferCtaText(o);

      content.append(logo, textBlock, ctaBtn);

      const actions = document.createElement("div");
      actions.className = "offer-actions";

      if (isPending) {
        const restoreBtn = document.createElement("button");
        restoreBtn.type = "button";
        restoreBtn.className = "offer-action-btn";
        const restoreFill = document.createElement("span");
        restoreFill.className = "restore-progress";
        restoreFill.dataset.offerId = o.id.toString();

        const restoreText = document.createElement("span");
        restoreText.className = "restore-text";
        restoreText.textContent = "Восстановить";

        const info = pendingDelete.get(o.id);
        if (info) {
          const remaining = info.endAt - Date.now();
          const progressValue = Math.max(0, Math.min(1, 1 - remaining / 5000));
          restoreFill.style.width = `${Math.round(progressValue * 100)}%`;
        }

        restoreBtn.append(restoreFill, restoreText);
        restoreBtn.addEventListener("click", e => {
          e.stopPropagation();
          restoreFromDeleteConfirmation(o.id);
          renderPreview();
        });
        actions.append(restoreBtn);
      } else {
        const isPinned = state.pinnedOfferIds.has(o.id);

        if (!isPinned) {
          const dragBtn = document.createElement("button");
          dragBtn.type = "button";
          dragBtn.className = "offer-action-btn offer-action-drag";
          dragBtn.setAttribute("aria-label", "Перетащить");
          dragBtn.innerHTML = '<span class="icon-burger"></span>';
          setupDragHandle(dragBtn, o.id);
          actions.appendChild(dragBtn);
        }

        const accentBtn = document.createElement("button");
        accentBtn.type = "button";
        accentBtn.className = "offer-action-btn";
        accentBtn.textContent = state.accentedOfferIds.has(o.id) ? "Снять акцент" : "Акцент";
        accentBtn.addEventListener("click", e => {
          e.stopPropagation();
          toggleAccent(o.id);
          renderPreview();
        });

        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "offer-action-btn";
        delBtn.textContent = "Удалить";
        delBtn.addEventListener("click", e => {
          e.stopPropagation();
          startDeleteConfirmation(o.id);
          renderPreview();
        });

        const lockBtn = document.createElement("button");
        lockBtn.type = "button";
        lockBtn.className = "offer-action-btn offer-action-lock" + (isPinned ? " is-pinned" : "");
        lockBtn.setAttribute("aria-label", isPinned ? "Открепить" : "Закрепить");
        lockBtn.innerHTML = '<span class="icon-lock"></span>';
        lockBtn.addEventListener("click", e => {
          e.stopPropagation();
          togglePinned(o.id);
          renderPreview();
        });

        actions.append(accentBtn, delBtn, lockBtn);

        if (isTouchLike()) {
          card.addEventListener("click", () => {
            card.classList.toggle("show-actions");
          });
        }
      }

      card.append(content, actions);
      grid.appendChild(card);
    });

    preview.appendChild(grid);
  } else {
    const empty = document.createElement("div");
    empty.style.marginTop = "8px";
    empty.style.fontSize = "12px";
    empty.style.color = "var(--text-muted)";
    empty.textContent = "Нет выбранных офферов — отметьте нужные на шаге «Контент».";
    preview.appendChild(empty);
  }

  const footer = document.createElement("div");
  footer.className = "landing-footer";
  footer.textContent = state.legalInfo || "";
  preview.appendChild(footer);

  renderOfferDesignBlock();
}

function renderOfferDesignBlock() {
  const container = document.getElementById("offer-design-container");
  if (!container) return;
  const offers = getShowcaseOrderedOffers();
  const newIds = offers.map(o => o.id);
  const currentIds = Array.from(container.querySelectorAll(".offer-design-subblock"))
    .map(el => el.dataset.offerId)
    .filter(Boolean)
    .map(Number);
  if (currentIds.length === newIds.length && currentIds.every((id, i) => id === newIds[i])) return;
  container.innerHTML = "";
  offers.forEach((offer, index) => {
    const sub = document.createElement("div");
    sub.className = "offer-design-subblock";
    sub.dataset.offerId = String(offer.id);
    const title = document.createElement("h3");
    title.textContent = `Оффер ${index + 1}`;
    sub.appendChild(title);
    const formGroup = document.createElement("div");
    formGroup.className = "form-group";
    const label = document.createElement("label");
    label.textContent = "Название оффера";
    label.setAttribute("for", `offer-name-${offer.id}`);
    const input = document.createElement("input");
    input.type = "text";
    input.id = `offer-name-${offer.id}`;
    input.placeholder = "Название оффера";
    input.value = getOfferDisplayName(offer);
    input.addEventListener("input", () => {
      state.offerDisplayNames[offer.id] = input.value.trim() || undefined;
      renderPreview();
    });
    formGroup.append(label, input);
    sub.appendChild(formGroup);

    const descGroup = document.createElement("div");
    descGroup.className = "form-group";
    const descLabel = document.createElement("label");
    descLabel.textContent = "Описание оффера";
    descLabel.setAttribute("for", `offer-desc-${offer.id}`);

    const descWrap = document.createElement("div");
    descWrap.className = "textarea-wrap";
    const textarea = document.createElement("textarea");
    textarea.id = `offer-desc-${offer.id}`;
    textarea.rows = 3;
    textarea.maxLength = DESCRIPTION_MAX;
    textarea.placeholder = DEFAULT_OFFER_DESCRIPTION;
    textarea.value = getOfferDisplayDescription(offer);
    const counter = document.createElement("div");
    counter.className = "char-counter";
    counter.textContent = `${textarea.value.length}/${DESCRIPTION_MAX}`;
    textarea.addEventListener("input", () => {
      state.offerDisplayDescriptions[offer.id] = textarea.value;
      counter.textContent = `${textarea.value.length}/${DESCRIPTION_MAX}`;
      renderPreview();
    });
    descWrap.append(textarea, counter);
    descGroup.append(descLabel, descWrap);
    sub.appendChild(descGroup);

    const ctaGroup = document.createElement("div");
    ctaGroup.className = "form-group";
    const ctaLabel = document.createElement("label");
    ctaLabel.textContent = "Текст кнопки (CTA)";
    ctaLabel.setAttribute("for", `offer-cta-${offer.id}`);
    const ctaInput = document.createElement("input");
    ctaInput.type = "text";
    ctaInput.id = `offer-cta-${offer.id}`;
    ctaInput.placeholder = state.ctaText || "Подать заявку";
    ctaInput.value = getOfferCtaText(offer);
    ctaInput.addEventListener("input", () => {
      state.offerCtaTexts[offer.id] = ctaInput.value.trim() || undefined;
      renderPreview();
    });
    ctaGroup.append(ctaLabel, ctaInput);
    sub.appendChild(ctaGroup);

    const pointsCard = document.createElement("div");
    pointsCard.className = "offer-points-card";
    const pointsTitle = document.createElement("div");
    pointsTitle.className = "offer-points-title";
    pointsTitle.textContent = "Пойнты";
    const pointsDesc = document.createElement("p");
    pointsDesc.className = "offer-points-desc";
    pointsDesc.textContent = "Добавьте краткие УТП для оффера, чтобы показать клиенту основные преимущества";
    const rows = document.createElement("div");
    rows.className = "offer-points-rows";
    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.className = "offer-points-add-btn";
    addBtn.textContent = "+ Добавить пойнт";

    function syncAddDisabled() {
      const count = getOfferPoints(offer).length;
      addBtn.disabled = count >= 3;
      addBtn.classList.toggle("is-disabled", addBtn.disabled);
    }

    function reindexRows() {
      Array.from(rows.querySelectorAll(".offer-points-row")).forEach((rowEl, i) => {
        rowEl.dataset.index = String(i);
      });
    }

    function removeAt(idx) {
      const list = getOfferPoints(offer).slice();
      list.splice(idx, 1);
      state.offerPoints[offer.id] = list;
      const rowEl = rows.querySelector(`.offer-points-row[data-index="${idx}"]`);
      if (rowEl) rowEl.remove();
      reindexRows();
      syncAddDisabled();
      renderPreview();
    }

    function addRow(initialText) {
      const idx = rows.querySelectorAll(".offer-points-row").length;
      const row = document.createElement("div");
      row.className = "offer-points-row";
      row.dataset.index = String(idx);
      const input = document.createElement("input");
      input.type = "text";
      input.value = initialText;
      input.addEventListener("input", () => {
        const i = Number(row.dataset.index);
        const list = getOfferPoints(offer).slice();
        list[i] = input.value;
        state.offerPoints[offer.id] = list;
        renderPreview();
      });
      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "offer-points-remove";
      removeBtn.setAttribute("aria-label", "Удалить пойнт");
      removeBtn.innerHTML =
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 3h6l1 2h5v2H3V5h5l1-2Zm1 7h2v9h-2v-9Zm4 0h2v9h-2v-9ZM6 10h2v9H6v-9Z" fill="currentColor"/></svg>';
      removeBtn.addEventListener("click", () => {
        removeAt(Number(row.dataset.index));
      });
      row.append(input, removeBtn);
      rows.appendChild(row);
    }

    const initialPoints = getOfferPoints(offer).slice(0, 3);
    initialPoints.forEach(p => addRow(p));
    syncAddDisabled();
    addBtn.addEventListener("click", () => {
      const current = getOfferPoints(offer).slice();
      if (current.length >= 3) return;
      current.push(DEFAULT_OFFER_POINT);
      state.offerPoints[offer.id] = current;
      addRow(DEFAULT_OFFER_POINT);
      syncAddDisabled();
      renderPreview();
    });

    pointsCard.append(pointsTitle, pointsDesc, rows, addBtn);
    sub.appendChild(pointsCard);

    container.appendChild(sub);
  });
}

