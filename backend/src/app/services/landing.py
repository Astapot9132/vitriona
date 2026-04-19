from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import Settings, get_settings
from src.infrastructure.models.partner_offer import PartnerOffer
from src.infrastructure.models.showcase import Showcase


OFFER_LOGO_GRADIENTS = [
    "linear-gradient(135deg, #f59e0b 0%, #7c3aed 100%)",
    "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
    "linear-gradient(135deg, #10b981 0%, #059669 100%)",
    "linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)",
    "linear-gradient(135deg, #f97316 0%, #eab308 100%)",
    "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
    "linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)",
    "linear-gradient(135deg, #84cc16 0%, #22c55e 100%)",
]


def _esc(value: str | None) -> str:
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _ordered_offers(offers: list[PartnerOffer], config: dict) -> list[PartnerOffer]:
    selected_ids = config.get("selectedOfferIds") or []
    selected = [offer for offer in offers if offer.id in selected_ids]

    ranking_mode = config.get("rankingMode", "auto")
    sort_metric = config.get("sortMetric", "none")
    showcase_order = config.get("showcaseOrder") or []

    if ranking_mode == "auto" and sort_metric in {"cr", "epc"}:
        return sorted(selected, key=lambda item: float(getattr(item, sort_metric, 0) or 0), reverse=True)

    if showcase_order:
        order_map = {int(value): index for index, value in enumerate(showcase_order)}
        return sorted(selected, key=lambda item: order_map.get(item.id, 10**9))

    return selected


