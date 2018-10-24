#!/usr/bin/env python3
from __future__ import print_function
import os
import time
import json
import click
import email
import base64
import shutil
import httplib2
import traceback
import subprocess

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    # TODO: Handle '--noauth_local_webserver' in click
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args(
        args=[])
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/mega-account-creator.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'MEGA Account Creator'
CREDENTIALS_PATH = ".credentials"
CREDENTIALS_FILE = "mega-account-creator.json"

ACCOUNTS_FILE = "accounts.txt"
REG_COMMAND = 'megareg --register --scripted --email "{0}" --name {1}' + \
              " --password {2}"
GMAIL_QUERY = "subject:MEGA Email Verification Required"
CONFIRM_LINK = "https://mega.nz/#confirm"


# @click.command()
# @click.option('-e', '--email', help="Mega.nz Account E-Mail")
# @click.option('-p', '--password', help="Mega.nz Account Password")
# @click.option('-n', '--name', default="", help="Mega.nz Account Name")
# @click.option('-l', '--limit', default=10, help="Number of Accounts to create")
# @click.option(
#     '-o', '--output', default=ACCOUNTS_FILE, help="Account Info Storage")
# @click.option(
#     '--register/--no-register', default=True, help="Register the Accounts")
# @click.option('--verify/--no-verify', default=True, help="Verify the Accounts")
def cli(email, password, name, limit, output, register, verify):
    try:
        # if not shutil.which('megareg'):
        #     print("Megatools is not installed." +
        #           "Download it from https://megatools.megous.com/")
        #     return
        cwd = os.path.dirname(os.path.realpath(__file__))
        account_info_path = os.path.join(cwd, output)
        if register:
            register_accounts(email, password, name, limit, account_info_path)
        click.secho(
            "\n\nSleeping for 10 seconds to allow the verification " +
            "mails to reach GMail...\n",
            fg='red')
        time.sleep(10)
        if verify:
            verify_accounts(account_info_path)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return


def register_accounts(email, password, name, limit, output_path):
    """Creates the required amount of account credentials & Registers them.

    Stores the created accounts & their verification_states in the specified
    output file.

    Returns:
        None
    """
    click.secho("\nStarting Registration...\n", fg='red')
    prefix = email.split('@')[0]
    suffix = email.split('@')[-1]
    if not name:
        name = prefix

    account_info_dict = {}

    for counter in range(1, limit + 1):
        account_email = "{PREFIX}+{COUNTER}@{SUFFIX}".format(
            PREFIX=prefix, COUNTER=counter, SUFFIX=suffix)
        account_name = "{NAME}+{COUNTER}".format(NAME=name, COUNTER=counter)
        account_password = password
        command = REG_COMMAND.format(account_email, account_name,
                                     account_password)
        click.secho(command, fg='magenta')
        verification_state = subprocess.check_output(
            command, shell=True, universal_newlines=True)
        account_info_dict[account_email] = verification_state.strip()
        time.sleep(5)
    with open(output_path, 'w') as accounts:
        json.dump(account_info_dict, accounts)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, CREDENTIALS_PATH)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CREDENTIALS_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        click.secho(
            '\nStoring Credentials to {}\n'.format(credential_path), fg='red')
    return credentials


def get_confirmation_links():
    """Gets valid confirmation links from GMail.

    Currently doesn't handle multiple confirmation links sent to the same mail
    address.

    Returns:
        Confirmation Link Dictionary, a dictionary containing a mapping between
        the email address and the confirmation link.
    """
    confirmation_link_dict = {}
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    result = service.users().messages().list(
        userId="me", q=GMAIL_QUERY).execute()
    messages = result.get('messages')
    if not messages:
        return False
    for message in messages:
        message_id = message["id"]
        mail_object = service.users().messages().get(
            userId="me", id=message_id, format="raw").execute()
        mail_string = base64.urlsafe_b64decode(
            mail_object['raw'].encode('UTF-8'))
        mail = email.message_from_string(mail_string)
        mail_to = mail["To"]
        mail_link = None
        for part in mail.walk():
            if part.get_content_type() == "text/plain":
                mail_link = get_confirmation_link(part.get_payload())
        if mail_link:
            confirmation_link_dict[mail_to] = mail_link
    return confirmation_link_dict


def get_confirmation_link(mail_payload):
    for line in mail_payload.split("\n"):
        if CONFIRM_LINK in line:
            return line.strip()
    return None


def verify_accounts(input_path):
    """Verifies the created accounts.

    Takes the created accounts & their verification_states from the specified
    output file.

    Returns:
        None
    """
    click.secho("\nStarting Verification...\n", fg='red')
    with open(input_path, 'r') as accounts_json:
        account_info_dict = json.load(accounts_json)
    if not account_info_dict:
        return
    account_confirmation_dict = get_confirmation_links()
    accounts = set(account_info_dict.keys()) & set(
        account_confirmation_dict.keys())
    count = 0
    for account in accounts:
        account_verification_command = account_info_dict[account]
        account_confirmation_link = account_confirmation_dict[account]
        command = account_verification_command.replace(
            "@LINK@", "{}".format(account_confirmation_link))
        click.secho(command, fg='magenta')
        try:
            verification_output = subprocess.check_output(command, shell=True)
            if verification_output:
                click.secho(
                    "Account {0} was verified successfully\n".format(account),
                    fg="green")
                count += 1
        except Exception as e:
            print(e)
            continue
    click.secho(
        "\n\nSuccessfully Verified Accounts ::: {0}\n\n".format(count),
        fg='green')
    return


if __name__ == '__main__':
    cli(email='pditty881188@gmail.com', password='playas8811', name='test', limit=10, output='accounts.txt', register=True,
        verify=True)