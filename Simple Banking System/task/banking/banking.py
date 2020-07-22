# Write your code here
import random
import sqlite3

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

    def get_balance(self):
        print("Balance: " + str(self.balance))


def store_account(account):
    card_id = random.randint(0, 100)
    accounts_list.append(account)
    # create and save new_account to database
    create_account = f'INSERT INTO card (number, pin) VALUES ({account.card_num}, {account.pin})'
    cur.execute(create_account)
    conn.commit()


logged_in = False


def log_in(input_card_num, input_pin):
    auth_account = None
    cur.execute('SELECT * FROM card')
    accounts = cur.fetchall()
    for account in accounts:
        if account[1] == input_card_num and account[2] == input_pin:
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
    print("2. Log out")
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
        user.get_balance()
        show_logged_user_page(user)

    elif choice == 2:
        log_out()
        show_init_page()
    else:
        exit_app()


show_init_page()
