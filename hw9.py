import pickle
from collections import UserDict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class View(ABC):
    @abstractmethod
    def display_message(self, message: str):
        pass

    @abstractmethod
    def display_contacts(self, contacts: list):
        pass

    @abstractmethod
    def display_help(self, commands: dict):
        pass

class ConsoleView(View):
    def display_message(self, message: str):
        print(message)

    def display_contacts(self, contacts: list):
        if not contacts:
            print("No contacts found.")
        else:
            for contact in contacts:
                print(contact)

    def display_help(self, commands: dict):
        print("Available commands:")
        for command, description in commands.items():
            print(f"{command}: {description}")



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid phone number. Should contain 10 digits.")
        super().__init__(value)

    @staticmethod
    def is_valid(value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")
        super().__init__(value)

    @staticmethod
    def is_valid(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("The phone is absent")

    def edit_phone(self, old_phone, new_phone):
        if not Phone.is_valid(new_phone):
            raise ValueError("Invalid number. Should contain 10 digits.")
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("The old phone is not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday.value if self.birthday else "Birthday not set."

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        birthday = self.show_birthday()
        return f"{self.name.value}: {phones}; Birthday: {birthday}"


class AddressBook(UserDict):
    def __init__(self, view=None):
        super().__init__()
        self.view = view or ConsoleView()

    def add_record(self, record):
        self.data[record.name.value] = record
        self.view.display_message(f"Contact {record.name.value} added successfully!")

    def find(self, name):
        return self.data.get(name)

    def show_all(self):
        if not self.data:
            self.view.display_message("No contacts found.")
        else:
            self.view.display_contacts([str(record) for record in self.data.values()])

    def show_help(self):
        commands = {
            "add": "Add a new contact",
            "change": "Change an existing contact",
            "phone": "Show phones of a contact",
            "all": "Show all contacts",
            "add-birthday": "Add a birthday to a contact",
            "show-birthday": "Show the birthday of a contact",
            "birthdays": "Show upcoming birthdays",
        }
        self.view.display_help(commands)


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Error: Not enough arguments."
        except KeyError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Error: {e}"
    return wrapper


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        return record.edit_phone(old_phone, new_phone)
    else:
        return f"Error: contact '{name}' not found."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {', '.join(phone.value for phone in record.phones)}"
    else:
        return f"Error: contact '{name}' not found."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return f"Error: contact '{name}' not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {record.show_birthday()}"
    else:
        return f"Error: contact '{name}' not found."


@input_error
def birthdays(args, book):
    return book.get_upcoming_birthdays()


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def main():
    view = ConsoleView() 
    book = AddressBook(view=view)

    view.display_message("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            view.display_message("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            view.display_message("How can I help you?")
        elif command == "add":
            view.display_message(add_contact(args, book))
        elif command == "change":
            view.display_message(change_contact(args, book))
        elif command == "phone":
            view.display_message(show_phone(args, book))
        elif command == "all":
            book.show_all()
        elif command == "add-birthday":
            view.display_message(add_birthday(args, book))
        elif command == "show-birthday":
            view.display_message(show_birthday(args, book))
        elif command == "birthdays":
            view.display_message(birthdays(args, book))
        elif command == "help":
            book.show_help()
        else:
            view.display_message("Invalid command.")

if __name__ == "__main__":
    main()