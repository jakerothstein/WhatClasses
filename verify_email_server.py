import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
password = "" # use you email password (would recommend and app password if using google)
sender = "" # use your email address that will be sending the email
server_adress = "http://127.0.0.1:8000" # change this to the server address


def send_verifacation_email(email, code):
    link = f"{server_adress}/verify-otp/{email}/{code}"
    subject = "Email Verification"
    recipients = [email]
    html = f"""<div style="font-family: Helvetica, Arial, sans-serif; min-width: 1000px; overflow: auto; line-height: 2;">
    <div style="margin: 50px auto; width: 70%; padding: 20px 0;">
        <div style="border-bottom: 1px solid #eee;">
            <a href="#" style="font-size: 1.4em; color: #00466a; text-decoration: none; font-weight: 600;">WhatClasses</a>
        </div>
        <p style="font-size: 1.1em;">Hello,</p>
        <p>Thank you for choosing WhatClasses. Use the following link to complete your Sign Up procedure.</p>
        <a href="{link}" style="display: inline-block; background-color: #00466a; color: #fff; font-weight: 600; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">Complete Sign Up</a>
        <p style="font-size: 0.9em;">Regards,<br />WhatClasses</p>
        <hr style="border: none; border-top: 1px solid #eee;" />
        <div style="float: right; padding: 8px 0; color: #aaa; font-size: 0.8em; line-height: 1; font-weight: 300;">
            <p>WhatClasses Inc</p>
            <p>Burlingame California</p>
        </div>
    </div>
</div>

    """
    msg = MIMEMultipart("alternative")
    part2 = MIMEText(html, "html")
    msg.attach(part2)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())


def reset_password_email(email, code):
    link = f"{server_adress}/reset-password/{email}/{code}"
    subject = "Password Reset"
    recipients = [email]
    html = f"""<div style="font-family: Helvetica, Arial, sans-serif; min-width: 1000px; overflow: auto; line-height: 2;">
        <div style="margin: 50px auto; width: 70%; padding: 20px 0;">
            <div style="border-bottom: 1px solid #eee;">
                <a href="#" style="font-size: 1.4em; color: #00466a; text-decoration: none; font-weight: 600;">WhatClasses</a>
            </div>
            <p style="font-size: 1.1em;">Hello,</p>
            <p>Thank you for choosing WhatClasses. Use the following link to reset your password.</p>
            <a href="{link}" style="display: inline-block; background-color: #00466a; color: #fff; font-weight: 600; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">Password Reset</a>
            <p style="font-size: 0.9em;">Regards,<br />WhatClasses</p>
            <hr style="border: none; border-top: 1px solid #eee;" />
            <div style="float: right; padding: 8px 0; color: #aaa; font-size: 0.8em; line-height: 1; font-weight: 300;">
                <p>WhatClasses Inc</p>
                <p>Burlingame California</p>
            </div>
        </div>
    </div>

        """
    msg = MIMEMultipart("alternative")
    part2 = MIMEText(html, "html")
    msg.attach(part2)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())