def render_landing_html(config: dict, offers: list[PartnerOffer]) -> str:
    ordered = _ordered_offers(offers, config)
    title = _esc(config.get("title"))
    description = _esc(config.get("description"))
    legal_info = _esc(config.get("legalInfo")).replace("\n", "<br>")
    landing_points = (config.get("landingPoints") or [])[:3]
    design_variant = config.get("designVariant", "variant1")
    body_classes = []
    if design_variant == "variant1":
        body_classes.append("result-variant1")
    elif design_variant == "variant2":
        body_classes.append("result-variant2")
    elif design_variant == "variant4":
        body_classes.append("result-variant4")
    if config.get("offersTwoColDesktop"):
        body_classes.append("result-offers-two-col-desktop")

    points_html = "".join(f"<li>{_esc(point)}</li>" for point in landing_points)
    accented = set(config.get("accentedOfferIds") or [])
    cta_default = config.get("ctaText") or "Оформить"
    names = config.get("offerDisplayNames") or {}
    descriptions = config.get("offerDisplayDescriptions") or {}
    cta_texts = config.get("offerCtaTexts") or {}
    offer_points = config.get("offerPoints") or {}

    offer_cards = []
    for index, offer in enumerate(ordered):
        display_name = _esc(names.get(str(offer.id)) or names.get(offer.id) or offer.title)
        display_desc = _esc(descriptions.get(str(offer.id)) or descriptions.get(offer.id) or "")
        cta_text = _esc(cta_texts.get(str(offer.id)) or cta_texts.get(offer.id) or cta_default)
        points = offer_points.get(str(offer.id)) or offer_points.get(offer.id) or []
        points_list = "".join(f"<li>{_esc(point)}</li>" for point in points[:3])
        accent_class = " is-accent" if offer.id in accented else ""
        gradient = OFFER_LOGO_GRADIENTS[index % len(OFFER_LOGO_GRADIENTS)]
        letter = display_name[:1].upper() if display_name else "O"
        offer_cards.append(
            f"""
            <div class="offer-card{accent_class}">
                <div class="offer-card-logo" style="background:{gradient}"><span class="offer-card-logo-icon">{letter}</span></div>
                <div class="offer-card-text">
                    <div class="offer-card-title">{display_name}</div>
                    {f'<div class="offer-card-meta">{display_desc}</div>' if display_desc else ''}
                    {f'<ul class="offer-card-points">{points_list}</ul>' if points_list else ''}
                </div>
                <button type="button" class="offer-card-cta">{cta_text}</button>
            </div>
            """
        )

    if design_variant == "variant4":
        header_content = (
            '<div class="landing-header-hero-text">'
            f'<div class="landing-header-title">{title or "Без названия"}</div>'
            f'<div class="landing-header-subtitle">{description or "Описание лендинга не задано."}</div>'
            f'{f"<ul class=\"landing-points\">{points_html}</ul>" if points_html else ""}'
            "</div>"
            '<div class="landing-header-hero-img" aria-hidden="true"></div>'
        )
    else:
        header_content = (
            f'<div class="landing-header-title">{title or "Без названия"}</div>'
            f'<div class="landing-header-subtitle">{description or "Описание лендинга не задано."}</div>'
            f'{f"<ul class=\"landing-points\">{points_html}</ul>" if points_html else ""}'
        )

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <title>{title or "Лендинг"}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}
        body {{ margin: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #020617; color: #e5e7eb; }}
        body.result-variant1 {{ background: #eff6ff; color: #111827; }}
        body.result-variant2 {{ background: #ecfdf5; color: #111827; }}
        body.result-variant4 {{ background: #f3f4f6; color: #111827; }}
        .page-wrap {{ min-height: 100vh; padding: 24px 16px 32px; display: flex; justify-content: stretch; }}
        .landing-shell {{ width: 100%; border-radius: 20px; background: radial-gradient(circle at top, #0b1120, #020617 55%, #020617 100%); padding: 24px 20px 20px; }}
        .landing-shell.landing-variant1 {{ background: linear-gradient(to bottom, #eff6ff, #ffffff 26%); color: #111827; }}
        .landing-shell.landing-variant2 {{ background: linear-gradient(to right, #ecfdf5, #ffffff 35%); color: #111827; }}
        .landing-shell.landing-variant4 {{ background: #f3f4f6; color: #111827; }}
        .landing-header {{ display: flex; flex-direction: column; gap: 8px; }}
        .landing-header-title {{ font-size: 24px; font-weight: 700; }}
        .landing-header-subtitle {{ font-size: 14px; color: #9ca3af; }}
        .landing-offers-grid {{ margin-top: 10px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; }}
        .offer-card {{ border-radius: 12px; border: 1px solid #1f2937; background: rgba(15, 23, 42, 0.9); padding: 10px 12px; font-size: 13px; display: flex; flex-direction: row; align-items: center; gap: 10px; }}
        .landing-variant1 .offer-card, .landing-variant2 .offer-card, .landing-variant4 .offer-card {{ background: #fff; border: 1px solid #e5e7eb; color: #111827; }}
        .landing-variant1 .offer-card.is-accent {{ background: #ede9fe; border-color: #c4b5fd; }}
        .landing-variant2 .offer-card.is-accent {{ background: #fef9c3; border-color: #fde68a; }}
        .landing-variant4 .offer-card.is-accent {{ border-color: #16a34a; background: linear-gradient(to right, #86efac 0%, #ffffff 65%); }}
        .offer-card-logo {{ width: 44px; height: 44px; flex-shrink: 0; border-radius: 10px; display: flex; align-items: center; justify-content: center; }}
        .offer-card-logo-icon {{ color: #fff; font-size: 18px; font-weight: 700; }}
        .offer-card-text {{ flex: 1; min-width: 0; }}
        .offer-card-title {{ font-weight: 600; margin-bottom: 4px; }}
        .offer-card-meta {{ font-size: 12px; color: #6b7280; }}
        .offer-card-points {{ margin: 12px 0 0; padding-left: 22px; }}
        .offer-card-cta {{ margin-left: auto; display: block; padding: 8px 14px; font-size: 13px; border-radius: 999px; border: none; background: #2563eb; color: #fff; cursor: default; }}
        .landing-points {{ margin: 8px 0 0; padding-left: 22px; }}
        .landing-footer {{ margin-top: 18px; padding-top: 12px; border-top: 1px solid #d1d5db; font-size: 11px; color: #6b7280; line-height: 1.4; }}
        .landing-header-hero {{ flex-direction: column; background: #fff; border-radius: 14px; padding: 20px; gap: 16px; }}
        .landing-header-hero-img {{ width: 100%; height: 180px; border-radius: 14px; background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%); }}
        @media (min-width: 641px) {{
            body.result-offers-two-col-desktop .landing-offers-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            .landing-variant4 .landing-header-hero {{ flex-direction: row; justify-content: space-between; }}
            .landing-variant4 .landing-header-hero-text {{ flex: 1; }}
            .landing-variant4 .landing-header-hero-img {{ width: 320px; height: 220px; flex-shrink: 0; }}
        }}
        @media (max-width: 640px) {{
            .page-wrap {{ padding: 12px 10px 20px; }}
            .offer-card {{ flex-direction: column; align-items: stretch; }}
            .offer-card-cta {{ margin-left: 0; align-self: flex-start; }}
        }}
    </style>
</head>
<body class="{' '.join(body_classes)}">
    <div class="page-wrap">
        <main class="landing-shell landing-{design_variant}">
            <header class="landing-header{' landing-header-hero' if design_variant == 'variant4' else ''}">
                {header_content}
            </header>
            <section>
                <div class="landing-offers-grid">
                    {''.join(offer_cards)}
                </div>
            </section>
            <div class="landing-footer">{legal_info}</div>
        </main>
    </div>
</body>
</html>"""


class LandingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def get_public_dir(self) -> Path:
        return Path(self.settings.storage_dir).joinpath("public")

    def get_preview_url(self, showcase_id: int) -> str | None:
        path = self.get_public_dir().joinpath("landings", str(showcase_id), "index.html")
        if path.exists():
            return f"/storage/landings/{showcase_id}/index.html"
        return None

    async def generate(self, db: AsyncSession, showcase: Showcase) -> str:
        offers = list(showcase.user.partner_offers)
        html = render_landing_html(showcase.config or {}, offers)
        target_dir = self.get_public_dir().joinpath("landings", str(showcase.id))
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir.joinpath("index.html")
        target_path.write_text(html, encoding="utf-8")
        return f"/storage/landings/{showcase.id}/index.html"
