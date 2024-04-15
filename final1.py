import imaplib
import email
from datetime import datetime
import re

name_regex = r'Patient Name (.+?)\n'
age_regex = r'Age (.+?)\n'
gender_regex = r'Gender (.+?)\n'
policy_regex = r'Policy No. (.+?)\n'

def fetch_emails(mode, from_date=None, to_date=None):
    # IMAP settings
    username = 'carmesystems.in@gmail.com'
    password = 'cyga omdm iflm gugb'
    imap_server = 'imap.gmail.com'
    mailbox = 'INBOX'
    print("Email Connected")

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select(mailbox)

    if mode == 'specified_date':
        # Convert from_date and to_date to datetime objects
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')

        # Search for emails within the specified date range
        date_query = '(SINCE {from_date} BEFORE {to_date})'.format(from_date=from_date_obj.strftime('%d-%b-%Y'),
                                                                    to_date=to_date_obj.strftime('%d-%b-%Y'))
    elif mode == 'today':
        # Get today's date
        today_date = datetime.today().strftime('%d-%b-%Y')
        date_query = '(SINCE {today_date})'.format(today_date=today_date)
    else:
        print("Invalid mode specified.")
        return []
    
    # Search for emails based on the date query
    result, data = mail.search(None, date_query)

    # Fetch email ids
    email_ids = data[0].split()

    emails = []
    for email_id in email_ids:
        # Fetch email data
        result, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract relevant information from the email
        sender = msg['from']
        receivers = msg['to']
        subject = msg['subject']
        date = msg['date']
        body = None

        # Fetching body
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')

        emails.append({'Sender': sender, 'Receiver': receivers, 'Subject': subject, 'Date': date, 'Body': body})

        # Print email body
        # print("Body:", body)

    # Close the connection
    mail.close()
    mail.logout()

    return emails

# Other functions remain the same...

# Example usage
mode = 'specified_date'
from_date = '2024-03-12'
to_date = '2024-03-15'
emails = fetch_emails(mode, from_date, to_date)
# for email_data in emails:
#     if email_data['Sender'] == "Maxcare Hospital <maxcarecashless@gmail.com>":
#         print("Sender:", email_data['Sender'])
#         print("Receiver:", email_data['Receiver'])
#         print("Subject:", email_data['Subject'])
#         print("Date:", email_data['Date'])

def extract_info_from_body(body):
    info = {}
    # Search for each information using regular expressions
    name_match = re.search(name_regex, body)
    age_match = re.search(age_regex, body)
    gender_match = re.search(gender_regex, body)
    policy_match = re.search(policy_regex, body)

    # Extract and store information if found
    if name_match:
        info['Patient Name'] = name_match.group(1)
    if age_match:
        info['Age'] = age_match.group(1)
    if gender_match:
        info['Gender'] = gender_match.group(1)
    if policy_match:
        info['Policy No.'] = policy_match.group(1)

    return info

for email_data in emails:
    if email_data['Sender'] == "Maxcare Hospital <maxcarecashless@gmail.com>":


        # Extract information from the email body
        info = extract_info_from_body(email_data['Body'])
        print("Patient INFO:")
        for key, value in info.items():
            print(key + ":", value)
        print("\n\n")