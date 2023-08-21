import json
import os
import re

from tabulate import tabulate

from models import ContactModel


class PhoneBook:
    FIELD_TYPES: dict = {
        'id': int,
        'first_name': str,
        'middle_name': str,
        'last_name': str,
        'organization': str,
        'work_phone': str | int,
        'personal_phone': str | int
    }

    TABLE_HEADERS: list[str] = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Организация', 'Рабочий телефон',
                                'Личный телефон']

    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.entries: list[ContactModel] = []

        self.load_contacts()
        self.next_id: int = self.get_next_id()

    def get_next_id(self) -> int:
        """
        Возвращает следующий доступный ID для нового контакта.

        Если в записной книжке уже есть контакты, возвращает максимальный ID + 1.
        Если записная книжка пуста, возвращает 1.
        """
        if self.entries:
            return max(contact.id for contact in self.entries) + 1
        return 1

    def validate_contact(self, contact: dict) -> bool:
        """
        Проверяет валидность данных контакта.

        Принимает словарь с данными контакта и проверяет, соответствуют ли они ожидаемым типам данных
        и обязательным полям. Возвращает True, если данные валидны, и False в противном случае.
        """
        if len(contact) != len(self.FIELD_TYPES):
            return False
        for contact_key, contact_value in contact.items():
            if contact_key not in self.FIELD_TYPES or not isinstance(contact_value, self.FIELD_TYPES[contact_key]):
                return False
        return True

    def sort_contacts(self) -> None:
        """
        Сортирует список контактов по ID.

        Изменяет порядок контактов в списке, сортируя их по возрастанию ID.
        """
        self.entries.sort(key=lambda contact: contact.id)

    def save_contact(self) -> None:
        """
        Сохраняет список контактов в файл 'contacts.json'.

        Преобразует список контактов в формат JSON и записывает его в файл 'contacts.json'.
        """
        with open(self.filename, 'w') as file:
            contacts_json: list[dict] = [item.model_dump() for item in self.entries]
            json.dump(contacts_json, file, indent=4)

    def validate_contacts(self, json_data: list[dict]) -> list[dict]:
        """
        Проверяет и корректирует валидность данных всех контактов.

        Принимает список словарей с данными контактов в формате JSON. Проверяет валидность данных
        каждого контакта, убирает дубликаты и корректирует ID в случае дублирования.
        Возвращает список валидных и корректных контактов.
        """
        result_data: list[dict] = []
        invalid_data: list[dict] = []
        processed_ids: list = []

        for contact in json_data:
            valid: bool = True
            if len(contact) == len(self.FIELD_TYPES):
                for contact_key, contact_value in contact.items():
                    if (contact_key not in self.FIELD_TYPES or not isinstance(contact_value,
                                                                              self.FIELD_TYPES[contact_key])):
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
            max_id = max(item['id'] for item in invalid_data)
            for index, contact in enumerate(invalid_data, start=1):
                contact['id'] = int(max_id + index)
                result_data.append(contact)

        return result_data

    def load_contacts(self) -> None:
        """
        Загружает контакты из файла 'contacts.json' в список.

        Если файл существует, читает из него данные контактов, проверяет их валидность и загружает
        в список контактов.
        """
        if os.path.exists(self.filename):
            with open(self.filename) as json_file:
                contacts_json: list[dict] = json.load(json_file)
            result_contacts: list[dict] = self.validate_contacts(contacts_json)
            self.entries.extend([ContactModel(**contact) for contact in result_contacts])

    def add_contact(self) -> None:
        """
        Добавляет новый контакт в записную книжку.

        Запрашивает у пользователя информацию о контакте и проверяет её на валидность. Если данные валидны,
        создаёт экземпляр класса ContactModel и добавляет его в список контактов. Затем сохраняет контакты
        в файл.
        """
        first_name: str = input('Имя: ')
        last_name: str = input('Фамилия: ')
        middle_name: str = input('Отчество: ')
        organization: str = input('Организация: ')
        work_phone: str = input('Рабочий телефон: ')
        personal_phone: str = input('Личный телефон: ')

        contact_data: dict = {
            'id': self.next_id,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'organization': organization,
            'work_phone': work_phone,
            'personal_phone': personal_phone
        }

        if self.validate_contact(contact_data):
            self.entries.append(ContactModel(**contact_data))
            self.save_contact()
            self.next_id += 1
            print('\nКонтакт успешно добавлен')
        else:
            print('\nДанные неверны')

    def edit_contact(self):
        """
        Позволяет пользователю изменить информацию о существующем контакте.

        Пользователь вводит номер контакта, затем программа выводит информацию о контакте и предлагает внести
        изменения. После внесения изменений, обновляет информацию о контакте и сохраняет изменения.
        """
        while True:
            contact_id: int | str = input('Введите номер контакта, или "q" для выхода: ')
            if contact_id.lower() == 'q':
                break
            elif contact_id.isdigit():
                for contact in self.entries:
                    if contact.id == int(contact_id):
                        print(tabulate([contact.model_dump_table()], headers=self.TABLE_HEADERS, tablefmt='fancy_grid'))
                        new_first_name: str = input(
                            f'Имя (по умолчанию: {contact.first_name}): ') or contact.first_name
                        new_last_name: str = input(
                            f'Фамилия (по умолчанию: {contact.last_name}): ') or contact.last_name
                        new_middle_name: str = input(
                            f'Отчество (по умолчанию: {contact.middle_name}): ') or contact.middle_name
                        new_organization: str = input(
                            f'Организация (по умолчанию: {contact.organization}): ') or contact.organization
                        new_work_phone: str = input(
                            f'Рабочий телефон (по умолчанию: {contact.work_phone}): ') or contact.work_phone
                        new_personal_phone: str = input(
                            f'Личный телефон (по умолчанию: {contact.personal_phone}): ') or contact.personal_phone

                        updated_contact: ContactModel = contact.model_copy(
                            update={
                                'first_name': new_first_name,
                                'last_name': new_last_name,
                                'middle_name': new_middle_name,
                                'organization': new_organization,
                                'work_phone': new_work_phone,
                                'personal_phone': new_personal_phone
                            }
                        )

                        self.entries.remove(contact)
                        self.entries.append(updated_contact)
                        self.sort_contacts()
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
        new_text: str = re.sub(r'[^0-9,]', '', user_input)
        fields: list[int] = [int(i) for i in new_text.split(',') if i != '' and int(i) <= 7]

        return fields

    @staticmethod
    def _get_search_values(fields: list[int]) -> dict:
        """
        Запрашивает у пользователя значения для полей поиска.

        Принимает список номеров полей, для которых нужно ввести значения. Запрашивает у пользователя
        соответствующие значения и возвращает словарь с введенными значениями.
        """
        fields_values: dict = {}

        for field in fields:
            if field == 1:
                contact_id: str = input('Введите id: ').strip()
                if contact_id.isdigit():
                    fields_values['id'] = int(contact_id)
            elif field == 2:
                contact_first_name: str = input('Введите имя: ').strip()
                if contact_first_name:
                    fields_values['first_name'] = contact_first_name
            elif field == 3:
                contact_last_name: str = input('Введите фамилию: ').strip()
                if contact_last_name:
                    fields_values['last_name'] = contact_last_name
            elif field == 4:
                contact_middle_name: str = input('Введите отчество: ').strip()
                if contact_middle_name:
                    fields_values['middle_name'] = contact_middle_name
            elif field == 5:
                contact_organization: str = input('Введите организацию: ').strip()
                if contact_organization:
                    fields_values['organization'] = contact_organization
            elif field == 6:
                contact_work_phone: str = input('Введите рабочий телефон: ').strip()
                if contact_work_phone:
                    fields_values['work_phone'] = contact_work_phone
            elif field == 7:
                contact_personal_phone: str = input('Введите личный телефон: ').strip()
                if contact_personal_phone:
                    fields_values['personal_phone'] = contact_personal_phone

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

                for contact in self.entries:
                    match: bool = True
                    for field, value in fields_values.items():
                        if field == 'id':
                            if contact.id != value:
                                match = False
                                break
                        elif field == 'first_name':
                            if contact.first_name.lower() != value.lower():
                                match = False
                                break
                        elif field == 'last_name':
                            if contact.last_name.lower() != value.lower():
                                match = False
                                break
                        elif field == 'middle_name':
                            if contact.middle_name.lower() != value.lower():
                                match = False
                                break
                        elif field == 'organization':
                            if contact.organization.lower() != value.lower():
                                match = False
                                break
                        elif field == 'work_phone':
                            if contact.work_phone != value:
                                match = False
                                break
                        elif field == 'personal_phone':
                            if contact.personal_phone != value:
                                match = False
                                break
                    if match:
                        table_data.append(contact.model_dump_table())
                if table_data:
                    print(tabulate(table_data, headers=self.TABLE_HEADERS, tablefmt='fancy_grid'))
                    break
                else:
                    print('Совпадение не найдено')
                    break

            else:
                print('Таких полей нет')
                continue

    def show_display_contacts(self, page_size: int = 2) -> None:
        """
        Отображает список контактов в виде таблицы на нескольких страницах.

        Выводит список контактов в виде таблицы с заданным количеством контактов на странице. Пользователь
        может переходить между страницами, просматривая все контакты.
        """
        page: int = 1
        total_pages: int = (len(self.entries) + page_size - 1) // page_size

        while True:
            print(f'\nСтраница {page}/{total_pages}')

            start_index: int = (page - 1) * page_size
            end_index: int = start_index + page_size

            table_data: list = []
            for index, contact in enumerate(self.entries[start_index:end_index], start=start_index):
                table_data.append(contact.model_dump_table())

            print(tabulate(table_data, headers=self.TABLE_HEADERS, tablefmt='fancy_grid'))
            user_input: str = input(
                "\nНажмите 'n' для перехода на следующую страницу, 'b' для перехода на преведущую страницу, 'q' для выхода: ")
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 'n':
                page = (page % total_pages) + 1
            elif user_input.lower() == 'b':
                page = (page - 2) % total_pages + 1


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
        print('5. Выход')
        choice: str = input('Введите цифру: ')

        if choice == '1':
            contacts.show_display_contacts(page_size=10)
        elif choice == '2':
            contacts.add_contact()
        elif choice == '3':
            contacts.edit_contact()
        elif choice == '4':
            contacts.search_contact()
        elif choice == '5':
            break


if __name__ == '__main__':
    main()
