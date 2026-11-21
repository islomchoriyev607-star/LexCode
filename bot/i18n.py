"""Uch tilli matnlar: oʻzbek (lotin, rasmiy imlo: oʻ, gʻ — U+02BB; tutuq — U+02BC), rus, ingliz.
Foydalanish: t(lang, 'KEY', **kw). Til topilmasa — oʻzbekcha."""

LANGS = ('uz', 'ru', 'en')
LANG_LABELS = {'uz': 'Oʻzbekcha', 'ru': 'Русский', 'en': 'English'}
# Tanlov: oʻzbek tili ikki yozuvda (kirill — standart; yangi lotin — OʻRQ–1184, 21.10.2026), rus, ingliz
LANG_CHOICES = [('uz-cyrl', '🇺🇿 Ўзбекча (кирилл)'), ('uz-latn', '🇺🇿 Özbekça (yangi lotin)'), ('ru', '🇷🇺 Русский'),
                ('en', '🇬🇧 English')]
LANG_FLAGS = {'uz': '🇺🇿', 'ru': '🇷🇺', 'en': '🇬🇧'}
AI_LANG = {'uz': 'oʻzbek (lotin yozuvi)', 'ru': 'rus', 'en': 'ingliz'}

_DISC = {
    'uz': ('⚖️ Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida. Javob umumiy qonunchilikka asoslangan: '
           'tashkilotning ichki tartib qoidalari (masalan, universitetning ichki tartib qoidalari) hisobga olinmagan.'),
    'ru': ('⚖️ Это не юридическая консультация, окончательную оценку даёт юрист. Ответ основан на общем законодательстве: '
           'внутренние правила организации (например, правила внутреннего распорядка университета) не учитывались.'),
    'en': ('⚖️ This is not legal advice; the final assessment is up to a lawyer. The answer is based on general legislation: '
           'an organisation’s internal rules (for example, a university’s internal regulations) were not taken into account.'),
}
_CONSENT_BODY = {
    'uz': ('🔒 <b>Rozilik</b>\n\n'
           '• Yuborgan matn, ovoz va rasmlaringiz faqat vaziyatni tahlil qilish uchun ishlatiladi.\n'
           '• Ovoz va rasm matnga oʻgirilgach, asl fayl oʻchiriladi.\n'
           '• Tahlil uchun matn sunʼiy intellekt xizmatlariga (Groq, Google Gemini) yuboriladi.\n'
           '• Murojaat idoraga faqat sizning roziligingiz va Yuridik klinika yuristining tekshiruvi bilan yuboriladi.'),
    'ru': ('🔒 <b>Согласие</b>\n\n'
           '• Ваши текст, голосовые сообщения и изображения используются только для анализа ситуации.\n'
           '• После перевода в текст исходный аудио- или графический файл удаляется.\n'
           '• Для анализа текст передаётся сервисам искусственного интеллекта (Groq, Google Gemini).\n'
           '• Обращение направляется в орган только с вашего согласия и после проверки юристом Юридической клиники.'),
    'en': ('🔒 <b>Consent</b>\n\n'
           '• Your text, voice messages and images are used only to analyse your situation.\n'
           '• Once audio or images are converted to text, the original file is deleted.\n'
           '• For the analysis, the text is sent to AI services (Groq, Google Gemini).\n'
           '• An appeal is sent to an authority only with your consent and after review by a Legal Clinic lawyer.'),
}

