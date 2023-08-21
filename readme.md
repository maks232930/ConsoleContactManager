# Console Contact Manager

Программа для управления контактами в консоли.

## Описание

Console Contact Manager - это простая консольная программа, которая позволяет управлять списком контактов. Вы можете добавлять, редактировать, искать и просматривать контакты через командную строку.

## Функционал программы

1. **Просмотр контактов:** Отображает список контактов в виде таблицы с полями ID, Имя, Фамилия, Отчество, Организация, Рабочий телефон и Личный телефон.

2. **Добавление контакта:** Позволяет вводить данные нового контакта, такие как Имя, Фамилия, Отчество, Организация, Рабочий телефон и Личный телефон. Введенные данные сохраняются в файле `contacts.json`.

3. **Редактирование контакта:** Позволяет выбрать контакт по ID и изменить его данные, такие как Имя, Фамилия, Отчество, Организация, Рабочий телефон и Личный телефон.

4. **Поиск контактов:** Позволяет искать контакты по различным полям, таким как ID, Имя, Фамилия, Отчество, Организация, Рабочий телефон и Личный телефон. Отображает результаты поиска в виде таблицы.

## Использование

1. Убедитесь, что у вас установлен Python 3.x.

2. Клонируйте этот репозиторий на свой компьютер:
3. Перейдите в директорию проекта:
4. Создайте и активируйте виртуальное окружение (опционально, но рекомендуется):
python -m venv venv
source venv/bin/activate # На Linux/macOS<br>
venv\Scripts\activate # На Windows<br>
5. Установите зависимости: pip install -r requirements.txt
6. Запустите программу: python main.py