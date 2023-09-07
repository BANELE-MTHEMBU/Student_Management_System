### SMS - Student Management System

This is a simple student database management system using `mysql` and `flask`.

### Programming Languages

In this project we are using the following programming languages:

```shell
- python
```

### Database

For the database we are going to use the following database

```shell
- mongodb
```

> Make sure that you have an instance of `mongodb` running in your computer.

### How to contribute?

1. You need to fork the repository.

You need to run the following commands in-order to contribute to `Student_Management_System`.

```shell
git clone https://github.com/BANELE-MTHEMBU/Student_Management_System.git
```

Then:

```shell
cd Student_Management_System
```

You need to create a virtual environment by running the following command.

```shell
virtualenv venv
# activate it
.\venv\Scripts\activate
```

Then install packages that are currently used:

```shell
pip install -r requirements.txt
```

### Database

All the database configuration are located in the `client.py` for both the `users` and `secretes` collections.

```python

# first importing the pymongo
from pymongo import MongoClient

#client is going to connect to MongoClient using the link from MongoDB
#client(local host)
client = MongoClient('mongodb://localhost:27017')

# creating / connecting the database 'sms'
db = client['sms']

#creating a collection -> a collection in mongoDB is actually a table
users = db["users"]
secretes = db["secretes"]
```

### You are Done contributing??

When you are done contributing we recommend you to run the following command before comitting changes
to github.

```shell
pip freeze > requirements.txt
```

### SMS

- bootstrap
- mongodb
- python
- flask
- css
- html

```shell
# user
- id
- email
- password
- avatar
- role (ADMIN | STUDENT)
```

- register (ADMIN)

  - email

- login (ADMIN, STUDENT)

- ADMIN -> REGISTER STUDENTS
  : DEREGISTER STUDENTS
  : EDIT STUDENTS

\*\* MONGODB

### Sending emails in Python

In this readme file we are going to learn how we can send emails using python. First thing first we are going to use `smtplib` library to send emails.

Follow the from [this link](https://support.google.com/accounts/answer/185833?hl=en) to generate password, for your mailing account. After getting the password copy the password for that mailing account as we are going to use it to send emails in python.

### Sending plain Email

In the following example we are going to send a plain email using python.

```py
import smtplib, ssl
from keys import Keys


class SmtpConfig(object):
    FROM = Keys.EMAIL
    PORT = 465  # For SSL
    SMTP_SERVER = "smtp.gmail.com"
    PASSWORD = Keys.PASSWORD


def sendEmail(to: str, body: str, subject: str):
    message = f"""\
    Subject: {subject}
    {body}
    """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        SmtpConfig.SMTP_SERVER, SmtpConfig.PORT, context=context
    ) as server:
        server.login(SmtpConfig.FROM, SmtpConfig.PASSWORD)
        server.sendmail(SmtpConfig.FROM, to, message)


sendEmail("crispengari@gmail.com", "Hi", "Testing")

```

> Note that the `keys.py` file will not be committed to github as we will add it to the `.gitignore` file and this file looks as follows:

```py
class Keys(object):
    EMAIL = "<your_email>"
    PASSWORD = "<your_password>"
```

### Sending email as html.

The following code snippet allows us to send email as `html`

```py
import smtplib, ssl
from keys import Keys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SmtpConfig(object):
    FROM = Keys.EMAIL
    PORT = 465  # For SSL
    SMTP_SERVER = "smtp.gmail.com"
    PASSWORD = Keys.PASSWORD

def sendFancyEmail(to: str, body: str, subject: str):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SmtpConfig.FROM
    message["To"] = to

    html = f"""
    <html>
    <body>
        <p>Hi,<br>
        {body}<br>

    </body>
    </html>
    """
    part2 = MIMEText(html, "html")
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", SmtpConfig.PORT, context=context) as server:
        server.login(SmtpConfig.FROM, SmtpConfig.PASSWORD)
        server.sendmail(SmtpConfig.FROM, to, message.as_string())

```

> If you want to send email with attachment read it [here](https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development)

### Refs

1. [realpython.com](https://realpython.com/python-send-email/)
2. [stackoverflow.com](https://stackoverflow.com/questions/70261815/smtplib-smtpauthenticationerror-534-b5-7-9-application-specific-password-req)
3. [python-and-mongodb](https://github.com/CrispenGari/python-and-mongodb)
4. [01_Flask](https://github.com/CrispenGari/python-and-flask/tree/main/01_Flask)
