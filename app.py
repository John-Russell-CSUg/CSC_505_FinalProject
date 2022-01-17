from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

# initialize app
app = Flask(__name__)
# Session Setup
app.secret_key = "csuglobal"
app.permanent_session_lifetime = timedelta(days=1)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Account Class
class account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Integer)
    pin = db.Column(db.Integer)
    balance = db.Column(db.Float)
    attempts = db.Column(db.Integer)
    locked = db.Column(db.Boolean)

    def __init__(self, acc_num, pin, balance):
        self.account = acc_num
        self.pin = pin
        self.balance = balance
        self.attempts = 0
        self.locked = False

    # Withdrawal Function
    def withdrawal(self, amount):
        self.balance -= amount

    # deposit Function
    def deposit(self, amount):
        self.balance += amount


@app.route("/validate_account", methods=["POST"])
def validate():
    acc_num = request.form["account"]
    pin = request.form["pin"]
    # Get account
    acc = account.query.filter_by(account=acc_num).first()
    if acc:  # if account exists
        if acc.balance == 0:  # if balance is 0 close account
            return close_account(acc)
        if not acc.locked:  # and is not locked
            if acc.attempts < 4:  # and has less than 4 attempts
                if int(pin) == acc.pin:  # and the pin matches
                    return render_template("account.html", account=acc.account, balance=acc.balance)  # view account
            else:  # add an attempt
                acc.attempts += 1
                if acc.attempts == 4:
                    acc.locked = True
                    return locked()
        else:  # return home
            return home()
    else:
        return home()


# home index
@app.route("/")
def home():
    return render_template('index.html')


# Create Account Page
@app.route("/create_account", methods=["POST", "GET"])
def create_account():
    if request.method == "POST":
        acc_num = request.form["account"]
        pin = request.form["pin"]
        balance = request.form["balance"]
        new_account = account(acc_num, pin, balance)
        # add account to database
        db.session.add(new_account)
        db.session.commit()
    return render_template('create_account.html')


# Locked Account Page
@app.route("/locked")
def locked():
    return render_template("account_locked.html")


# remove account from database
def close_account(acc):
    db.session.remove(acc)
    return home()


if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
