import telebot
import psycopg2
from telebot.util import quick_markup
from random import shuffle

# Подключение к базе данных
conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="Ak200213!",
    host="localhost",
    port="5432"
)

# Инициализация бота
bot = telebot.TeleBot("7016352548:AAHwqc4Oz-kSZYKdYn13VN6NyUq6QgPy6Os")

# --- Обработчики ---


@bot.message_handler(commands=['start'])
def start(message):
    # Добавление пользователя в БД
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (message.chat.id, message.from_user.username),
        )
        conn.commit()

    # Приветственное сообщение
    markup = quick_markup({
        "Переводчик": {"callback_data": "game_start"},
        "Словарь": {"callback_data": "dictionary"}
    }, row_width=2)
    bot.send_message(
        message.chat.id,
        "Привет 👋 Я твой персональный Переводчик. Мы будем практиковаться в переводе английских слов. \n\n"
        "Кнопка 'Переводчик' откроет набор случайных слов с одним правильным переводом. \n\n"
        "Кнопка 'Словарь' предоставит возможность добавлять или удалять слова из базы.",
        reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    # Добавление пользователя в БД
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (message.chat.id, message.from_user.username),
        )
        conn.commit()

    # Приветственное сообщение
    markup = quick_markup({
        "Переводчик": {"callback_data": "game_start"},
        "Словарь": {"callback_data": "dictionary"}
    }, row_width=2)
    bot.send_message(
        message.chat.id,
        "Кнопка 'Переводчик' откроет набор случайных слов с одним правильным переводом. \n\n"
        "Кнопка 'Словарь' предоставит возможность добавлять или удалять слова из базы.",
        reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    # Добавление пользователя в БД
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
            (message.chat.id, message.from_user.username),
        )
        conn.commit()

    # Приветственное сообщение
    markup = quick_markup({
        "Переводчик": {"callback_data": "game_start"},
        "Словарь": {"callback_data": "dictionary"}
    }, row_width=2)
    bot.send_message(
        message.chat.id,
        "Кнопка 'Переводчик' откроет набор случайных слов с одним правильным переводом. \n\n"
        "Кнопка 'Словарь' предоставит возможность добавлять или удалять слова из базы.",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "game_start":
        send_word(call.message)
    elif call.data == "dictionary":
        show_dictionary_menu(call.message)
    elif call.data == "show_words":
        show_all_words(call.message)
    elif call.data == "add_word":
        add_word(call.message)
    elif call.data == "delete_word":
        delete_word(call.message)
    elif call.data.startswith("check_"):
        check_answer(call)
    elif call.data == "start":
        # Возвращаемся к стартовому сообщению
        start(call.message)


def send_word(message):
    chat_id = message.chat.id
    with conn.cursor() as cur:
        cur.execute(
            "SELECT word_id, russian FROM words ORDER BY RANDOM() LIMIT 1")
        word_id, russian = cur.fetchone()

    # Получаем 3 случайных слова (отличных от выбранного)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT english FROM words WHERE word_id != %s ORDER BY RANDOM() LIMIT 3",
            (word_id,),
        )
        wrong_options = [row[0] for row in cur.fetchall()]

    # Получаем правильный вариант перевода
    with conn.cursor() as cur:
        cur.execute("SELECT english FROM words WHERE word_id = %s", (word_id,))
        correct_option = cur.fetchone()[0]

    # Создаем список вариантов ответа и перемешиваем его
    options = wrong_options + [correct_option]
    shuffle(options)

    # Создаем клавиатуру с вариантами ответа
    markup = quick_markup({
        options[0]: {"callback_data": f"check_{options[0]}_{word_id}"},
        options[1]: {"callback_data": f"check_{options[1]}_{word_id}"},
        options[2]: {"callback_data": f"check_{options[2]}_{word_id}"},
        options[3]: {"callback_data": f"check_{options[3]}_{word_id}"},
        "Дальше": {"callback_data": "game_start"},
        "Главное меню": {"callback_data": "start"}
    }, row_width=2)

    bot.send_message(
        chat_id,
        f"Переведите слово: *{russian}*",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_dictionary_menu(message):
    markup = quick_markup({
        "Показать все слова": {"callback_data": "show_words"},
        "Добавить слово": {"callback_data": "add_word"},
        "Удалить слово": {"callback_data": "delete_word"},
        "Главное меню": {"callback_data": "start"}
    }, row_width=1)
    bot.send_message(message.chat.id, "Меню словаря", reply_markup=markup)


def show_all_words(message):
    user_id = message.chat.id
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT w.english, w.russian
            FROM words w
            JOIN user_words uw ON w.word_id = uw.word_id
            WHERE uw.user_id = %s
            """,
            (user_id,),
        )
        words = cur.fetchall()

    if words:
        word_list = "\n".join(
            [f"{i + 1}. {english} - {russian}" for i, (english, russian) in enumerate(words)])
        bot.send_message(message.chat.id, f"Ваши слова:\n{word_list}")
    else:
        bot.send_message(message.chat.id, "У вас пока нет слов в словаре.")


def add_word(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите слово на английском и его перевод на русском через дефис.\n\n"
        "Например: *hello-привет*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_word_input)


def process_word_input(message):
    try:
        english, russian = message.text.split("-")
        english = english.strip().lower()
        russian = russian.strip()
        user_id = message.chat.id

        with conn.cursor() as cur:
            # Проверяем, есть ли уже такое слово в базе words
            cur.execute("SELECT word_id FROM words WHERE english = %s", (english,))
            result = cur.fetchone()

            if result:
                word_id = result[0]
                # Проверяем, есть ли слово у пользователя в user_words
                cur.execute("SELECT 1 FROM user_words WHERE user_id = %s AND word_id = %s", (user_id, word_id))
                if cur.fetchone():
                    bot.send_message(message.chat.id, "Такое слово уже есть в вашем словаре.")
                else:
                    # Добавляем слово в user_words для текущего пользователя
                    cur.execute("INSERT INTO user_words (user_id, word_id) VALUES (%s, %s)", (user_id, word_id))
                    conn.commit()
                    bot.send_message(message.chat.id, f"Слово *{english} - {russian}* добавлено в ваш словарь.",
                                     parse_mode="Markdown")
            else:
                # Добавляем слово в таблицу words
                cur.execute("INSERT INTO words (english, russian) VALUES (%s, %s)", (english, russian))
                conn.commit()
                # Достаём id только что добавленного слова
                cur.execute("SELECT word_id FROM words WHERE english = %s", (english,))
                word_id = cur.fetchone()[0]
                # Добавляем связь в таблицу user_words
                cur.execute("INSERT INTO user_words (user_id, word_id) VALUES (%s, %s)", (user_id, word_id))
                conn.commit()
                bot.send_message(message.chat.id, f"Слово *{english} - {russian}* добавлено в ваш словарь.",
                                 parse_mode="Markdown")

    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат ввода. Пожалуйста, введите слово и перевод через дефис.")


def delete_word(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите слово на английском, которое хотите удалить из словаря:"
    )
    bot.register_next_step_handler(msg, process_word_deletion)


def process_word_deletion(message):
    english_word = message.text.strip().lower()

    with conn.cursor() as cur:
        # Удаляем слово из таблицы user_words
        cur.execute("DELETE FROM user_words WHERE word_id IN (SELECT word_id FROM words WHERE english = %s)", (english_word,))

        # Удаляем слово из таблицы words
        cur.execute("DELETE FROM words WHERE english = %s", (english_word,))
        conn.commit()

        if cur.rowcount > 0:
            bot.send_message(
                message.chat.id,
                f"Слово *{english_word}* удалено из словаря.",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"Слово *{english_word}* не найдено в словаре.",
                parse_mode="Markdown"
            )


def check_answer(call):
    user_answer, word_id = call.data.split("_")[1:]
    word_id = int(word_id)
    with conn.cursor() as cur:
        cur.execute("SELECT english FROM words WHERE word_id = %s", (word_id,))
        correct_answer = cur.fetchone()[0]

    if user_answer.lower() == correct_answer.lower():
        bot.answer_callback_query(call.id, "Верно!")
    else:
        bot.answer_callback_query(call.id, "Неверно, попробуй еще раз!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def process_word_deletion_callback(call):  # Изменил имя функции для ясности
    word_id = int(call.data.split("_")[1])
    user_id = call.message.chat.id

    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM user_words WHERE user_id = %s AND word_id = %s",
            (user_id,
             word_id))
        conn.commit()

    bot.answer_callback_query(call.id, "Слово удалено из вашего словаря.")


# Запуск бота
bot.polling()
