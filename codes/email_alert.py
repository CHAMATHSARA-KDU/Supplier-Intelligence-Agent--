"""
Email Alert Module
Sends autonomous email alerts with PDF report attached.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


def send_risk_alert_email(
    sender_email: str,
    sender_password: str,
    receiver_email: str,
    supplier_name: str,
    previous_score: float,
    current_score: float,
    risk_level: str,
    summary: str = "",
    pdf_path: str = None,
):
    delta = round(current_score - previous_score, 1)

    recommendations = {
        "LOW RISK":      "Continue monitoring. No immediate action required.",
        "MODERATE RISK": "Request trial order before full commitment.",
        "HIGH RISK":     "Activate contingency plan. Explore alternative suppliers.",
        "CRITICAL RISK": "Immediate action required. Do not proceed with this supplier.",
    }
    recommendation = recommendations.get(risk_level, "Review supplier immediately.")

    subject = f"Supplier Intelligence Report — {supplier_name}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a2744; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 20px;">Supplier Intelligence Report</h1>
            <p style="color: #d0d8e8; margin: 5px 0 0 0; font-size: 12px;">
                Generated autonomously — {datetime.now().strftime("%B %d, %Y at %H:%M")}
            </p>
        </div>

        <div style="background: #f9f9f9; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: #1a2744;">{supplier_name}</h2>

            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #1a2744;">
                    <td style="padding: 10px; color: white; font-weight: bold;">Risk Score</td>
                    <td style="padding: 10px; color: white; font-weight: bold;">Risk Level</td>
                    <td style="padding: 10px; color: white; font-weight: bold;">Change</td>
                </tr>
                <tr style="background: #fdf2f2;">
                    <td style="padding: 10px; font-size: 18px; font-weight: bold; color: #e74c3c;">
                        {current_score} / 10
                    </td>
                    <td style="padding: 10px; font-weight: bold; color: #e74c3c;">{risk_level}</td>
                    <td style="padding: 10px; color: #e74c3c;">+{delta} points</td>
                </tr>
            </table>

            <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin: 15px 0;">
                <strong>Recommended Action:</strong><br>{recommendation}
            </div>

            <p style="color: #555; font-size: 13px;">
                The full intelligence report is attached as a PDF.
            </p>

            <p style="color: #999; font-size: 11px; margin-top: 20px;">
                This report was generated autonomously by your Supplier Intelligence Agent
                on {datetime.now().strftime("%Y-%m-%d at %H:%M")} — no human intervention required.
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    msg.attach(MIMEText(html_body, "html"))

    # Attach PDF if provided
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(pdf_path)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"[Email] Report sent to {receiver_email} for {supplier_name}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False