T: dict[str, dict] = {
    'DISCLAIMER': _DISC,
    'LANG_ASK': {'uz': '🌐 Tilni tanlang · Выберите язык · Choose a language', 'ru': '🌐 Tilni tanlang · Выберите язык · Choose a language',
                 'en': '🌐 Tilni tanlang · Выберите язык · Choose a language'},
    'LANG_SET': {'uz': '✅ Til: Oʻzbekcha', 'ru': '✅ Язык: русский', 'en': '✅ Language: English'},
    'START': {
        'uz': ('Assalomu alaykum! Men — <b>Huquqiy Navigator</b>.\n\n'
               'Vaziyatingizni yozing yoki ovozli xabar yuboring. Uni amaldagi qonunchilik (lex.uz) bilan solishtirib, '
               'quyidagilarni aytaman:\n'
               '• huquq va majburiyatlaringiz;\n'
               '• <b>kimga, qayerga va qachon</b> murojaat qilish kerakligi;\n'
               '• qanday dalillarni saqlash kerakligi;\n'
               '• shuningdek, ariza matnini tayyorlab beraman.\n\n'
               'Davom etish uchun shaxsiy maʼlumotlaringizni qayta ishlashga rozilik bering.'),
        'ru': ('Здравствуйте! Я — <b>Правовой навигатор</b>.\n\n'
               'Опишите ситуацию текстом или отправьте голосовое сообщение. Я сопоставлю её с действующим '
               'законодательством (lex.uz) и подскажу:\n'
               '• ваши права и обязанности;\n'
               '• <b>куда, к кому и в какой срок</b> обращаться;\n'
               '• какие доказательства сохранить;\n'
               '• а также подготовлю текст заявления.\n\n'
               'Чтобы продолжить, дайте согласие на обработку персональных данных.'),
        'en': ('Hello! I am <b>Legal Navigator</b>.\n\n'
               'Describe your situation in a message or send a voice note. I will compare it with current legislation '
               '(lex.uz) and tell you:\n'
               '• your rights and obligations;\n'
               '• <b>where, to whom and by when</b> to file an appeal;\n'
               '• what evidence to keep;\n'
               '• and I will draft the application for you.\n\n'
               'To continue, please consent to the processing of your personal data.'),
    },
    'CONSENT': {k: v + q for (k, v), q in zip(_CONSENT_BODY.items(), ('\n\nRozimisiz?', '\n\nВы согласны?', '\n\nDo you agree?'))},
    'PRIVACY': {k: v + q for (k, v), q in zip(_CONSENT_BODY.items(), (
        '\n\nRozilikni qaytarib olish uchun Yuridik klinikaga yozing yoki /start orqali «Yoʻq» tugmasini bosing.',
        '\n\nЧтобы отозвать согласие, напишите в Юридическую клинику или нажмите «Нет» через /start.',
        '\n\nTo withdraw consent, contact the Legal Clinic or press “No” via /start.'))},
    'CONSENT_YES': {'uz': '✅ Roziman', 'ru': '✅ Согласен', 'en': '✅ I agree'},
    'CONSENT_NO_BTN': {'uz': 'Yoʻq', 'ru': 'Нет', 'en': 'No'},
    'CONSENT_GIVEN': {'uz': '✅ <i>Rozilik berildi</i>', 'ru': '✅ <i>Согласие получено</i>', 'en': '✅ <i>Consent given</i>'},
    'CONSENT_OK': {'uz': '✅ Rahmat! Endi vaziyatingizni yozing yoki ovozli xabar yuboring.',
                   'ru': '✅ Спасибо! Теперь опишите ситуацию или отправьте голосовое сообщение.',
                   'en': '✅ Thank you! Now describe your situation or send a voice message.'},
    'CONSENT_NEED': {'uz': 'Avval rozilik bering: /start', 'ru': 'Сначала дайте согласие: /start', 'en': 'Please give your consent first: /start'},
    'CONSENT_NO': {'uz': 'Tushunarli. Rozilik bermasangiz, bot vaziyatni tahlil qila olmaydi. Fikringiz oʻzgarsa: /start',
                   'ru': 'Понятно. Без согласия бот не сможет проанализировать ситуацию. Если передумаете: /start',
                   'en': 'Understood. Without consent the bot cannot analyse your situation. If you change your mind: /start'},
    'HELP': {
        'uz': ('<b>Qanday foydalanish</b>\n'
               '1. Vaziyatni oddiy soʻzlar bilan yozing yoki ovozli xabar yuboring.\n'
               '2. Telefon suhbati yozuvini yoki SMS skrinshotini ham yuborishingiz mumkin.\n'
               '3. Bot qonundagi tegishli moddalarni havola bilan koʻrsatadi va qayerga murojaat qilishni aytadi.\n'
               '4. Kerak boʻlsa, ariza matnini tayyorlaydi.\n\n'
               '/yangi — yangi murojaat\n/til — tilni oʻzgartirish\n/maxfiylik — shaxsiy maʼlumotlar'),
        'ru': ('<b>Как пользоваться</b>\n'
               '1. Опишите ситуацию простыми словами или отправьте голосовое сообщение.\n'
               '2. Можно также отправить запись телефонного разговора или скриншот SMS.\n'
               '3. Бот покажет нужные статьи закона со ссылками и подскажет, куда обращаться.\n'
               '4. При необходимости подготовит текст заявления.\n\n'
               '/yangi — новое обращение\n/til — сменить язык\n/maxfiylik — персональные данные'),
        'en': ('<b>How to use</b>\n'
               '1. Describe the situation in plain words or send a voice message.\n'
               '2. You can also send a phone call recording or an SMS screenshot.\n'
               '3. The bot shows the relevant articles of law with links and tells you where to apply.\n'
               '4. If needed, it drafts the application text.\n\n'
               '/yangi — new appeal\n/til — change language\n/maxfiylik — personal data'),
    },
    'NEW': {'uz': 'Yangi murojaat. Vaziyatingizni yozing yoki ovozli xabar yuboring.',
            'ru': 'Новое обращение. Опишите ситуацию или отправьте голосовое сообщение.',
            'en': 'New appeal. Describe your situation or send a voice message.'},
    'EMERGENCY': {
        'uz': ('🚨 <b>Hayotingiz yoki sogʻligʻingizga xavf boʻlsa, hozir qoʻngʻiroq qiling:</b>\n'
               '• <b>112</b> — yagona favqulodda xizmat\n• <b>102</b> — politsiya\n• <b>103</b> — tez tibbiy yordam\n\n'
               'Xavfsiz joyga oʻtgach, vaziyatni yozing — qayerga murojaat qilishni tushuntiraman.'),
        'ru': ('🚨 <b>Если есть угроза жизни или здоровью, звоните прямо сейчас:</b>\n'
               '• <b>112</b> — единая экстренная служба\n• <b>102</b> — полиция\n• <b>103</b> — скорая помощь\n\n'
               'Когда будете в безопасности, опишите ситуацию — я подскажу, куда обращаться.'),
        'en': ('🚨 <b>If your life or health is in danger, call now:</b>\n'
               '• <b>112</b> — single emergency number\n• <b>102</b> — police\n• <b>103</b> — ambulance\n\n'
               'Once you are safe, describe the situation and I will explain where to apply.'),
    },
    'EMERGENCY_SHORT': {'uz': '🚨 <b>Xavf boʻlsa, hozir qoʻngʻiroq qiling: 112, 102 (politsiya), 103 (tez yordam).</b>',
                        'ru': '🚨 <b>При угрозе звоните сейчас: 112, 102 (полиция), 103 (скорая помощь).</b>',
                        'en': '🚨 <b>If you are in danger, call now: 112, 102 (police), 103 (ambulance).</b>'},
    # ---------- Navigator ----------
    'CLARIFY_INTRO': {'uz': 'Yaxshi, tushundim. Aniqroq yoʻl topishim uchun bir-ikki savol beraman — javob bera olmasangiz, oʻtkazib yuboring.',
                      'ru': 'Понял. Чтобы подобрать точный путь, задам пару вопросов — если не знаете ответа, просто пропустите.',
                      'en': 'Got it. To find the right path, I’ll ask one or two questions — skip any you can’t answer.'},
    'BTN_SKIP': {'uz': 'Oʻtkazib yuborish', 'ru': 'Пропустить', 'en': 'Skip'},
    'DISTRICT_ASK': {'uz': '📍 Qaysi shahar va tumandasiz? Yaqin idoralarni xaritada koʻrsataman.\nJoylashuvingizni yuboring yoki tuman nomini yozing (masalan: Toshkent, Chilonzor).',
                     'ru': '📍 В каком вы городе и районе? Покажу ближайшие учреждения на карте.\nОтправьте геолокацию или напишите район (например: Ташкент, Чиланзар).',
                     'en': '📍 Which city and district are you in? I’ll show nearby offices on the map.\nShare your location or type the district (e.g. Tashkent, Chilanzar).'},
    'BTN_LOCATION': {'uz': '📍 Joylashuvni yuborish', 'ru': '📍 Отправить геолокацию', 'en': '📍 Share location'},
    'DISTRICT_OK': {'uz': '👌 Qabul qilindi.', 'ru': '👌 Принято.', 'en': '👌 Got it.'},
    'ROUTES_INTRO': {'uz': '🧭 <b>Sizga {n} ta yoʻl topdim.</b> Qaysi biri bilan boramiz? Men har qadamda yoningizdaman.',
                     'ru': '🧭 <b>Нашёл для вас {n} пути.</b> Каким пойдём? Я буду рядом на каждом шаге.',
                     'en': '🧭 <b>I found {n} paths for you.</b> Which one shall we take? I’ll be with you at every step.'},
    'RECOMMENDED': {'uz': 'tavsiya', 'ru': 'рекомендую', 'en': 'recommended'},
    'BTN_DETAILS': {'uz': '📚 Batafsil va qonun', 'ru': '📚 Подробнее и закон', 'en': '📚 Details and law'},
    'STEP_HEAD': {'uz': '🧭 <b>{route}</b> · {i}/{n}-qadam', 'ru': '🧭 <b>{route}</b> · шаг {i} из {n}', 'en': '🧭 <b>{route}</b> · step {i} of {n}'},
    'STEP_WHERE': {'uz': '📍 <b>Qayerga:</b> {x}', 'ru': '📍 <b>Куда:</b> {x}', 'en': '📍 <b>Where:</b> {x}'},
    'STEP_BRING': {'uz': '🎒 <b>Olib boring:</b> {x}', 'ru': '🎒 <b>Взять с собой:</b> {x}', 'en': '🎒 <b>Bring:</b> {x}'},
    'STEP_DEADLINE': {'uz': '⏱ <b>Javob muddati:</b> {n} kun', 'ru': '⏱ <b>Срок ответа:</b> {n} дн.', 'en': '⏱ <b>Response time:</b> {n} days'},
    'BTN_DONE': {'uz': '✅ Bajardim', 'ru': '✅ Сделал', 'en': '✅ Done'},
    'BTN_MAP': {'uz': '🚌 Qanday boraman', 'ru': '🚌 Как добраться', 'en': '🚌 How to get there'},
    'MAP_HINT': {'uz': '🚌 Xaritada idorani bosing → «Yoʻnalish» → avtobus belgisi: avtobus va metro raqamlari chiqadi.',
                 'ru': '🚌 На карте нажмите на учреждение → «Маршрут» → значок автобуса: появятся номера автобусов и метро.',
                 'en': '🚌 On the map tap the office → “Route” → the bus icon: bus and metro numbers will appear.'},
    'BTN_PRINT': {'uz': '🖨 Chop etish joylari', 'ru': '🖨 Где распечатать', 'en': '🖨 Where to print'},
    'BTN_MORE': {'uz': '⋯ Yana', 'ru': '⋯ Ещё', 'en': '⋯ More'},
    'BTN_LESS': {'uz': '↩️ Orqaga', 'ru': '↩️ Назад', 'en': '↩️ Back'},
    'BTN_DONATE': {'uz': '❤️ Loyihani qoʻllab-quvvatlash', 'ru': '❤️ Поддержать проект', 'en': '❤️ Support the project'},
    'SOON_ROUTE': {'uz': '🚌 Yoʻnalish va transport maʼlumotlari hali qoʻshilmagan. Idoralar manzili qoʻshilgach, shu yerda chiqadi.',
                   'ru': '🚌 Маршруты и транспорт ещё не добавлены. Когда добавим адреса учреждений, они появятся здесь.',
                   'en': '🚌 Routes and transport are not added yet. Once office addresses are added, they will appear here.'},
    'SOON_PRINT': {'uz': '🖨 Chop etish joylari hali qoʻshilmagan. Hamkor manzillar qoʻshilgach, shu yerda chiqadi.',
                   'ru': '🖨 Места печати ещё не добавлены. Когда добавим адреса партнёров, они появятся здесь.',
                   'en': '🖨 Print locations are not added yet. Once partner addresses are added, they will appear here.'},
    'SOON_DONATE': {'uz': '❤️ Donat hali mavjud emas. Rahmat — qoʻllab-quvvatlash imkoniyati tez orada qoʻshiladi.',
                    'ru': '❤️ Пожертвования пока недоступны. Спасибо — возможность поддержать скоро появится.',
                    'en': '❤️ Donations are not available yet. Thank you — this option is coming soon.'},
    'TYPE_HINT': {'uz': '✍️ Variant mos kelmasa, javobni oʻzingiz yozib yuboring.',
                  'ru': '✍️ Если вариант не подходит, напишите ответ сами.',
                  'en': '✍️ If no option fits, just type your answer.'},
    'TYPE_ONLY': {'uz': '✍️ Javobni yozib yuboring (masalan, summa yoki sana).',
                  'ru': '✍️ Напишите ответ (например, сумму или дату).',
                  'en': '✍️ Type your answer (e.g. an amount or a date).'},
    'PRINT_QUERY': {'uz': 'nusxa koʻchirish chop etish xizmati', 'ru': 'копицентр печать документов', 'en': 'print copy center'},
    'BTN_PDF': {'uz': '📄 Ariza (PDF)', 'ru': '📄 Заявление (PDF)', 'en': '📄 Application (PDF)'},
    'BTN_ASK': {'uz': '💬 Savolim bor', 'ru': '💬 Есть вопрос', 'en': '💬 I have a question'},
    'BTN_ALT': {'uz': '🔀 Boshqa yoʻl', 'ru': '🔀 Другой путь', 'en': '🔀 Another path'},
    'BTN_LAWYER': {'uz': '⚖️ Advokat yoki klinika', 'ru': '⚖️ Адвокат или клиника', 'en': '⚖️ Lawyer or clinic'},
    'LAWYER_QUERY': {'uz': 'advokatlik byurosi', 'ru': 'адвокатское бюро', 'en': 'law office'},
    'LAWYER_TEXT': {'uz': '⚖️ Yurist bilan maslahatlashmoqchi boʻlsangiz: yaqin advokatlik byurolari xaritada. Bepul maslahat uchun universitetning Yuridik klinikasiga ham yozishingiz mumkin.',
                    'ru': '⚖️ Если хотите посоветоваться с юристом: ближайшие адвокатские бюро — на карте. За бесплатной консультацией можно обратиться в Юридическую клинику университета.',
                    'en': '⚖️ If you’d like to consult a lawyer: nearby law offices are on the map. For free advice you can also contact the university Legal Clinic.'},
    'WAIT_SET': {'uz': '👍 Zoʻr! Endi javobni kutamiz. {n} kundan soʻng oʻzim soʻrayman — eslatishni menga qoldiring.',
                 'ru': '👍 Отлично! Теперь ждём ответа. Через {n} дн. я сам спрошу — напоминание беру на себя.',
                 'en': '👍 Great! Now we wait for the reply. In {n} days I’ll check in with you — leave the reminder to me.'},
    'NEXT_STEP': {'uz': '👍 Zoʻr, keyingi qadam:', 'ru': '👍 Отлично, следующий шаг:', 'en': '👍 Great, next step:'},
    'CHECK': {'uz': '🔔 <b>{route}</b>: javob keldimi? Vaziyat qanday?', 'ru': '🔔 <b>{route}</b>: ответ пришёл? Как ситуация?',
              'en': '🔔 <b>{route}</b>: has a reply come? How are things?'},
    'BTN_RES_OK': {'uz': '✅ Hal boʻldi', 'ru': '✅ Решилось', 'en': '✅ Resolved'},
    'BTN_RES_WAIT': {'uz': '⏳ Hali javob yoʻq', 'ru': '⏳ Ответа пока нет', 'en': '⏳ No reply yet'},
    'BTN_RES_NO': {'uz': '❌ Rad etishdi', 'ru': '❌ Отказали', 'en': '❌ Refused'},
    'RES_OK': {'uz': '🎉 Ajoyib, tabriklayman! Murojaat yopildi. Yana biror masala boʻlsa — men shu yerdaman, bemalol yozing.',
               'ru': '🎉 Отлично, поздравляю! Обращение закрыто. Если появится другой вопрос — я здесь, пишите.',
               'en': '🎉 Wonderful, congratulations! The appeal is closed. If anything else comes up, I’m here — just write.'},
    'RES_WAIT': {'uz': 'Tushunarli, sabr qilamiz. {n} kundan soʻng yana soʻrayman. Muddat oʻtib ketsa, keyingi qadamni koʻrsataman.',
                 'ru': 'Понятно, подождём. Через {n} дн. спрошу снова. Если срок истечёт, покажу следующий шаг.',
                 'en': 'Understood, we’ll wait. I’ll check again in {n} days. If the deadline passes, I’ll show you the next step.'},
    'RES_NO': {'uz': 'Afsus. Lekin bu yoʻlning oxiri emas — keyingi qadamga oʻtamiz:', 'ru': 'Жаль. Но это не конец — переходим к следующему шагу:',
               'en': 'Sorry to hear that. But this isn’t the end — let’s move to the next step:'},
    'ROUTE_DONE': {'uz': 'Bu yoʻlning hamma qadamlari bajarildi. Vaziyat hal boʻldimi?', 'ru': 'Все шаги этого пути выполнены. Ситуация решилась?',
                   'en': 'All steps on this path are done. Has the situation been resolved?'},
    'ROUTE_EXHAUSTED': {'uz': 'Bu yoʻlda qadam qolmadi. Boshqa yoʻlni tanlab koʻramizmi yoki yurist bilan maslahatlashasizmi?',
                        'ru': 'На этом пути шагов не осталось. Попробуем другой путь или посоветуетесь с юристом?',
                        'en': 'No steps are left on this path. Shall we try another path, or would you like to consult a lawyer?'},
    'ASK_PROMPT': {'uz': '💬 Savolingizni yozing — shu murojaat boʻyicha javob beraman.', 'ru': '💬 Напишите вопрос — отвечу по этому обращению.',
                   'en': '💬 Type your question — I’ll answer about this appeal.'},
    'BTN_BACK_STEP': {'uz': '↩️ Qadamga qaytish', 'ru': '↩️ Вернуться к шагу', 'en': '↩️ Back to the step'},
    'PDF_CAPTION': {'uz': '📄 Ariza #{id}. Chop eting, chiziqli joylarni qoʻlda toʻldiring va imzolang.',
                    'ru': '📄 Заявление #{id}. Распечатайте, заполните от руки места с линиями и подпишите.',
                    'en': '📄 Application #{id} (in Uzbek). Print it, fill in the underlined fields by hand and sign.'},
    'NO_ROUTES': {'uz': 'Bu vaziyat uchun aniq yoʻl tuza olmadim. Batafsil maʼlumot va qonun pastda; yurist bilan maslahatlashishni tavsiya qilaman.',
                  'ru': 'Не удалось составить точный путь для этой ситуации. Подробности и закон — ниже; рекомендую посоветоваться с юристом.',
                  'en': 'I couldn’t build a clear path for this situation. Details and the law are below; I recommend consulting a lawyer.'},
    'RECEIVED': {'uz': '⏳ Qabul qilindi, tahlil qilyapman…', 'ru': '⏳ Принято, анализирую…', 'en': '⏳ Received, analysing…'},
    'TRANSCRIBING': {'uz': '🎧 Ovozni matnga oʻgiryapman…', 'ru': '🎧 Перевожу голос в текст…', 'en': '🎧 Converting voice to text…'},
    'READING': {'uz': '🖼 Rasmni oʻqiyapman…', 'ru': '🖼 Читаю изображение…', 'en': '🖼 Reading the image…'},
    'UNDERSTOOD': {'uz': '📝 <b>Men shunday tushundim:</b>\n<i>{text}</i>', 'ru': '📝 <b>Я понял так:</b>\n<i>{text}</i>',
                   'en': '📝 <b>Here is what I understood:</b>\n<i>{text}</i>'},
    'NO_SPEECH': {'uz': 'Ovozli xabarda nutqni ajrata olmadim. Iltimos, aniqroq gapirib qayta yuboring yoki yozib yuboring.',
                  'ru': 'Не удалось распознать речь. Пожалуйста, запишите сообщение чётче или напишите текстом.',
                  'en': 'I could not recognise the speech. Please record it more clearly or type your message.'},
    'TOO_BIG': {'uz': 'Fayl juda katta (20 MB dan ortiq). Iltimos, qisqaroq yozuv yoki skrinshot yuboring.',
                'ru': 'Файл слишком большой (больше 20 МБ). Пожалуйста, отправьте запись короче или скриншот.',
                'en': 'The file is too large (over 20 MB). Please send a shorter recording or a screenshot.'},
    'UNSUPPORTED': {'uz': 'Bu turdagi xabarni hali tushunmayman. Matn, ovozli xabar, audio yoki rasm yuboring.',
                    'ru': 'Такой тип сообщения пока не поддерживается. Отправьте текст, голосовое сообщение, аудио или изображение.',
                    'en': 'This message type is not supported yet. Please send text, a voice message, audio or an image.'},
    'ERROR': {'uz': 'Kechirasiz, texnik xatolik yuz berdi. Birozdan keyin qayta urinib koʻring.',
              'ru': 'Извините, произошла техническая ошибка. Попробуйте ещё раз чуть позже.',
              'en': 'Sorry, a technical error occurred. Please try again shortly.'},
    'ROLE_ASK': {
        'uz': '👤 <b>Bu vaziyatda siz kimsiz?</b>\nTanlov faqat shu murojaat uchun: javobni vaziyatingizga moslab, tezroq va aniqroq berishga yordam beradi.',
        'ru': '👤 <b>Кто вы в этой ситуации?</b>\nВыбор действует только для этого обращения и помогает дать более точный и быстрый ответ.',
        'en': '👤 <b>Who are you in this situation?</b>\nThis choice applies only to this appeal and helps give a faster, more accurate answer.'},
    'ROLE_CHOSEN': {'uz': '👤 Bu murojaatda: <b>{role}</b>', 'ru': '👤 В этом обращении: <b>{role}</b>', 'en': '👤 In this appeal: <b>{role}</b>'},
    'ROLES': {
        'uz': {'talaba': '🎓 Talaba', 'xodim': '👷 Xodim (ishchi)', 'tadbirkor': '💼 Tadbirkor', 'xaridor': '🛒 Xaridor (isteʼmolchi)', 'boshqa': '👤 Boshqa'},
        'ru': {'talaba': '🎓 Студент', 'xodim': '👷 Работник', 'tadbirkor': '💼 Предприниматель', 'xaridor': '🛒 Покупатель (потребитель)', 'boshqa': '👤 Другое'},
        'en': {'talaba': '🎓 Student', 'xodim': '👷 Employee', 'tadbirkor': '💼 Entrepreneur', 'xaridor': '🛒 Buyer (consumer)', 'boshqa': '👤 Other'},
    },
    'ANALYZING': {'uz': '⚖️ Qonun bazasidan (lex.uz) tegishli moddalarni qidiryapman va tahlil qilyapman… (10–15 soniya)',
                  'ru': '⚖️ Ищу нужные статьи в базе законов (lex.uz) и анализирую… (10–15 секунд)',
                  'en': '⚖️ Searching the law database (lex.uz) for relevant articles and analysing… (10–15 seconds)'},
    'ANALYSIS_FAILED': {'uz': 'Kechirasiz, hozir tahlil qilib boʻlmadi (AI xizmati band). Bir daqiqadan soʻng rolni qayta tanlang — tahlil qaytadan boshlanadi:',
                        'ru': 'Извините, сейчас не удалось выполнить анализ (сервис ИИ занят). Через минуту выберите роль снова — анализ начнётся заново:',
                        'en': 'Sorry, the analysis failed (the AI service is busy). In a minute, choose your role again to restart the analysis:'},
    'BTN_APP': {'uz': '📝 Ariza tayyorlash', 'ru': '📝 Подготовить заявление', 'en': '📝 Draft the application'},
    'BTN_ESC': {'uz': '📨 Idoraga murojaat yuborish (3 kalit)', 'ru': '📨 Отправить в орган (3 ключа)', 'en': '📨 Send to the authority (3 keys)'},
    'BTN_NEW': {'uz': '🆕 Yangi murojaat', 'ru': '🆕 Новое обращение', 'en': '🆕 New appeal'},
    'APP_WRITING': {'uz': '📝 Ariza matnini tayyorlayapman…', 'ru': '📝 Готовлю текст заявления…', 'en': '📝 Drafting the application…'},
    'APP_HEADER': {'uz': '📝 <b>Ariza loyihasi.</b> Matnni nusxalab, [qavs ichidagi] joylarni oʻzingiz toʻldiring:',
                   'ru': '📝 <b>Проект заявления.</b> Скопируйте текст и заполните места [в скобках]:',
                   'en': '📝 <b>Draft application</b> (in Uzbek, the state language). Copy it and fill in the [bracketed] fields:'},
    'APP_FOOTER': {
        'uz': 'ℹ️ Arizani yozma ravishda, shaxsan yoki tashkilotning rasmiy elektron manzili yoxud my.gov.uz orqali yuborishingiz mumkin. Nusxasini va qabul qilinganini tasdiqlovchi hujjatni saqlab qoʻying.',
        'ru': 'ℹ️ Заявление можно подать письменно, лично, на официальный электронный адрес организации или через my.gov.uz. Сохраните копию и документ, подтверждающий его приём.',
        'en': 'ℹ️ You can submit the application in writing, in person, to the organisation’s official e-mail or via my.gov.uz. Keep a copy and proof that it was received.'},
    'APP_FAILED': {'uz': 'Kechirasiz, ariza matnini hozir tayyorlab boʻlmadi. Bir daqiqadan soʻng «📝 Ariza tayyorlash» tugmasini qayta bosing.',
                   'ru': 'Извините, сейчас не удалось подготовить заявление. Через минуту нажмите «📝 Подготовить заявление» ещё раз.',
                   'en': 'Sorry, the application could not be drafted right now. Press “📝 Draft the application” again in a minute.'},
    'CASE_GONE': {'uz': 'Bu murojaat topilmadi. Vaziyatni qaytadan yuboring.', 'ru': 'Обращение не найдено. Отправьте ситуацию заново.',
                  'en': 'This appeal was not found. Please send your situation again.'},
    'WEBAPP_OPEN': {'uz': '📱 Ilovani ochish', 'ru': '📱 Открыть приложение', 'en': '📱 Open the app'},
    'WEBAPP_ESCALATE': {
        'uz': '📨 Murojaat #{id} ni idoraga yuborish uchun 3 kalitdan oʻting. Birinchi kalit — telefon raqamingizni tasdiqlash, u faqat shu chatda ishlaydi. Pastdagi tugmani bosing:',
        'ru': '📨 Чтобы отправить обращение #{id} в орган, пройдите 3 ключа. Первый — подтверждение номера телефона, он работает только в этом чате. Нажмите кнопку ниже:',
        'en': '📨 To send appeal #{id} to the authority, pass the 3 keys. The first key — confirming your phone number — works only in this chat. Press the button below:'},
    'ESC_ALREADY': {'uz': 'Bu murojaat allaqachon tekshiruvda yoki yuborilgan.', 'ru': 'Это обращение уже на проверке или отправлено.',
                    'en': 'This appeal is already under review or has been sent.'},
    'ESC_NOT_CONFIGURED': {'uz': 'Idoraga yuborish hali sozlanmagan (klinika guruhi ulanmagan). Ariza loyihasidan foydalaning.',
                           'ru': 'Отправка в орган пока не настроена (группа клиники не подключена). Воспользуйтесь проектом заявления.',
                           'en': 'Sending to the authority is not set up yet (the clinic group is not connected). Please use the draft application.'},
    'ESC_LIMIT': {'uz': 'Bir kunda {n} tadan ortiq murojaatni idoraga yuborib boʻlmaydi. Ertaga qayta urinib koʻring.',
                  'ru': 'Нельзя отправить в орган больше {n} обращений в день. Попробуйте завтра.',
                  'en': 'You cannot send more than {n} appeals a day to the authority. Please try again tomorrow.'},
    'K1_ASK': {'uz': '🔑 <b>1-kalit: shaxsni tasdiqlash.</b>\nIdoraga anonim murojaat yuborilmaydi. Pastdagi tugma orqali oʻz telefon raqamingizni yuboring.',
               'ru': '🔑 <b>Ключ 1: подтверждение личности.</b>\nАнонимные обращения в орган не отправляются. Отправьте свой номер телефона кнопкой ниже.',
               'en': '🔑 <b>Key 1: identity check.</b>\nAnonymous appeals are not sent to authorities. Share your own phone number with the button below.'},
    'K1_BUTTON': {'uz': '📱 Telefon raqamimni yuborish', 'ru': '📱 Отправить мой номер', 'en': '📱 Share my phone number'},
    'K1_NOT_OWN': {'uz': 'Faqat oʻzingizning raqamingizni pastdagi tugma orqali yuboring.', 'ru': 'Отправьте только свой номер — кнопкой ниже.',
                   'en': 'Please share only your own number using the button below.'},
    'K1_OK': {'uz': '✅ 1-kalit: telefon raqamingiz tasdiqlandi.', 'ru': '✅ Ключ 1: номер телефона подтверждён.', 'en': '✅ Key 1: your phone number is confirmed.'},
    'LIABILITY': {'uz': '⚠️ <b>Ogohlantirish.</b> Davlat organiga bila turib yolgʻon xabar berish qonunga koʻra javobgarlikka sabab boʻlishi mumkin. Murojaatdagi maʼlumotlar toʻgʻri ekanini tasdiqlaysizmi?',
                  'ru': '⚠️ <b>Предупреждение.</b> Заведомо ложное сообщение в государственный орган может повлечь ответственность по закону. Подтверждаете, что сведения в обращении верны?',
                  'en': '⚠️ <b>Warning.</b> Knowingly giving false information to a state body may lead to legal liability. Do you confirm the information in the appeal is true?'},
    'LIABILITY_BTN': {'uz': '✅ Tushundim, tasdiqlayman', 'ru': '✅ Понимаю, подтверждаю', 'en': '✅ I understand and confirm'},
    'K2_CHECKING': {'uz': '🔑 <b>2-kalit:</b> murojaatning izchilligi va dalillarini tekshiryapman…', 'ru': '🔑 <b>Ключ 2:</b> проверяю последовательность и доказательства…',
                    'en': '🔑 <b>Key 2:</b> checking consistency and evidence…'},
    'K2_LOW': {'uz': '🔑 2-kalit: ishonchlilik bali <b>{score}/100</b> — idoraga yuborish uchun yetarli emas.\nSabab: {reason}\n\n<b>Iltimos, aniqlashtiring:</b>\n{missing}\n\nVaziyatni toʻliqroq yozib, qayta yuboring.',
               'ru': '🔑 Ключ 2: балл достоверности <b>{score}/100</b> — недостаточно для отправки в орган.\nПричина: {reason}\n\n<b>Пожалуйста, уточните:</b>\n{missing}\n\nОпишите ситуацию подробнее и отправьте заново.',
               'en': '🔑 Key 2: credibility score <b>{score}/100</b> — not enough to send to the authority.\nReason: {reason}\n\n<b>Please clarify:</b>\n{missing}\n\nDescribe the situation in more detail and send it again.'},
    'K2_OK': {'uz': '✅ 2-kalit: ishonchlilik bali <b>{score}/100</b>.', 'ru': '✅ Ключ 2: балл достоверности <b>{score}/100</b>.', 'en': '✅ Key 2: credibility score <b>{score}/100</b>.'},
    'K3_SENT': {'uz': '🔑 <b>3-kalit:</b> murojaatingiz Yuridik klinika yuristiga tekshiruvga yuborildi. Yurist tasdiqlasa, masʼul idoraga yetkaziladi va sizga xabar beraman.',
                'ru': '🔑 <b>Ключ 3:</b> обращение передано на проверку юристу Юридической клиники. После одобрения оно будет направлено в ответственный орган, и я вам сообщу.',
                'en': '🔑 <b>Key 3:</b> your appeal has been sent to a Legal Clinic lawyer for review. Once approved, it will be forwarded to the responsible authority and I will let you know.'},
    'K3_APPROVED': {'uz': '✅ Murojaat #{id} yurist tomonidan tasdiqlandi va masʼul idoraga yuborildi.', 'ru': '✅ Обращение #{id} одобрено юристом и направлено в ответственный орган.',
                    'en': '✅ Appeal #{id} was approved by the lawyer and sent to the responsible authority.'},
    'K3_REJECTED': {'uz': 'Murojaat #{id} yurist tomonidan idoraga yuborilmadi. Ariza loyihasidan foydalanib oʻzingiz murojaat qilishingiz yoki Yuridik klinikaga yozishingiz mumkin.',
                    'ru': 'Юрист не направил обращение #{id} в орган. Вы можете подать его сами по проекту заявления или написать в Юридическую клинику.',
                    'en': 'The lawyer did not forward appeal #{id}. You can file it yourself using the draft application or contact the Legal Clinic.'},
    'K3_ASK': {'uz': 'Yurist murojaat #{id} boʻyicha aniqlashtirish soʻradi. Vaziyatni batafsilroq yozib, qayta yuboring.',
               'ru': 'Юрист запросил уточнения по обращению #{id}. Опишите ситуацию подробнее и отправьте заново.',
               'en': 'The lawyer asked for clarification on appeal #{id}. Please describe the situation in more detail and send it again.'},
    'REMINDER': {'uz': '🔔 Murojaat #{id} boʻyicha vaziyatingiz hal boʻldimi?', 'ru': '🔔 Ваша ситуация по обращению #{id} решилась?',
                 'en': '🔔 Has your situation with appeal #{id} been resolved?'},
    'CLOSE_YES': {'uz': '✅ Ha, yopish', 'ru': '✅ Да, закрыть', 'en': '✅ Yes, close it'},
    'CLOSE_NO': {'uz': 'Yoʻq, hal boʻlmadi', 'ru': 'Нет, не решилась', 'en': 'No, not resolved'},
    'CLOSED': {'uz': '✅ Murojaat yopildi. Yana yordam kerak boʻlsa, yozing.', 'ru': '✅ Обращение закрыто. Если понадобится помощь — пишите.',
               'en': '✅ The appeal is closed. Write any time you need help.'},
    'NOT_CLOSED': {'uz': 'Tushunarli. Murojaat ochiq qoladi; kerak boʻlsa, «📨 Idoraga murojaat yuborish» tugmasidan foydalaning.',
                   'ru': 'Понятно. Обращение остаётся открытым; при необходимости используйте кнопку «📨 Отправить в орган».',
                   'en': 'Understood. The appeal stays open; if needed, use the “📨 Send to the authority” button.'},
    'LEVELS': {
        'uz': {'oddiy': '🟢 Oddiy', 'muhim': '🟡 Muhim', 'jiddiy': '🔴 Jiddiy', 'xavf': '🚨 Xavf'},
        'ru': {'oddiy': '🟢 Обычная', 'muhim': '🟡 Важная', 'jiddiy': '🔴 Серьёзная', 'xavf': '🚨 Опасность'},
        'en': {'oddiy': '🟢 Routine', 'muhim': '🟡 Important', 'jiddiy': '🔴 Serious', 'xavf': '🚨 Danger'},
    },
    'H_SITUATION': {'uz': '📌 <b>Vaziyat:</b>', 'ru': '📌 <b>Ситуация:</b>', 'en': '📌 <b>Situation:</b>'},
    'H_RIGHTS': {'uz': '✅ <b>Huquqlaringiz:</b>', 'ru': '✅ <b>Ваши права:</b>', 'en': '✅ <b>Your rights:</b>'},
    'H_DUTIES': {'uz': '📋 <b>Nima qilishingiz kerak:</b>', 'ru': '📋 <b>Что нужно сделать:</b>', 'en': '📋 <b>What you should do:</b>'},
    'H_WHERE': {'uz': '🏛 <b>Qayerga murojaat qilish:</b>', 'ru': '🏛 <b>Куда обращаться:</b>', 'en': '🏛 <b>Where to apply:</b>'},
    'H_PROOF': {'uz': '🗂 <b>Dalillarni saqlang:</b>', 'ru': '🗂 <b>Сохраните доказательства:</b>', 'en': '🗂 <b>Keep the evidence:</b>'},
    'H_LAW': {'uz': '📚 <b>Qonun (lex.uz):</b>', 'ru': '📚 <b>Закон (lex.uz):</b>', 'en': '📚 <b>Law (lex.uz):</b>'},
    'H_ASK': {'uz': '<b>Aniqroq javob uchun yozing:</b>', 'ru': '<b>Для более точного ответа напишите:</b>', 'en': '<b>For a more precise answer, tell me:</b>'},
    'ARTICLE': {'uz': '{num}-modda', 'ru': 'ст. {num}', 'en': 'Art. {num}'},
    'AI_FALLBACK_WHY': {'uz': 'Vaziyatga tegishli boʻlishi mumkin — yurist tekshirsin', 'ru': 'Может относиться к ситуации — проверит юрист',
                        'en': 'May be relevant — to be checked by a lawyer'},
    'CMD': {
        'uz': {'start': 'Botni ishga tushirish', 'yangi': 'Yangi murojaat', 'til': 'Tilni oʻzgartirish', 'yordam': 'Qanday foydalanish',
               'maxfiylik': 'Shaxsiy maʼlumotlar va rozilik'},
        'ru': {'start': 'Запустить бота', 'yangi': 'Новое обращение', 'til': 'Сменить язык', 'yordam': 'Как пользоваться',
               'maxfiylik': 'Персональные данные и согласие'},
        'en': {'start': 'Start the bot', 'yangi': 'New appeal', 'til': 'Change language', 'yordam': 'How to use',
               'maxfiylik': 'Personal data and consent'},
    },
    'BOT_SHORT': {'uz': 'Vaziyatingizni yozing yoki ovoz yuboring: qonun asosida qayerga, qachon va qanday murojaat qilishni aytaman.',
                  'ru': 'Опишите ситуацию или отправьте голос: по закону подскажу, куда, когда и как обращаться.',
                  'en': 'Describe your situation or send a voice note: I will tell you where, when and how to apply, based on the law.'},
    'BOT_DESC': {
        'uz': ('Huquqiy Navigator — davlat tashkilotlariga murojaat qilishda yordamchingiz.\n\n'
               '• Vaziyatingizni matn, ovozli xabar yoki skrinshot bilan yuboring\n• Bot uni amaldagi qonun bilan solishtiradi (lex.uz)\n'
               '• Kimga, qayerga, qachon murojaat qilish va qanday dalil saqlashni aytadi\n• Ariza matnini tayyorlab beradi\n'
               '• Jiddiy murojaat Yuridik klinika yuristi tekshiruvidan oʻtadi\n\n'
               'Bu huquqiy maslahat emas, yakuniy baho yurist zimmasida. Hayotga xavf boʻlsa: 102 / 103.'),
        'ru': ('Правовой навигатор — помощник при обращении в государственные органы.\n\n'
               '• Отправьте ситуацию текстом, голосом или скриншотом\n• Бот сопоставит её с действующим законодательством (lex.uz)\n'
               '• Подскажет, куда, к кому и когда обращаться и какие доказательства сохранить\n• Подготовит текст заявления\n'
               '• Серьёзное обращение проверяет юрист Юридической клиники\n\n'
               'Это не юридическая консультация, окончательную оценку даёт юрист. При угрозе жизни: 102 / 103.'),
        'en': ('Legal Navigator helps you file appeals with state bodies in Uzbekistan.\n\n'
               '• Send your situation as text, voice or a screenshot\n• The bot compares it with current legislation (lex.uz)\n'
               '• It tells you where, to whom and when to apply and what evidence to keep\n• It drafts the application\n'
               '• Serious appeals are reviewed by a Legal Clinic lawyer\n\n'
               'This is not legal advice; the final assessment is up to a lawyer. In an emergency: 102 / 103.'),
    },
}
# Ilovaga oʻtish tugmasi va APP_FOOTER oxiriga ogohlantirish
for _l in LANGS:
    T['APP_FOOTER'][_l] = T['APP_FOOTER'][_l] + '\n\n' + _DISC[_l]
    T['HELP'][_l] = T['HELP'][_l] + '\n\n' + _DISC[_l]

