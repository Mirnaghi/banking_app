# Write your code here
import random
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# # create engine
# engine = create_engine('sqlite:///card.s3db?check_same_thread=False')
#
# Base = declarative_base()
#
#
# # define table
# class Card(Base):
#     __tablename__ = 'card'
#     id = Column(Integer, primary_key=True)
#     number = Column(String)
#     pin = Column(String)
#     balance = Column(Integer, default=0)
#
#     def __repr__(self):
#         return self.number
#
#
# # create database
# Base.metadata.create_all(engine)
#
#
# # create session for accessing database
# Session = sessionmaker(bind=engine)
# session = Session()
accounts_list = []

create_table = """
CREATE TABLE IF NOT EXISTS card (
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
)
"""
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute(create_table)
conn.commit()


class BankAccount:
    def __init__(self):
        self.card_num = None
        self.pin = None
        self.balance = 0

    def create_account(self):
        # generate card number for user
        card_num = "400000"

        c_n_sum = 0

        while (len(card_num) < 15):
            digit = random.randint(0, 9)

            card_num += str(digit)

        for i in range(15):
            new_digit = None
            if i % 2 == 0:
                new_digit = int(card_num[i]) * 2
            else:
                new_digit = int(card_num[i])

            if new_digit > 9:
                c_n_sum += (new_digit - 9)
            else:
                c_n_sum += new_digit

        if c_n_sum % 10 == 0:
            last_digit = 0
        else:
            last_digit = 10 - (c_n_sum % 10)

        card_num += str(last_digit)

        # generate PIN for user
        card_pin = ""
        while len(card_pin) < 4:
            card_pin += str(random.randint(0, 9))

        self.card_num = card_num
        self.pin = card_pin

    # def get_balance(self):
    #     print("Balance: " + str(self.balance))


# id for accounts as PRIMARY KEY
card_id = 0


def store_account(account):
    global card_id
    accounts_list.append(account)
    # create and save new_account to database
    create_account = f'INSERT INTO card (id, number, pin) VALUES ({card_id}, {account.card_num}, {account.pin})'
    cur.execute(create_account)
    conn.commit()
    card_id += 1  # after creating new account increment id by 1


logged_in = False


def log_in(input_card_num, input_pin):
    auth_account = None
    cur.execute('SELECT number, pin FROM card')
    accounts = cur.fetchall()
    print(accounts)
    for account in accounts:
        if account[0] == input_card_num and account[1] == input_pin:
            global logged_in
            logged_in = True
            auth_account = account
            print("You have successfully logged in!")
    else:
        print("Wrong card number or PIN!")
        logged_in = False

    return auth_account


def log_out():
    print("You have successfully logged out!")


def get_balance(account):
    """
    Show balance of user
    :param account: logged user`s account
    :return: print user`s balance
    """
    cur.execute(f"SELECT balance FROM card WHERE number={account[0]}")
    balance = cur.fetchall()
    print("Balance: {}".format(balance[0][0]))


def add_income(user):
    print("Enter income:")
    amount = int(input())
    cur.execute(f"""UPDATE card SET balance = balance + {amount} WHERE number={user[0]}""")
    conn.commit()
    print("Income was added!")


def check_card__validation(card_number):
    """
    Check car number validation according to Luhn algorithm
    :param card_number: input card number
    :return: True if valid, False if not
    """
    card_num_sum = 0
    for i in range(15):
        new_digit = None
        if i % 2 == 0:
            new_digit = int(card_number[i]) * 2
        else:
            new_digit = int(card_number[i])

        if new_digit > 9:
            card_num_sum += (new_digit - 9)
        else:
            card_num_sum += new_digit

    card_num_sum += int(card_number[-1])

    if card_num_sum % 10 == 0:
        return True
    else:
        return False


def check_card_exists(card_number):
    """
    check card number is exists or not
    :param card_number: input number
    :return: True if exists, False if not
    """
    exists = False
    cur.execute("SELECT number FROM card")
    card_numbers = cur.fetchall()

    for number in card_numbers:
        if card_number == number[0]:
            exists = True
            break
    return exists


def do_transfer(user):
    """
    Transfer money from user`s account to other account
    :param user: logged user
    :return: message according to the successful or unsuccessful transfer
    """
    print("Transfer")
    print("Enter card number:")
    card_num = input()

    if user[0] == card_num:
        print("You can't transfer money to the same account!")
        return

    cur.execute(f"SELECT balance FROM card WHERE number = {user[0]}")
    balance = cur.fetchall()

    valid = check_card__validation(card_num)
    if valid:
        exists = check_card_exists(card_num)
        if exists:
            print("Enter how much money you want to transfer:")
            amount = int(input())
            if balance[0][0] >= amount:
                cur.execute(f"UPDATE card SET balance = balance - {amount} WHERE id = {user[0]}")
                conn.commit()
                print("Success!")
            else:
                print("Not enough money!")
        else:
            print("Such a card does not exists.")
    else:
        print("Probably you made mistake in the card number. Please try again!")


def close_account(user_id):
    """
    Delete user account
    :param user_id: id of user`s account
    :return: prints delete message
    """
    cur.execute(f"DELETE FROM card WHERER id = {user_id}")
    conn.commit("The account has been closed!")


def exit_app():
    print("Bye!")


# interact with user

def show_init_page():
    """
    Show initial page to user
    :return: 
    """
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    user_choice = int(input())

    handle_init_page(user_choice)


def show_logged_user_page(user):
    """
    Shows account page to logged user
    :param user: Logged user`s account
    :return: 
    """
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")

    user_choice = int(input())

    handle_logged_user_page(user, user_choice)


def handle_init_page(choice):
    """
    Handles user`s choice
    :param choice: User`s activity choice
    :return: 
    """
    if choice == 1:
        new_account = BankAccount()
        new_account.create_account()
        store_account(new_account)

        print("Your card has been created")
        print("Your card number:")
        print(new_account.card_num)
        print("Your card PIN:")
        print(new_account.pin)

        show_init_page()

    elif choice == 2:
        print("Enter your card number:")
        user_card_num = input()
        print("Enter your PIN:")
        user_pin = input()
        current_account = log_in(user_card_num, user_pin)
        if current_account != None:
            show_logged_user_page(current_account)
        else:
            show_init_page()

    else:
        exit_app()


def handle_logged_user_page(user, choice):
    """
    Handle authenticate user`s activities
    :param user: Logged user
    :param choice: User`s action choice
    :return: 
    """
    if choice == 1:
        get_balance(user)
        show_logged_user_page(user)

    elif choice == 2:
        add_income(user)
        show_logged_user_page(user)

    elif choice == 3:
        do_transfer(user)
        show_logged_user_page(user)

    elif choice == 4:
        close_account(user[0])
        show_init_page()

    elif choice == 5:
        log_out()
        show_init_page()
    else:
        exit_app()


show_init_page()

