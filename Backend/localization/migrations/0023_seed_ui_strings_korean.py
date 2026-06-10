from django.db import migrations

KOREAN_LANGUAGE_CODE = "kr"

TRANSLATIONS = {
    "about.all": "전체",
    "about.allergens": "알레르겐",
    "about.calories": "칼로리",
    "about.follow-us": "팔로우하기",
    "about.ingredients": "재료",
    "about.no-dishes-found-in-this-category": "이 카테고리에서 요리를 찾을 수 없습니다.",
    "about.popular": "인기",
    "about.popular-choice": "인기 메뉴",
    "about.prep-time": "조리 시간",
    "about.price": "가격",
    "about.view-details": "자세히 보기",
    "about.visit_us": "방문하기",
    "abouth.popular-choice": "인기 메뉴",
    "adisyon.bill": "계산서",
    "adisyon.discounted-total-price": "할인 합계",
    "adisyon.total-price": "총 금액",
    "favorites.add-dishes-": (
        "메뉴 항목의 계산서 아이콘을 눌러 주문에 요리를 추가하세요."
    ),
    "favorites.add-dishes-to-order": (
        "메뉴의 상품에서 계산서 아이콘을 눌러 주문에 추가하세요"
    ),
    "favorites.exploremenu": "메뉴 둘러보기",
    "favorites.no-items-yet": "아직 항목이 없습니다",
    "favorites.your-order-list": "주문 목록",
    "footer-nav.about": "소개",
    "footer-nav.adisyon": "계산서",
    "footer-nav.home": "홈",
    "footer-nav.menu": "메뉴",
    "menu.our-menu": "우리 메뉴",
    "menu.search-dishes": "요리 검색...",
    "product-detaile.add-to-order": "주문에 추가",
    "product-detaile.added-to-order": "주문에 추가됨",
}


def seed_ui_strings_korean(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    language = Language.objects.filter(
        code=KOREAN_LANGUAGE_CODE, is_active=True
    ).first()
    if not language:
        return

    for key_name, text in TRANSLATIONS.items():
        key = UiStringKey.objects.filter(key=key_name).first()
        if not key:
            continue

        UiString.objects.update_or_create(
            language=language,
            key=key,
            defaults={"text": text},
        )


def unseed_ui_strings_korean(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    keys = UiStringKey.objects.filter(key__in=TRANSLATIONS.keys())
    UiString.objects.filter(
        language__code=KOREAN_LANGUAGE_CODE,
        key__in=keys,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0022_seed_ui_strings_additional_languages"),
    ]

    operations = [
        migrations.RunPython(seed_ui_strings_korean, unseed_ui_strings_korean),
    ]
