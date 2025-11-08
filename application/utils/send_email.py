import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def send_email(
    sender_email,
    sender_password,
    recipient_email,
    subject,
    body,
    pdf_path,
    smtp_server="smtp.gmail.com",
    smtp_port=587,
):
    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Add body text
        msg.attach(MIMEText(body, "plain"))

        # Attach PDF
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(pdf_path)}"',
                )
                msg.attach(part)

        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Error:", str(e))


# Example usage
if __name__ == "__main__":
    send_email(
        sender_email="mscs20029@gmail.com",
        sender_password="hebr oohl gedg tiir",  # use App Password for Gmail
        recipient_email="ziaurrehman6434@gmail.com",
        subject="Test Email with PDF",
        body="Hello,\n\nThis is a test email with a PDF attachment.\n\nRegards,\nYour Python Script",
        pdf_path="sample.pdf",
    )
