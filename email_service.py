import smtplib, os, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_HOST     = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT     = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USER     = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_FROM     = os.environ.get('EMAIL_FROM', f'Nomchat ID <{EMAIL_USER}>')

def send_code(to_email: str, code: str) -> bool:
    """Send verification code. Returns True if sent via SMTP, False if demo mode."""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f'[NOMCHAT EMAIL] Demo mode — code for {to_email}: {code}')
        return False

    fmt  = f'{code[:3]} {code[3:]}'
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fa;padding:40px 20px">
<tr><td align="center">
<table width="520" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.10)">

  <!-- Header -->
  <tr>
    <td style="background:linear-gradient(135deg,#1a3a6b 0%,#1565c0 50%,#0d47a1 100%);padding:36px 40px;text-align:center">
      <table cellpadding="0" cellspacing="0" style="margin:0 auto">
        <tr>
          <td style="background:rgba(255,255,255,0.15);border-radius:14px;padding:12px 20px">
            <span style="font-size:1.6em;vertical-align:middle">💬</span>
            <span style="color:#fff;font-size:1.3em;font-weight:900;letter-spacing:1px;vertical-align:middle;margin-left:8px">NOMCHAT</span>
            <span style="background:#fff;color:#1565c0;font-size:0.7em;font-weight:900;padding:3px 8px;border-radius:5px;margin-left:6px;vertical-align:middle">ID</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:44px 40px 36px;text-align:center">
      <p style="color:#555;font-size:1em;margin:0 0 8px">Your verification code</p>
      <h1 style="color:#111;font-size:1.5em;font-weight:800;margin:0 0 28px">Log in to Nomchat ID</h1>

      <!-- Code box -->
      <div style="background:linear-gradient(135deg,#1565c0,#0d47a1);border-radius:16px;padding:28px 40px;display:inline-block;margin-bottom:28px">
        <span style="color:#fff;font-size:2.8em;font-weight:900;letter-spacing:16px;font-family:'Courier New',monospace">{fmt}</span>
      </div>

      <p style="color:#777;font-size:0.92em;line-height:1.7;margin:0 0 8px">
        This code expires in <strong style="color:#333">10 minutes</strong>.
      </p>
      <p style="color:#aaa;font-size:0.85em;margin:0">
        If you didn't request this, you can safely ignore this email.
      </p>
    </td>
  </tr>

  <!-- Divider -->
  <tr><td style="padding:0 40px"><div style="height:1px;background:#f0f0f0"></div></td></tr>

  <!-- Footer -->
  <tr>
    <td style="padding:24px 40px;text-align:center">
      <p style="color:#bbb;font-size:0.78em;margin:0">
        © 2026 Nomchat ID &nbsp;·&nbsp;
        <a href="#" style="color:#1565c0;text-decoration:none">Privacy Policy</a> &nbsp;·&nbsp;
        <a href="#" style="color:#1565c0;text-decoration:none">Terms of Service</a>
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body></html>"""

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Your Nomchat ID code: {fmt}'
        msg['From']    = EMAIL_FROM
        msg['To']      = to_email
        msg['X-Priority'] = '1'
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ctx)
            smtp.ehlo()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_USER, to_email, msg.as_string())

        print(f'[NOMCHAT EMAIL] Sent to {to_email}')
        return True
    except Exception as e:
        print(f'[NOMCHAT EMAIL] Error: {e}')
        return False
