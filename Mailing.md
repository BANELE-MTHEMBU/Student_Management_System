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
    EMAIL = "<youremail>"
    PASSWORD = "<password>"
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
