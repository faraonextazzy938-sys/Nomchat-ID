import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_HOST     = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT     = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER     = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_FROM     = os.environ.get('EMAIL_FROM', 'Nomchat ID <noreply@nomchat.id>')

def send_code(to_email: str, code: str) -> bool:
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f'[NOMCHAT] Demo code for {to_email}: {code}')
        return False

    fmt = f'{code[:3]} {code[3:]}'
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:40px 20px">
  <tr><td align="center">
    <table width="480" cellpadding="0" cellspacing="0" style="background:#111118;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden">
      <tr>
        <td style="background:linear-gradient(135deg,#1a3a6b,#1565c0);padding:32px;text-align:center">
          <table cellpadding="0" cellspacing="0" style="margin:0 auto">
            <tr>
              <td style="background:rgba(255,255,255,0.15);border-radius:10px;padding:8px 12px;display:inline-block">
                <span style="color:#fff;font-size:1.3em;font-weight:900;letter-spacing:1px">💬 Nomchat</span>
                <span style="background:#fff;color:#111;font-size:0.7em;font-weight:900;padding:2px 7px;border-radius:4px;margin-left:6px">ID</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td style="padding:40px 36px;text-align:center">
          <p style="color:rgba(255,255,255,0.6);font-size:1em;margin-bottom:8px">Your login code</p>
          <div style="background:linear-gradient(135deg,#1565c0,#0d47a1);border-radius:16px;padding:24px 32px;display:inline-block;margin:16px 0">
            <span style="color:#fff;font-size:2.8em;font-weight:900;letter-spacing:16px;font-family:monospace">{fmt}</span>
          </div>
          <p style="color:rgba(255,255,255,0.4);font-size:0.85em;margin-top:16px;line-height:1.6">
            Valid for <strong style="color:rgba(255,255,255,0.7)">10 minutes</strong>.<br>
            If you didn't request this, ignore this email.
          </p>
        </td>
      </tr>
      <tr>
        <td style="padding:20px 36px;border-top:1px solid rgba(255,255,255,0.06);text-align:center">
          <span style="color:rgba(255,255,255,0.25);font-size:0.78em">© 2026 Nomchat ID. All rights reserved.</span>
        </td>
      </tr>
    </table>
  </td></tr>
</table>
</body></html>"""

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Nomchat ID — your code: {fmt}'
        msg['From']    = EMAIL_FROM
        msg['To']      = to_email
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_USER, to_email, msg.as_string())
        print(f'[NOMCHAT] Email sent to {to_email}')
        return True
    except Exception as e:
        print(f'[NOMCHAT] Email error: {e}')
        return False
