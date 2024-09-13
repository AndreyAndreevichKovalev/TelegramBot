-- Создание таблицы users
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT
);

-- Создание таблицы words
CREATE TABLE words (
    word_id SERIAL PRIMARY KEY,
    english TEXT UNIQUE,
    russian TEXT
);

-- Создание таблицы user_words
CREATE TABLE user_words (
    user_id BIGINT REFERENCES users(user_id),
    word_id INTEGER REFERENCES words(word_id),
    PRIMARY KEY (user_id, word_id)
);

-- Заполнение таблицы words начальными данными
INSERT INTO words (english, russian) VALUES
('red', 'красный'),
('blue', 'синий'),
('green', 'зеленый'),
('yellow', 'желтый'),
('black', 'черный'),
('white', 'белый'),
('I', 'я'),
('you', 'ты'),
('he', 'он'),
('she', 'она');