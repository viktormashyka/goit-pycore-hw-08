from collections import UserDict
from datetime import datetime
from functools import wraps
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    # реалізація класу
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
              raise ValueError("phone number must be a string of 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            datetime_object = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(datetime_object)
        except ValueError:
            raise ValueError("invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу
    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)
        return f"Phone {phone} added."

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(phone)
                return f"Phone {phone} removed."
        return f"Phone {phone} not found."

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone)
                return f"Phone {old_phone} updated to {new_phone}."
        return f"Phone {old_phone} not found."
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return f"Phone {phone} not found."
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return f"Birthday {birthday} added."

    def __str__(self):
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    # реалізація класу
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, f"Contact {name} not found.")
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted."
        return f"Contact {name} not found."
    
    def get_upcoming_birthdays(self, book):
        upcoming_birthdays = []
        today = datetime.now().date()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday < 7:
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")})
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Enter the argument for the command: {e}"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid input. Please provide the correct information."
        except Exception as e:
            return f"An error occurred: {e}"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("name and phone number.")
    name, phone, *_ = args
    if name in book.data:
        record = book.find(name)
        message = f"Contact with name {name} updated."
    else:
        record = Record(name)
        message = f"Contact with name {name} added."
    if phone:
        record.add_phone(phone)
    book.add_record(record)
    return message

@input_error
def change_contact(args, book):
    if len(args) < 3:
        raise ValueError("name, old phone number, new phone number.")
    name, old_phone, new_phone, *_ = args
    if name not in book:
        raise KeyError
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Contact with name {name} changed."

@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError("name.")
    name = args[0]
    if name not in book:
        raise KeyError
    record = book.find(name)
    return f"Phones for {name}: {'; '.join(phone.value for phone in record.phones)}"

@input_error
def show_all(book):
    if not book:
        print("No contacts found")
    for name, record in book.data.items():
        print(record)

@input_error
def add_birthday(args, book):
    # реалізація
    if len(args) < 2:
        raise ValueError("name and date of birthday.")
    name, dob, *_ = args
    if name in book.data:
        record = book.data[name]
    else:
        record = Record(name)
    record.add_birthday(dob)
    book.add_record(record)

    return f"Birthday to contact with name {name} added."

@input_error
def show_birthday(args, book):
    # реалізація
    if len(args) < 1:
        raise ValueError("name.")
    name = args[0]
    if name not in book:
        raise KeyError
    record = book.find(name)
    return f"Birthday for {name}: {record.birthday}"

@input_error
def birthdays(book):
    # реалізація
    return book.get_upcoming_birthdays(book)

@input_error
def help():
    print("\thello - start dialog")
    print("\tadd <name> <phone> - add contact, require name and phone")
    print("\tchange <name> <old phone> <new phone> - change contact, require name, old phone and new phone")
    print("\tphone <name> - show phone, require name")
    print("\tall - show all contacts")
    print("\tadd-birthday <name> <date of birthday> - add birthday, require name and date of birthday")
    print("\tshow-birthday <name> - show birthday, require name")
    print("\tbirthdays - show birthdays next week")
    print("\texit or close - exit")

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            # реалізація
            print(add_birthday(args, book))
        elif command == "show-birthday":
            # реалізація
            print(show_birthday(args, book))
        elif command == "birthdays":
            # реалізація
            print(birthdays(book))
        elif command == "help" or "-h":
            help()
        else:
            print("Invalid command.")
        

if __name__ == "__main__":
    main()

#     # Приклад використання класів
#     # Створення нової адресної книги
#     book = AddressBook()

#     # Створення запису для John
#     john_record = Record("John")
#     john_record.add_phone("1234567890")
#     john_record.add_phone("5555555555")
#     john_record.add_birthday("30.07.2006")

#     # Додавання запису John до адресної книги
#     book.add_record(john_record)

#     # Створення та додавання нового запису для Jane
#     jane_record = Record("Jane")
#     jane_record.add_phone("9876543210")
#     jane_record.add_birthday("14.05.2011")
#     book.add_record(jane_record)

#     # Виведення всіх записів у книзі
#     for name, record in book.data.items():
#         print(record)

#     # Виведення днів народжень на найближчий тиждень
#     upcoming_birthdays = book.get_upcoming_birthdays()
#     print(upcoming_birthdays) 

#     # Знаходження та редагування телефону для John
#     john = book.find("John")
#     john.edit_phone("1234567890", "1112223333")

#     print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

#     # Пошук конкретного телефону у записі John
#     found_phone = john.find_phone("5555555555")
#     print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

#     # Видалення запису Jane
#     book.delete("Jane")