from django.db import migrations

NEW_LANGUAGE_CODES = ("it", "fr", "es", "ja", "zh", "ru", "ar")

TRANSLATIONS = {
    "about.all": {
        "it": "Tutti",
        "fr": "Tous",
        "es": "Todos",
        "ja": "すべて",
        "zh": "全部",
        "ru": "Все",
        "ar": "الكل",
    },
    "about.allergens": {
        "it": "Allergeni",
        "fr": "Allergènes",
        "es": "Alérgenos",
        "ja": "アレルゲン",
        "zh": "过敏原",
        "ru": "Аллергены",
        "ar": "مسببات الحساسية",
    },
    "about.calories": {
        "it": "Calorie",
        "fr": "Calories",
        "es": "Calorías",
        "ja": "カロリー",
        "zh": "卡路里",
        "ru": "Калории",
        "ar": "السعرات الحرارية",
    },
    "about.follow-us": {
        "it": "Seguici",
        "fr": "Suivez-nous",
        "es": "Síguenos",
        "ja": "フォローする",
        "zh": "关注我们",
        "ru": "Подписывайтесь на нас",
        "ar": "تابعنا",
    },
    "about.ingredients": {
        "it": "Ingredienti",
        "fr": "Ingrédients",
        "es": "Ingredientes",
        "ja": "材料",
        "zh": "配料",
        "ru": "Ингредиенты",
        "ar": "المكونات",
    },
    "about.no-dishes-found-in-this-category": {
        "it": "Nessun piatto trovato in questa categoria.",
        "fr": "Aucun plat trouvé dans cette catégorie.",
        "es": "No se encontraron platos en esta categoría.",
        "ja": "このカテゴリに料理は見つかりませんでした。",
        "zh": "此分类下未找到菜品。",
        "ru": "В этой категории блюда не найдены.",
        "ar": "لم يتم العثور على أطباق في هذه الفئة.",
    },
    "about.popular": {
        "it": "Popolare",
        "fr": "Populaire",
        "es": "Popular",
        "ja": "人気",
        "zh": "热门",
        "ru": "Популярное",
        "ar": "شائع",
    },
    "about.popular-choice": {
        "it": "Scelta popolare",
        "fr": "Choix populaire",
        "es": "Elección popular",
        "ja": "人気の選択",
        "zh": "热门之选",
        "ru": "Популярный выбор",
        "ar": "اختيار شائع",
    },
    "about.prep-time": {
        "it": "Tempo di preparazione",
        "fr": "Temps de préparation",
        "es": "Tiempo de preparación",
        "ja": "調理時間",
        "zh": "准备时间",
        "ru": "Время приготовления",
        "ar": "وقت التحضير",
    },
    "about.price": {
        "it": "Prezzo",
        "fr": "Prix",
        "es": "Precio",
        "ja": "価格",
        "zh": "价格",
        "ru": "Цена",
        "ar": "السعر",
    },
    "about.view-details": {
        "it": "Vedi dettagli",
        "fr": "Voir les détails",
        "es": "Ver detalles",
        "ja": "詳細を見る",
        "zh": "查看详情",
        "ru": "Подробнее",
        "ar": "عرض التفاصيل",
    },
    "about.visit_us": {
        "it": "Visitaci",
        "fr": "Venez nous voir",
        "es": "Visítanos",
        "ja": "お越しください",
        "zh": "欢迎光临",
        "ru": "Посетите нас",
        "ar": "زورونا",
    },
    "abouth.popular-choice": {
        "it": "Scelta popolare",
        "fr": "Choix populaire",
        "es": "Elección popular",
        "ja": "人気の選択",
        "zh": "热门之选",
        "ru": "Популярный выбор",
        "ar": "اختيار شائع",
    },
    "adisyon.bill": {
        "it": "Conto",
        "fr": "Addition",
        "es": "Cuenta",
        "ja": "会計",
        "zh": "账单",
        "ru": "Счёт",
        "ar": "الحساب",
    },
    "adisyon.discounted-total-price": {
        "it": "Totale scontato",
        "fr": "Total remisé",
        "es": "Total con descuento",
        "ja": "割引後合計",
        "zh": "折扣后总计",
        "ru": "Итого со скидкой",
        "ar": "الإجمالي بعد الخصم",
    },
    "adisyon.total-price": {
        "it": "Importo totale",
        "fr": "Montant total",
        "es": "Importe total",
        "ja": "合計金額",
        "zh": "总金额",
        "ru": "Общая сумма",
        "ar": "المبلغ الإجمالي",
    },
    "favorites.add-dishes-": {
        "it": "Tocca l'icona del conto su un piatto del menu per aggiungerlo al tuo ordine.",
        "fr": "Appuyez sur l'icône d'addition sur un plat du menu pour l'ajouter à votre commande.",
        "es": "Toca el icono del ticket en cualquier plato del menú para añadirlo a tu pedido.",
        "ja": "メニューの料理のレシートアイコンをタップして注文に追加してください。",
        "zh": "点击菜单项上的账单图标将菜品添加到订单。",
        "ru": "Нажмите на значок счёта у блюда в меню, чтобы добавить его в заказ.",
        "ar": "اضغط على أيقونة الفاتورة على أي عنصر في القائمة لإضافته إلى طلبك.",
    },
    "favorites.add-dishes-to-order": {
        "it": "Tocca l'icona del conto su un piatto del menu per aggiungerlo al tuo ordine",
        "fr": "Appuyez sur l'icône d'addition sur un plat du menu pour l'ajouter à votre commande",
        "es": "Toca el icono del ticket en cualquier plato del menú para añadirlo a tu pedido",
        "ja": "メニューの料理のレシートアイコンをタップして注文に追加してください",
        "zh": "点击菜单项上的账单图标将菜品添加到订单",
        "ru": "Нажмите на значок счёта у блюда в меню, чтобы добавить его в заказ",
        "ar": "اضغط على أيقونة الفاتورة على أي عنصر في القائمة لإضافته إلى طلبك",
    },
    "favorites.exploremenu": {
        "it": "Esplora il menu",
        "fr": "Explorer le menu",
        "es": "Explorar el menú",
        "ja": "メニューを見る",
        "zh": "浏览菜单",
        "ru": "Смотреть меню",
        "ar": "استكشف القائمة",
    },
    "favorites.no-items-yet": {
        "it": "Nessun articolo ancora",
        "fr": "Aucun article pour le moment",
        "es": "Aún no hay artículos",
        "ja": "まだ商品がありません",
        "zh": "暂无商品",
        "ru": "Пока нет позиций",
        "ar": "لا توجد عناصر بعد",
    },
    "favorites.your-order-list": {
        "it": "Il tuo ordine",
        "fr": "Votre commande",
        "es": "Tu lista de pedido",
        "ja": "ご注文リスト",
        "zh": "您的订单",
        "ru": "Ваш заказ",
        "ar": "قائمة طلبك",
    },
    "footer-nav.about": {
        "it": "Chi siamo",
        "fr": "À propos",
        "es": "Acerca de",
        "ja": "について",
        "zh": "关于",
        "ru": "О нас",
        "ar": "عنّا",
    },
    "footer-nav.adisyon": {
        "it": "Conto",
        "fr": "Addition",
        "es": "Cuenta",
        "ja": "会計",
        "zh": "账单",
        "ru": "Счёт",
        "ar": "الفاتورة",
    },
    "footer-nav.home": {
        "it": "Home",
        "fr": "Accueil",
        "es": "Inicio",
        "ja": "ホーム",
        "zh": "首页",
        "ru": "Главная",
        "ar": "الرئيسية",
    },
    "footer-nav.menu": {
        "it": "Menu",
        "fr": "Menu",
        "es": "Menú",
        "ja": "メニュー",
        "zh": "菜单",
        "ru": "Меню",
        "ar": "القائمة",
    },
    "menu.our-menu": {
        "it": "Il nostro menu",
        "fr": "Notre menu",
        "es": "Nuestro menú",
        "ja": "当店のメニュー",
        "zh": "我们的菜单",
        "ru": "Наше меню",
        "ar": "قائمتنا",
    },
    "menu.search-dishes": {
        "it": "Cerca piatti...",
        "fr": "Rechercher des plats...",
        "es": "Buscar platos...",
        "ja": "料理を検索...",
        "zh": "搜索菜品...",
        "ru": "Поиск блюд...",
        "ar": "ابحث عن الأطباق...",
    },
    "product-detaile.add-to-order": {
        "it": "Aggiungi al conto",
        "fr": "Ajouter à l'addition",
        "es": "Añadir a la cuenta",
        "ja": "会計に追加",
        "zh": "添加到账单",
        "ru": "Добавить в счёт",
        "ar": "أضف إلى الفاتورة",
    },
    "product-detaile.added-to-order": {
        "it": "Aggiunto al conto",
        "fr": "Ajouté à l'addition",
        "es": "Añadido a la cuenta",
        "ja": "会計に追加済み",
        "zh": "已添加到账单",
        "ru": "Добавлено в счёт",
        "ar": "تمت الإضافة إلى الفاتورة",
    },
}


def seed_ui_strings_additional_languages(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    languages = {
        lang.code: lang
        for lang in Language.objects.filter(code__in=NEW_LANGUAGE_CODES, is_active=True)
    }

    for key_name, translations in TRANSLATIONS.items():
        key = UiStringKey.objects.filter(key=key_name).first()
        if not key:
            continue

        for code, text in translations.items():
            language = languages.get(code)
            if language:
                UiString.objects.update_or_create(
                    language=language,
                    key=key,
                    defaults={"text": text},
                )


def unseed_ui_strings_additional_languages(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    keys = UiStringKey.objects.filter(key__in=TRANSLATIONS.keys())
    UiString.objects.filter(
        language__code__in=NEW_LANGUAGE_CODES,
        key__in=keys,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0021_seed_additional_languages"),
    ]

    operations = [
        migrations.RunPython(
            seed_ui_strings_additional_languages,
            unseed_ui_strings_additional_languages,
        ),
    ]
