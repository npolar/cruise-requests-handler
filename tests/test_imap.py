import imaplib
import email
import yaml
import re
import getpass

def extract_body(payload):
    if isinstance(payload, str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])

def extract_config_yaml(body):
    pattern = "---([^-]+)---"
    config_string = re.findall(pattern, body)
    yaml_config = yaml.load(config_string[0])
    return yaml_config

user = getpass.getuser(); print user
password = getpass.getpass(prompt='Password: ', stream=None)

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login(user, password)
conn.select()
typ, data = conn.search(None, '(SUBJECT "data request")')
try:
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                subject = msg['subject']
                print(subject)
                payload = msg.get_payload()
                body = extract_body(payload)
                config = extract_config_yaml(body)
                print(config)
                typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()
