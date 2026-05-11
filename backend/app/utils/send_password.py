import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_password(email: str, password: str):
    msg = EmailMessage()
    msg["Subject"] = "Hisob yaratildi"
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = email

    msg.set_content(
        f"Sizning foydalanuvchi nomingiz: {email}\n" f"Sizning parolingiz: {password}",
        charset="utf-8",
    )

    try:

        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
            smtp.set_debuglevel(0)  # 1 qilsangiz terminalda loglarni ko'rasiz
            smtp.starttls()  # Aloqani shifrlash
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")
