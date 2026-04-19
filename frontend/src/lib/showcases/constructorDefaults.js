export const DEFAULT_OFFER_DESCRIPTION = 'Оформите займ с одобрением за 5 минут';
export const DEFAULT_OFFER_POINT = 'Ставка от 0%';

export const DEFAULT_CONFIG = {
    title: 'Займы онлайн со ставкой от 0%',
    description: 'Подобрали предложения с одобрением заявки за 15 минут!',
    designVariant: 'variant1',
    ctaText: 'Оформить',
    offersTwoColDesktop: true,
    landingPoints: [],
    selectedOfferIds: [],
    accentedOfferIds: [],
    showcaseOrder: [],
    rankingMode: 'auto',
    sortMetric: 'none',
    legalInfo: 'Компания не является банком и не принимает решения о займах. Мы используем файлы cookie для того, чтобы предоставить пользователям больше возможностей при посещении сайта. Оставаясь на сайте, Вы соглашаетесь на обработку файлов cookie.',
    trackingLink: 'pxlsync.su',
    permanentTags: [],
    customJs: '',
    domainType: 'system',
    systemDomain: 'smart-1.smartconstruct.app',
    customDomain: '',
    trafficBackMode: 'none',
    trafficBackCustomUrl: '',
    trafficBackOfferId: '',
    offerDisplayNames: {},
    offerDisplayDescriptions: {},
    offerCtaTexts: {},
    offerPoints: {},
};

export const DESCRIPTION_MAX = 500;

export const DESIGN_VARIANTS = [
    { value: 'variant1', label: 'Вариант 1', desc: 'Светлый, крупный заголовок, сетка офферов' },
    { value: 'variant2', label: 'Вариант 2', desc: 'Левый заголовок, список офферов' },
    { value: 'variant3', label: 'Вариант 3', desc: 'Компактные карточки, более тёмный хедер' },
    { value: 'variant4', label: 'Вариант 4', desc: 'Крупный заголовок и карточки, изображение в шапке' },
];

export const TRACKING_LINKS = [
    { value: 'pxlsync.su', label: 'pxlsync.su' },
    { value: 'trksync.com', label: 'trksync.com' },
    { value: 'link.sync', label: 'link.sync' },
];

export const OFFER_LOGO_GRADIENTS = [
    'linear-gradient(135deg, #f59e0b 0%, #7c3aed 100%)',
    'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
    'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
    'linear-gradient(135deg, #f97316 0%, #eab308 100%)',
    'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
    'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
    'linear-gradient(135deg, #84cc16 0%, #22c55e 100%)',
];

export function getOfferDisplayName(offer, config) {
    return config.offerDisplayNames?.[offer.id] ?? offer.title;
}

export function getOfferDisplayDescription(offer, config) {
    if (config.offerDisplayDescriptions && Object.prototype.hasOwnProperty.call(config.offerDisplayDescriptions, String(offer.id))) {
        return config.offerDisplayDescriptions[String(offer.id)] ?? '';
    }
    return '';
}

export function getOfferCtaText(offer, config) {
    return config.offerCtaTexts?.[offer.id] ?? config.ctaText ?? 'Оформить';
}

export function getOfferPoints(offer, config) {
    const points = config.offerPoints?.[offer.id];
    return Array.isArray(points) ? points : [];
}

export function getOfferLogoStyle(index) {
    return OFFER_LOGO_GRADIENTS[index % OFFER_LOGO_GRADIENTS.length];
}

export function getOrderedSelectedOffers(offers, config) {
    const selectedIds = config.selectedOfferIds ?? [];
    const selected = offers.filter(o => selectedIds.includes(o.id));

    const rankingMode = config.rankingMode ?? 'auto';
    const sortMetric = config.sortMetric ?? 'none';
    const showcaseOrder = config.showcaseOrder ?? [];

    if (rankingMode === 'auto' && sortMetric !== 'none') {
        return [...selected].sort((a, b) => (b[sortMetric] ?? 0) - (a[sortMetric] ?? 0));
    }

    if (showcaseOrder.length > 0) {
        const orderMap = {};
        showcaseOrder.forEach((id, i) => { orderMap[id] = i; });
        return [...selected].sort((a, b) => (orderMap[a.id] ?? Infinity) - (orderMap[b.id] ?? Infinity));
    }

    return selected;
}
