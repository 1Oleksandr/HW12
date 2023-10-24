from collections import UserDict
from datetime import datetime
from itertools import islice
import pickle
import os.path


class PhoneError(Exception):
    ...


class DateError(Exception):
    ...


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    # def __repr__(self) -> str:
    #     return str(self)


class Name(Field):
    ...


class Phone(Field):

    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        if len(val) == 10 and int(val):
            self.__value = val
        else:
            raise ValueError()


class Birthday(Field):

    def __init__(self, birthday) -> None:
        self.__birthday = None
        self.birthday = birthday

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, birthday):
        if isinstance(birthday, datetime):
            self.birthday = birthday
        else:
            raise DateError()

    def __str__(self):
        return f"Days to birthday: {self.days_to_birthday}"


class Record:

    def __init__(self, name: str, phone: str = None, birthday: Birthday = None):
        self.name = Name(name)
        self.phones = []
        if phone:
            self.add_phone(phone)
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday

    def days_to_birthday(self) -> int:
        if self.birthday:
            current_date = datetime.today().date()
            birthday = self.birthday.replace(year=current_date.year)
            if birthday > current_date:
                days_to_birthday = birthday - current_date
            else:
                birthday = birthday.replace(year=current_date.year + 1)
                days_to_birthday = birthday - current_date
        else:
            raise DateError()
        return days_to_birthday.days

    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return f"Phone {old_phone} changed to phone {new_phone}"
        raise ValueError()

    def find_phone(self, phone):
        for p in self.phones:
            if Phone(phone).value == p.value:
                return p
        # raise ValueError()

    def remove_phone(self, phone):
        for p in self.phones:
            if Phone(phone).value == p.value:
                return self.phones.remove(p)
        raise PhoneError()

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        rec = self.data.get(name)
        if rec:
            f"Contact name: {rec.name.value}, phones: {'; '.join(p.value for p in rec.phones)}"
            return rec
        # else:
        #     raise KeyError()

    def delete(self, name):
        if self.data.get(name):
            del self.data[name]
        # else:
        #     raise KeyError()

    def iterator(self, n=None):
        counter = 0
        records = iter(self.data.values())
        while counter < len(self.data):
            rec = []
            for i in islice(records, n):
                rec.append(i)
                print(i)
            yield rec
            if n:
                counter += n
            else:
                break

    def __str__(self):
        return "\n".join([str(r) for r in self.data.values()])


# customers = AddressBook()
filename = 'address_book.bin'


