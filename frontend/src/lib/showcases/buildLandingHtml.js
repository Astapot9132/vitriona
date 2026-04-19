import { getOfferDisplayName, getOfferDisplayDescription, getOfferCtaText, getOfferPoints, getOfferLogoStyle, getOrderedSelectedOffers } from './constructorDefaults';

function esc(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export default function buildLandingHtml(config, offers) {
    const selectedOffers = getOrderedSelectedOffers(offers, config);
    const designVariant = config.designVariant || 'variant1';
    const variantNum = designVariant.slice(-1);
    const title = esc(config.title || '');
    const description = esc(config.description || '');
    const legalInfo = esc(config.legalInfo || '').replace(/\n/g, '<br>');
    const landingPoints = (config.landingPoints || []).slice(0, 3);
    const twoCol = config.offersTwoColDesktop;
    const accentedIds = config.accentedOfferIds || [];

    const bodyClasses = [];
    if (designVariant === 'variant1') bodyClasses.push('result-variant1');
    else if (designVariant === 'variant2') bodyClasses.push('result-variant2');
    else if (designVariant === 'variant4') bodyClasses.push('result-variant4');
    if (twoCol) bodyClasses.push('result-offers-two-col-desktop');

    const landingPointsHtml = landingPoints
        .map(p => `<li>${esc(p)}</li>`)
        .join('');

    const offersHtml = selectedOffers
        .map((o, idx) => {
            const displayName = getOfferDisplayName(o, config);
            const desc = getOfferDisplayDescription(o, config);
            const ctaText = getOfferCtaText(o, config);
            const points = getOfferPoints(o, config).slice(0, 3);
            const isAccented = accentedIds.includes(o.id);
            const gradient = getOfferLogoStyle(idx);
            const letter = (displayName || 'O').charAt(0).toUpperCase();
            const pointsHtml = points.map(p => `<li>${esc(p)}</li>`).join('');

            return `
            <div class="offer-card${isAccented ? ' is-accent' : ''}">
                <div class="offer-card-logo" style="background:${gradient}"><span class="offer-card-logo-icon">${letter}</span></div>
                <div class="offer-card-text">
                    <div class="offer-card-title">${esc(displayName)}</div>
                    ${desc ? `<div class="offer-card-meta">${esc(desc)}</div>` : ''}
                    ${pointsHtml ? `<ul class="offer-card-points">${pointsHtml}</ul>` : ''}
                </div>
                <button type="button" class="offer-card-cta">${esc(ctaText)}</button>
            </div>`;
        })
        .join('');

    const headerContent = designVariant === 'variant4'
        ? `<div class="landing-header-hero-text"><div class="landing-header-title">${title || 'Без названия'}</div><div class="landing-header-subtitle">${description || 'Описание лендинга не задано.'}</div>${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ''}</div><div class="landing-header-hero-img" aria-hidden="true"></div>`
        : `<div class="landing-header-title">${title || 'Без названия'}</div><div class="landing-header-subtitle">${description || 'Описание лендинга не задано.'}</div>${landingPointsHtml ? `<ul class="landing-points">${landingPointsHtml}</ul>` : ''}`;

    return `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <title>${title || 'Лендинг'}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body { margin: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #020617; color: #e5e7eb; }
        body.result-variant1 { background: #eff6ff; color: #111827; }
        body.result-variant2 { background: #ecfdf5; color: #111827; }
        body.result-variant4 { background: #f3f4f6; color: #111827; }
        html, body { overflow-x: hidden; word-break: break-word; overflow-wrap: break-word; }
        .page-wrap { min-height: 100vh; padding: 24px 16px 32px; display: flex; justify-content: stretch; max-width: 100%; min-width: 0; }
        .landing-shell { width: 100%; max-width: 100%; min-width: 0; border-radius: 20px; background: radial-gradient(circle at top, #0b1120, #020617 55%, #020617 100%); padding: 24px 20px 20px; border: none; }
        .landing-header { display: flex; flex-direction: column; gap: 8px; }
        .landing-header-title { font-size: 24px; font-weight: 700; }
        .landing-header-subtitle { font-size: 14px; color: #9ca3af; }
        .landing-offers-grid { margin-top: 10px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; }
        .offer-card { border-radius: 12px; border: 1px solid #1f2937; background: rgba(15, 23, 42, 0.9); padding: 10px 12px; font-size: 13px; display: flex; flex-direction: row; align-items: center; gap: 10px; }
        .offer-card-logo { width: 44px; height: 44px; flex-shrink: 0; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
        .offer-card-logo-icon { color: #fff; font-size: 18px; font-weight: 700; }
        .offer-card-text { flex: 1; min-width: 0; }
        .offer-card .offer-card-title { margin-bottom: 2px; }
        .offer-card .offer-card-meta { font-size: 12px; color: #9ca3af; }
        .offer-card-title { font-weight: 600; margin-bottom: 4px; }
        .offer-card-meta { font-size: 12px; color: #9ca3af; }
        .offer-card-points { margin: 12px 0 0; padding-left: 26px; color: #111827; font-size: 16px; line-height: 1.35; }
        .offer-card-points li { margin: 0 0 4px; }
        .offer-card-points li::marker { color: #111827; }
        .offer-card-cta { margin-left: auto; display: block; padding: 8px 14px; font-size: 13px; border-radius: 999px; border: none; background: #2563eb; color: #ffffff; cursor: default; }
        .landing-points { margin: 6px 0 0; padding-left: 26px; color: #111827; font-size: inherit; line-height: 1.35; }
        .landing-points li { margin: 0 0 4px; }
        .landing-points li::marker { color: #f97316; }
        .landing-footer { margin-top: 18px; padding-top: 12px; border-top: 1px solid #1f2937; font-size: 11px; color: #9ca3af; line-height: 1.4; }
        .landing-variant3 .offer-card.is-accent { border-color: #91d217; background: linear-gradient(to right, #1f6915 0%, #020617 70%); }
        .landing-variant3 .offer-card-points, .landing-variant3 .offer-card-points li::marker { color: #ffffff; }
        .landing-variant3 .landing-points { color: #ffffff; }
        .landing-shell.landing-variant1 { background: linear-gradient(to bottom, #eff6ff, #ffffff 26%); color: #111827; }
        .landing-shell.landing-variant1 .landing-header-title { color: #111827; font-size: 54px; }
        .landing-shell.landing-variant1 .landing-header-subtitle { color: #6b7280; font-size: 24px; }
        .landing-shell.landing-variant1 .landing-header { gap: 16px; }
        .landing-shell.landing-variant1 .offer-card { background: #ffffff; border: 1px solid #e5e7eb; }
        .landing-shell.landing-variant1 .offer-card.is-accent { background: #ede9fe; border-color: #c4b5fd; }
        .landing-shell.landing-variant1 .offer-card-title { color: #111827; font-size: 22px; margin-bottom: 12px; }
        .landing-shell.landing-variant1 .offer-card-meta { color: #6b7280; font-size: 14px; }
        .landing-shell.landing-variant1 .landing-footer { color: #6b7280; border-top-color: #e5e7eb; }
        .landing-shell.landing-variant2 { background: linear-gradient(to right, #ecfdf5, #ffffff 35%); color: #111827; }
        .landing-shell.landing-variant2 .landing-header-title { color: #111827; font-size: 54px; }
        .landing-shell.landing-variant2 .landing-header-subtitle { color: #6b7280; font-size: 24px; }
        .landing-shell.landing-variant2 .landing-header { gap: 16px; }
        .landing-shell.landing-variant2 .offer-card { background: #ffffff; border: 1px solid #e5e7eb; }
        .landing-shell.landing-variant2 .offer-card.is-accent { background: #fef9c3; border-color: #fde68a; }
        .landing-shell.landing-variant2 .offer-card-title { color: #111827; font-size: 22px; margin-bottom: 12px; }
        .landing-shell.landing-variant2 .offer-card-meta { color: #6b7280; font-size: 14px; }
        .landing-shell.landing-variant2 .landing-footer { color: #6b7280; border-top-color: #e5e7eb; }
        .landing-shell.landing-variant3 .landing-header-title { font-size: 54px; }
        .landing-shell.landing-variant3 .landing-header-subtitle { font-size: 24px; }
        .landing-shell.landing-variant3 .landing-header { gap: 16px; }
        .landing-shell.landing-variant3 .offer-card-title { font-size: 22px; margin-bottom: 12px; }
        .landing-shell.landing-variant3 .offer-card-meta { font-size: 14px; }
        .landing-shell.landing-variant1 > section, .landing-shell.landing-variant2 > section, .landing-shell.landing-variant3 > section { margin-top: 60px; }
        .landing-shell.landing-variant1 .landing-points, .landing-shell.landing-variant2 .landing-points, .landing-shell.landing-variant3 .landing-points { margin-top: 12px; font-size: 20px; }
        .landing-shell.landing-variant1 .landing-points li, .landing-shell.landing-variant2 .landing-points li, .landing-shell.landing-variant3 .landing-points li { margin-bottom: 8px; }
        .landing-variant1 .landing-points li::marker, .landing-variant2 .landing-points li::marker, .landing-variant3 .landing-points li::marker { color: #2563eb; }
        .landing-shell.landing-variant4 { background: #f3f4f6; color: #111827; }
        .landing-shell.landing-variant4 .landing-header { flex-direction: row; align-items: flex-start; justify-content: space-between; gap: 20px; padding: 20px 24px 24px; background: #fff; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .landing-shell.landing-variant4 .landing-header-hero-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
        .landing-shell.landing-variant4 .landing-points { margin-top: 16px; padding-left: 34px; font-size: 18px; line-height: 1.45; }
        .landing-shell.landing-variant4 .landing-points li { margin: 0 0 14px; }
        @media (max-width: 640px) {
            .landing-shell.landing-variant4 .landing-header { flex-direction: column; align-items: stretch; min-width: 0; }
            .landing-shell.landing-variant4 .landing-header-hero-text { min-width: 0; }
            .landing-shell.landing-variant4 .landing-header-hero-img { width: 100%; max-width: 100%; height: 340px; min-height: 200px; align-self: stretch; flex-shrink: 0; border-radius: 14px; background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%); display: flex; align-items: center; justify-content: center; }
            .landing-shell.landing-variant4 .landing-header-hero-text .landing-header-title { font-size: 22px; }
            .landing-shell.landing-variant4 .landing-header-hero-text .landing-header-subtitle { font-size: 16px; }
            .landing-shell.landing-variant4 .offer-card { padding: 16px 18px; flex-direction: column; align-items: stretch; gap: 12px; background: #fff; border: none; border-radius: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
            .landing-shell.landing-variant4 .offer-card.is-accent { border: 1px solid #07810c; background: linear-gradient(to right, #76f370 0%, #ffffff 65%); }
            .landing-shell.landing-variant4 .offer-card-logo { width: 100%; height: 100px; margin-right: 0; margin-bottom: 4px; }
            .landing-shell.landing-variant4 .offer-card-logo-icon { font-size: 40px; }
            .landing-shell.landing-variant4 .offer-card-text { margin-right: 0; min-width: 0; }
            .landing-shell.landing-variant4 .offer-card-cta { margin-left: 0; align-self: flex-start; padding: 8px 14px; font-size: 14px; }
            .landing-shell.landing-variant4 .offer-card-title { font-size: 16px; }
            .landing-shell.landing-variant4 .offer-card-meta { font-size: 13px; }
            .landing-shell.landing-variant4 .landing-footer { font-size: 10px; }
        }
        @media (min-width: 641px) {
            .landing-shell.landing-variant4 .landing-header-title { font-size: 30px; color: #111827; }
            .landing-shell.landing-variant4 .landing-header-subtitle { color: #6b7280; font-size: 20px; }
            .landing-shell.landing-variant4 .landing-header-hero-img { width: 560px; height: 290px; border-radius: 18px; background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%); flex-shrink: 0; }
            .landing-shell.landing-variant4 .offer-card { background: #fff; border: none; border-radius: 14px; padding: 28px 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); width: 100%; min-height: 171px; }
            .landing-shell.landing-variant4 .offer-card-cta { background: #f97316; padding: 9px 18px; font-size: 18px; align-self: center; }
            .landing-shell.landing-variant4 .offer-card-logo { width: 260px; height: 170px; border-radius: 18px; margin-right: 18px; }
            .landing-shell.landing-variant4 .offer-card-logo-icon { font-size: 54px; }
            .landing-shell.landing-variant4 .offer-card-title { font-size: 24px; line-height: 1.2; }
            .landing-shell.landing-variant4 .offer-card-meta { font-size: 16px; line-height: 1.35; white-space: normal; }
            .landing-shell.landing-variant4 .offer-card-text { flex: 1; min-width: 0; margin-right: 22px; }
            .landing-shell.landing-variant4 .offer-card-cta { margin-left: auto; }
            .landing-shell.landing-variant4 .offer-card.is-accent { border: 1px solid #07810c; background: linear-gradient(to right, #76f370 0%, #ffffff 65%); }
            .landing-shell.landing-variant4 .landing-footer { border-top-color: #e5e7eb; color: #6b7280; font-size: 20px; }
        }
        @media (min-width: 641px) {
            body.result-offers-two-col-desktop .landing-offers-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
            body.result-offers-two-col-desktop .landing-shell.landing-variant4 .offer-card-logo { width: 160px; height: 140px; }
            .landing-shell.landing-variant1 .offer-card-logo, .landing-shell.landing-variant2 .offer-card-logo, .landing-shell.landing-variant3 .offer-card-logo { width: 94px; height: 64px; }
            .landing-shell.landing-variant1 .offer-card, .landing-shell.landing-variant2 .offer-card, .landing-shell.landing-variant3 .offer-card { gap: 30px; }
            .landing-shell.landing-variant1 .landing-footer, .landing-shell.landing-variant2 .landing-footer, .landing-shell.landing-variant3 .landing-footer { font-size: 14px; }
            .landing-shell.landing-variant1 > section, .landing-shell.landing-variant2 > section, .landing-shell.landing-variant3 > section { margin-top: 40px; }
        }
        @media (max-width: 640px) {
            .page-wrap { padding: 12px 10px 20px; }
            .landing-shell { border-radius: 0; max-width: 100%; min-width: 0; padding: 16px 12px 20px; border-left: none; border-right: none; }
            .landing-shell.landing-variant4 .landing-header { padding-left: 16px; padding-right: 16px; }
            .landing-header-title { font-size: 20px; }
            .landing-shell .landing-footer { font-size: 10px; }
            .landing-shell.landing-variant1 .landing-header-title, .landing-shell.landing-variant2 .landing-header-title, .landing-shell.landing-variant3 .landing-header-title { font-size: 34px; }
            .landing-shell.landing-variant1 .landing-header-subtitle, .landing-shell.landing-variant2 .landing-header-subtitle, .landing-shell.landing-variant3 .landing-header-subtitle { font-size: 20px; }
            .landing-shell.landing-variant1 .landing-footer, .landing-shell.landing-variant2 .landing-footer, .landing-shell.landing-variant3 .landing-footer { font-size: 12px; }
            .landing-shell.landing-variant1 .offer-card, .landing-shell.landing-variant2 .offer-card, .landing-shell.landing-variant3 .offer-card { flex-direction: column; align-items: stretch; gap: 12px; }
            .landing-shell.landing-variant1 .offer-card-logo, .landing-shell.landing-variant2 .offer-card-logo, .landing-shell.landing-variant3 .offer-card-logo { width: 100%; }
            .landing-shell.landing-variant1 .offer-card-cta, .landing-shell.landing-variant2 .offer-card-cta, .landing-shell.landing-variant3 .offer-card-cta { margin-left: 0; align-self: flex-start; }
            .landing-shell.landing-variant1 .offer-card-title, .landing-shell.landing-variant2 .offer-card-title, .landing-shell.landing-variant3 .offer-card-title { font-size: 16px; }
            .landing-shell.landing-variant1 .offer-card-points, .landing-shell.landing-variant2 .offer-card-points, .landing-shell.landing-variant3 .offer-card-points { font-size: 14px; }
        }
    </style>
</head>
<body class="${bodyClasses.join(' ')}">
    <div class="page-wrap">
        <main class="landing-shell landing-variant${variantNum}">
            <header class="landing-header${designVariant === 'variant4' ? ' landing-header-hero' : ''}">
                ${headerContent}
            </header>
            <section>
                <div class="landing-offers-grid">
                    ${offersHtml}
                </div>
            </section>
            <div class="landing-footer">${legalInfo}</div>
        </main>
    </div>
</body>
</html>`;
}