# Qonun nomlari (bazada oʻzbekcha). Kartada foydalanuvchi tilida koʻrsatiladi.
LAW_NAMES = {
    'ru': {'MK': 'Трудовой кодекс', 'FK-1': 'Гражданский кодекс (ч. 1)', 'FK-2': 'Гражданский кодекс (ч. 2)', 'JK': 'Уголовный кодекс',
           'MJtK': 'Кодекс об административной ответственности', 'IHHQ': 'Закон «О защите прав потребителей»',
           'MurQ': 'Закон «Об обращениях физических и юридических лиц»'},
    'en': {'MK': 'Labour Code', 'FK-1': 'Civil Code (Part 1)', 'FK-2': 'Civil Code (Part 2)', 'JK': 'Criminal Code',
           'MJtK': 'Code of Administrative Liability', 'IHHQ': 'Law on Consumer Rights Protection',
           'MurQ': 'Law on Appeals of Individuals and Legal Entities'},
}


def norm(lang) -> str:
    """Telegram language_code yoki istalgan qiymat → uz | ru | en."""
    lang = (lang or '').lower()[:2]
    return lang if lang in LANGS else ('uz' if lang in ('', 'uz') else 'ru' if lang in ('kk', 'ky', 'tg', 'be', 'uk') else 'en')


def t(lang: str, key: str, **kw):
    v = T[key].get(lang if lang in LANGS else 'uz', T[key]['uz'])
    return v.format(**kw) if kw and isinstance(v, str) else v


def law_name(lang: str, abbr: str, default: str) -> str:
    return LAW_NAMES.get(lang, {}).get(abbr, default)