def read_contacts_from_file(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as fh:
            customers = pickle.load(fh)
    else:
        customers = AddressBook()
    return customers


customers = read_contacts_from_file(filename)


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough params. It needs to have 2 params (Name Phone): "
        except KeyError:
            return "This name doesn't have in the dictionary."
        except NameError:
            return "This name is already in the dictionary. Use 'add phone' to append new phone."
        except ValueError:
            return "The phone number must contains only 10 digit."
        except PhoneError:
            return "This phone number doesn't exist in the dictionary."
        except DateError:
            return "Birthday date error"
    return inner


@input_error
def add_record(*args):
    name = args[0].lower()
    phone = args[1]
    try:
        if args[2]:
            birthday = datetime.strptime(args[2], "%d/%m/%Y").date()
    except:
        birthday = None
    rec = customers.get(name)
    if rec:
        raise NameError()
    rec = Record(name, phone, birthday)
    customers.add_record(rec)
    return f"Add name = {name}, phone = {phone}, birthday = {birthday}"


@input_error
def change_record(*args):
    name = args[0].lower()
    old_phone = args[1]
    new_phone = args[2]
    rec = customers.get(name)
    if rec:
        return rec.edit_phone(old_phone, new_phone)
    else:
        raise KeyError()


@input_error
def find_record(*args):
    name = args[0].lower()
    if customers.get(name):
        return customers.find(name)
    else:
        raise KeyError()


@input_error
def del_record(*args):
    name = args[0].lower()
    if customers.get(name):
        customers.delete(name)
        return f"Record with name {args[0].capitalize()} deleted."
    else:
        raise KeyError()


@input_error
def add_phone(*args):
    name = args[0].lower()
    new_phone = args[1]
    rec = customers.get(name)
    if rec:
        rec.add_phone(new_phone)
        return f"{args[0].capitalize()}'s phone added another one {args[1]}"
    else:
        raise KeyError()


@input_error
def find_phone(*args):
    name = args[0].lower()
    phone = args[1]
    rec = customers.get(name)
    if rec:
        find_phone = rec.find_phone(phone)
        return find_phone
    else:
        raise PhoneError()


@input_error
def remove_phone(*args):
    name = args[0].lower()
    phone = args[1]
    rec = customers.get(name)
    if rec:
        rec.remove_phone(phone)
        return f'{phone} deleted.'
    else:
        raise PhoneError()


@input_error
def add_birhday(*args):
    name = args[0].lower()
    try:
        birhday = datetime.strptime(args[1], "%d/%m/%Y")
    except:
        raise DateError()
    rec = customers.get(name)
    if rec:
        rec.add_birthday(birhday.date())
        return f"{args[0].capitalize()}'s birthday added {args[1]}"
    else:
        raise DateError()


@input_error
def days_to_birthday(*args):
    name = args[0].lower()
    rec = customers.get(name)
    if rec:
        days = rec.days_to_birthday()
        return f"{days} days to {name.capitalize()}'s birthday"
    else:
        raise KeyError()


def unknown(*args):
    return "Unknown command. Try again."


def end_program(*args):
    write_contacts_to_file(filename, customers)
    return "Good Bye!"


def hello(*args):
    return "How can I help you?:"


def help(*args):
    message = '''Use next commands:
    add 'name' 'phone'  - add name and phone number to the dictionary
    add_b 'name' 'birthday' - add birthday date to the name in dictionary
    add_phone 'name' 'phone'  - add phone number to the name in dictionary
    change 'name' 'old_phone' 'new_phone' - change phone number in this name
    days_to_birthday 'name' - return number days to birhday
    delete 'name' - delete name and phones from the dictionary
    find 'name' - find info by name
    seek 'name' 'phone' - find phone for name in the dictionary
    phone 'name' - show phone number for this name
    remove_phone 'name' 'phone' - remove phone for this name
    show_all  -  show all records in the dictionary
    show_all 'N' - show records by N numbers
    exit - exit from bot'''
    return message


def show_all(*args):
    try:
        if args[0]:
            for rec in customers.iterator(int(args[0])):
                input("Press Enter for next records")
    except:
        return customers
    # for name, record in customers.data.items():
    #     print(record)
    return "There is all records in dictionary"


@input_error
def phone(*args):
    name = args[0].lower()
    if customers[name]:
        return f'{name.capitalize()} has {customers[name]} phone number.'


COMMANDS = {add_record: "add",
            add_birhday: "add_b",
            add_phone: "add_phone",
            change_record: "change",
            days_to_birthday: "days_to_birthday",
            del_record: "delete",
            end_program: "exit",
            find_record: "find",
            find_phone: 'find_phone',
            hello: "hello",
            help: "help",
            phone: "phone",
            show_all: "show_all",
            remove_phone: "remove_phone"
            }


def parser(text: str):
    for func, kw in COMMANDS.items():
        command = text.rstrip().split()
        # if kw == command[0].lower():
        #     return func, text[len(kw):].strip().split()
        if text.lower().startswith(kw) and kw == command[0].lower():
            return func, text[len(kw):].strip().split()
    return unknown, []


def write_contacts_to_file(filename, customers):
    with open(filename, "wb") as fh:
        pickle.dump(customers, fh)


def main():
    while True:
        user_input = input(
            "Enter user name and phone number or 'help' for help: ")
        func, data = parser(user_input)
        print(func(*data))
        if user_input == 'exit':
            break


if __name__ == '__main__':
    main()
