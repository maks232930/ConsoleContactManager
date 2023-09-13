import json
import os
import re

from tabulate import tabulate

from models import ContactModel


class PhoneBook:
    _FIELD_TYPES: dict = {
        'id': int,
        'first_name': str,
        'last_name': str,
        'middle_name': str,
        'organization': str,
        'work_phone': str,
        'personal_phone': str
    }

    _TABLE_HEADERS: list[str] = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Организация', 'Рабочий телефон',
                                 'Личный телефон']

    def __init__(self, filename: str) -> None:
        self._filename: str = filename
        self._entries: list[ContactModel] = []

        self._load_contacts()
        self._next_id: int = self._get_next_id()

    def _get_next_id(self) -> int:
        """
        Возвращает следующий доступный ID для нового контакта.

        Если в записной книжке уже есть контакты, возвращает максимальный ID + 1.
        Если записная книжка пуста, возвращает 1.
        """
        if self._entries:
            return max(contact.id for contact in self._entries) + 1
        return 1

    def _print_tabulate(self, table_data: list) -> None:
        print(tabulate(table_data, headers=self._TABLE_HEADERS, tablefmt='fancy_grid'))

    def _validate_contact(self, contact: dict) -> bool:
        """
        Проверяет валидность данных контакта.

        Принимает словарь с данными контакта и проверяет, соответствуют ли они ожидаемым типам данных
        и обязательным полям. Возвращает True, если данные валидны, и False в противном случае.
        """
        if len(contact) != len(self._FIELD_TYPES):
            return False
        for contact_key, contact_value in contact.items():
            if contact_key not in self._FIELD_TYPES or not isinstance(contact_value, self._FIELD_TYPES[contact_key]):
                return False
        return True

    def _sort_contacts(self) -> None:
        """
        Сортирует список контактов по ID.

        Изменяет порядок контактов в списке, сортируя их по возрастанию ID.
        """
        self._entries.sort(key=lambda contact: contact.id)

    def save_contact(self) -> None:
        """
        Сохраняет список контактов в файл 'self.filename'.

        Преобразует список контактов в формат JSON и записывает его в файл из 'self.filename'.
        """
        with open(self._filename, 'w') as file:
            contacts_json: list[dict] = [item.model_dump() for item in self._entries]
            json.dump(contacts_json, file, indent=4)

    def _validate_contacts(self, json_data: list[dict]) -> list[dict]:
        """
        Проверяет и корректирует валидность данных всех контактов.

        Принимает список словарей с данными контактов в формате JSON. Проверяет валидность данных
        каждого контакта, убирает дубликаты и корректирует ID в случае дублирования.
        Возвращает список валидных и корректных контактов.
        """
        result_data: list[dict] = []
        invalid_data: list[dict] = []
        processed_ids: list[int] = []

        for contact in json_data:
            valid: bool = True
            if len(contact) == len(self._FIELD_TYPES):
                for contact_key, contact_value in contact.items():
                    if (contact_key not in self._FIELD_TYPES or not isinstance(contact_value,
                                                                               self._FIELD_TYPES[contact_key])):
                        valid = False
                        break
            else:
                continue

            if valid:
                if contact['id'] not in processed_ids:
                    result_data.append(contact)
                    processed_ids.append(contact['id'])
                else:
                    invalid_data.append(contact)

        if invalid_data:
            max_id: int = max(processed_ids)
            for index, contact in enumerate(invalid_data, start=1):
                contact['id'] = int(max_id + index)
                result_data.append(contact)

        return result_data

    def _load_contacts(self) -> None:
        """
        Загружает контакты из файла 'contacts.json' в список.

        Если файл существует, читает из него данные контактов, проверяет их валидность и загружает
        в список контактов.
        """
        if os.path.exists(self._filename):
            with open(self._filename) as json_file:
                contacts_json: list[dict] = json.load(json_file)
            result_contacts: list[dict] = self._validate_contacts(contacts_json)
            self._entries.extend([ContactModel(**contact) for contact in result_contacts])

    def remove_contact(self) -> None:
        """
        Удаляет контакт из записной книжки по его ID.

        Запрашивает у пользователя ввод ID контакта, который нужно удалить. Если контакт с указанным ID существует,
        удаляет его из записной книжки и сохраняет изменения. Если контакт не найден или введен неверный формат ID,
        выводит соответствующие сообщения.

        """
        contact_id: str = input('Введите id: ').strip()
        if contact_id.isdigit():
            contact = self._get_contact_by_id(int(contact_id))
            if contact:
                self._entries.remove(contact)
                self.save_contact()
                print('Контакт успешно удален')
            else:
                print('Такого контакта нет')
        else:
            print('Неверный формат')

    def add_contact(self) -> None:
        """
        Добавляет новый контакт в записную книжку.

        Запрашивает у пользователя информацию о контакте и проверяет её на валидность. Если данные валидны,
        создаёт экземпляр класса ContactModel и добавляет его в список контактов. Затем сохраняет контакты
        в файл.
        """
        contact_data = {
            'id': self._next_id,
            'first_name': input('Имя: '),
            'last_name': input('Фамилия: '),
            'middle_name': input('Отчество: '),
            'organization': input('Организация: '),
            'work_phone': input('Рабочий телефон: '),
            'personal_phone': input('Личный телефон: ')
        }

        if self._validate_contact(contact_data):
            self._entries.append(ContactModel(**contact_data))
            self.save_contact()
            self._next_id += 1
            print('\nКонтакт успешно добавлен')
        else:
            print('\nДанные неверны')

    @staticmethod
    def _get_contact_data(contact: ContactModel) -> dict:
        """
        Получает новые данные для контакта от пользователя.

        Метод запрашивает у пользователя новые данные для существующего контакта, включая имя, фамилию, отчество,
        организацию, рабочий и личный телефон. Если пользователь не вводит новое значение, используется текущее
        значение из контакта.
        """

        return {
            'first_name': input(f'Имя (по умолчанию: {contact.first_name}): ').strip() or contact.first_name,
            'last_name': input(f'Фамилия (по умолчанию: {contact.last_name}): ').strip() or contact.last_name,
            'middle_name': input(f'Отчество (по умолчанию: {contact.middle_name}): ').strip() or contact.middle_name,
            'organization': input(
                f'Организация (по умолчанию: {contact.organization}): ').strip() or contact.organization,
            'work_phone': input(
                f'Рабочий телефон (по умолчанию: {contact.work_phone}): ').strip() or contact.work_phone,
            'personal_phone': input(
                f'Личный телефон (по умолчанию: {contact.personal_phone}): ').strip() or contact.personal_phone
        }

    def _get_contact_by_id(self, contact_id: int) -> ContactModel | None:
        """
        Возвращает контакт по его ID.
        """
        for contact in self._entries:
            if contact.id == contact_id:
                return contact

    def edit_contact(self) -> None:
        """
        Позволяет пользователю изменить информацию о существующем контакте.

        Пользователь вводит номер контакта, затем программа выводит информацию о контакте и предлагает внести
        изменения. После внесения изменений, обновляет информацию о контакте и сохраняет изменения.
        """
        while True:
            contact_id: str = input('Введите номер контакта, или "q" для выхода: ')
            if contact_id.lower() == 'q':
                break
            elif contact_id.isdigit():
                contact = self._get_contact_by_id(int(contact_id))
                if contact:
                    self._print_tabulate([contact.model_dump_table()])

                    updated_contact: ContactModel = contact.model_copy(
                        update=self._get_contact_data(contact)
                    )
                    self._entries.remove(contact)
                    self._entries.append(updated_contact)
                    self._sort_contacts()
                    self.save_contact()
                    print('\nКонтакт успешно изменен')
                    break
                else:
                    print('\nТакого контакта нет')
                    break
            else:
                print('\nНеверный формат')
                continue

    @staticmethod
    def _get_search_fields() -> list[int]:
        """
        Запрашивает у пользователя номера полей для поиска.

        Выводит список доступных полей для поиска и позволяет пользователю выбрать поля, по которым
        он хочет выполнить поиск. Возвращает список выбранных номеров полей.
        """
        print("""Выберите по каким полям искать (через запятую):
            1: id,
            2: имя,
            3: фамилия,
            4: отчество,
            5: организация,
            6: рабочий телефон,
            7: личный телефон"""
              )
        user_input: str = input('Введите номера через запятую: ')
        new_text: str = re.sub(r'[^1-7,]', '', user_input)
        fields: list[int] = list(set(int(i) for i in new_text.split(',') if i.isdigit() and 1 <= int(i) <= 7))

        return fields

    def _get_search_values(self, fields: list[int]) -> dict:
        """
        Запрашивает у пользователя значения для полей поиска.

        Принимает список номеров полей, для которых нужно ввести значения. Запрашивает у пользователя
        соответствующие значения и возвращает словарь с введенными значениями.
        """
        fields_values: dict = {}
        contact_headers: list[str] = list(self._FIELD_TYPES.keys())

        for field in fields:
            user_input: str = input(f'Введите {self._TABLE_HEADERS[field - 1]}: ').strip()
            if user_input:
                fields_values[contact_headers[field - 1]] = user_input

        return fields_values

    def search_contact(self) -> None:
        """
        Позволяет пользователю выполнять поиск контактов по различным полям.

        Пользователь выбирает поля, по которым будет выполняться поиск, и вводит значения для этих полей.
        Программа выводит список контактов, удовлетворяющих заданным критериям поиска.
        """
        while True:
            fields: list[int] = self._get_search_fields()
            if fields:
                fields_values: dict = self._get_search_values(fields)
                table_data: list = []

                for contact in self._entries:
                    match: bool = True
                    for field, value in fields_values.items():
                        if field == 'id':
                            if str(contact.id) != value:
                                match = False
                                break
                        else:
                            if getattr(contact, field).lower() != value.lower():
                                match = False
                                break
                    if match:
                        table_data.append(contact.model_dump_table())
                if table_data:
                    self._print_tabulate(table_data)
                    break
                else:
                    print('\nСовпадение не найдено')
                    break

            else:
                print('Таких полей нет')
                continue

    def show_display_contacts(self, page_size: int = 10) -> None:
        """
        Отображает список контактов в виде таблицы на нескольких страницах.

        Выводит список контактов в виде таблицы с заданным количеством контактов на странице. Пользователь
        может переходить между страницами, просматривая все контакты.
        """

        page: int = 1
        total_pages: int = (len(self._entries) + page_size - 1) // page_size

        while True:
            try:
                print(f'\nСтраница {page}/{total_pages}')

                start_index: int = (page - 1) * page_size
                end_index: int = start_index + page_size

                table_data: list = []
                for index, contact in enumerate(self._entries[start_index:end_index], start=start_index):
                    table_data.append(contact.model_dump_table())

                self._print_tabulate(table_data)
                print(
                    "Для перехода на следующую страницу, нажмите 'n'. Для перехода на предыдущую страницу, нажмите 'b'. Для выхода, нажмите 'q'. Чтобы перейти на конкретную страницу, укажите её номер.")

                user_input: str = input(
                    "\nВведите: ")
                if user_input.lower() == 'q':
                    break
                elif user_input.lower() == 'n':
                    page = (page % total_pages) + 1
                elif user_input.lower() == 'b':
                    page = (page - 2) % total_pages + 1
                elif user_input.isdigit():
                    if 1 <= int(user_input) <= total_pages:
                        page = int(user_input)
                    else:
                        print('Такой страницы нет!')
                else:
                    print("Неправильный формат!")
            except ZeroDivisionError:
                print('У вас одна страница')
                continue


def main() -> None:
    """
    Основная функция для запуска консольной программы управления контактами.
    """
    contacts: PhoneBook = PhoneBook('contacts.json')

    while True:
        print('\nЗаписная книжка:')
        print('1. Показать контакты')
        print('2. Добавить контакт')
        print('3. Изменить контакт')
        print('4. Поиск контактов')
        print('5. Удалить контакт')
        print('6. Выход')
        choice: str = input('Введите цифру: ')

        if choice == '1':
            contacts.show_display_contacts()
        elif choice == '2':
            contacts.add_contact()
        elif choice == '3':
            contacts.edit_contact()
        elif choice == '4':
            contacts.search_contact()
        elif choice == '5':
            contacts.remove_contact()
        elif choice == '6':
            contacts.save_contact()
            break


if __name__ == '__main__':
    main()
