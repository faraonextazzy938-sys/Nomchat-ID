import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Настройки — такие же как в основном сервере
EMAIL_HOST     = 'smtp.gmail.com'
EMAIL_PORT     = 587
EMAIL_USER     = ''          # example@gmail.com
EMAIL_PASSWORD = ''          # пароль приложения
EMAIL_FROM     = 'Nomchat ID <example@gmail.com>'

def send_code(to_email: str, code: str) -> bool:
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f'[NOMCHAT EMAIL] Демо. Код для {to_email}: {code}')
        return False

    fmt = f'{code[:3]} {code[3:]}'
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden">
      <div style="background:linear-gradient(135deg,#1565c0,#0d47a1);padding:28px;text-align:center">
        <span style="color:#fff;font-size:1.3em;font-weight:900">Nomchat</span>
        <span style="background:#fff;color:#111;font-size:0.75em;font-weight:900;padding:2px 7px;border-radius:4px;margin-left:6px">ID</span>
      </div>
      <div style="padding:32px;text-align:center">
        <p style="color:#333;margin-bottom:20px">Your login code for <strong>Nomchat ID</strong>:</p>
        <div style="background:#1565c0;color:#fff;font-size:2.2em;font-weight:900;letter-spacing:12px;padding:18px 24px;border-radius:10px;display:inline-block">{fmt}</div>
        <p style="color:#999;font-size:0.85em;margin-top:20px">Valid for 10 minutes. If you didn't request this, ignore this email.</p>
      </div>
    </div>
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Nomchat ID — login code: {fmt}'
        msg['From']    = EMAIL_FROM
        msg['To']      = to_email
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[NOMCHAT EMAIL] Error: {e}')
        return False
