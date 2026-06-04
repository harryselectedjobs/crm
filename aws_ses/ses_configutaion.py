import boto3
import os
from dotenv import load_dotenv


load_dotenv()



def send_email_ses(recipient, subject, body_text, body_html):
    ses = boto3.client(
        "ses",
        region_name="eu-north-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    response = ses.send_email(
        Source="harry@selected.jobs",
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {"Data": body_text, "Charset": "UTF-8"},
                "Html": {"Data": body_html, "Charset": "UTF-8"}
            }
        }
        # Removed: ConfigurationSetName="my-tracking"
    )

    return response


# send_email_ses(
#     recipient="btech60067.19@bitmesra.ac.in",
#     subject="Test Email from SES",
#     body_text="Hello! This email is sent using Amazon SES + boto3.",
#     body_html="""
#     <html>
#       <body>
#         <h2>Hello!</h2>
#         <p>This email is sent using <b>Amazon SES</b> + boto3.</p>
#       </body>
#     </html>
#     """
# )