# MSU Corn
# Script dedicated to letting my friends know when an MSU dining hall is serving corn
# Created by Blake Potvin (01/21/2022) at 4am
import feedparser
import smtplib
import ssl
import json
from datetime import date

def open_file(filename):
    with open(filename) as f:
        return json.load(f)

def get_menu(link):
    return feedparser.parse(link)

def parse_menu(corn_list, menu):
    current_date = date.today()
    date_str = current_date.strftime("%d %b %Y")
    if menu['feed']: # if there is a menu and it's not empty (ex. menu fails to load)
        hall_name = menu['feed']['title']
        for item in menu['entries']:
            if date_str in item['published']:
                title = item['title']
                if "Corn" in title.split():
                    corn_list[hall_name] = title
                    
def send_notification(credentials, emails, corn_list):
    messages = parse_list(corn_list)
    try:
        context = ssl.create_default_context()
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
        server_ssl.ehlo()
        server_ssl.login(*credentials)
        for email in emails:
            for message in messages:
                server_ssl.sendmail(credentials[0], email, message)
    except:
        print("Error connecting to SMTP server.")

def get_credentials(config):
    return tuple(config['credentials'].values())
    
def parse_list(corn_list):
    final_str = ""
    final_list = []
    if corn_list:
        final_str += "\r\n\r\nToday's Corn Offerings at MSU:\n\n"
        for hall in corn_list:
            if len(final_str) < 100: # sms is limited character length
                final_str += hall + ": \n" + corn_list[hall] + "\n\n"
            else:
                final_list.append(final_str)
                final_str = "\r\n\r\n" + hall + ": \n" + corn_list[hall] + "\n\n"
    else:
        final_str = "Sorry, no corn offerings today. 😭"
    final_list.append(final_str)
    return final_list

def main():
    CONFIG = "config.json"
    CONFIG_DICT = open_file(CONFIG)
    CREDENTIALS = get_credentials(CONFIG_DICT)
    DINING_MENUS = CONFIG_DICT['menus']
    corn_list = {}
    for menu_link in DINING_MENUS:
        menu = get_menu(menu_link)
        parse_menu(corn_list, menu)
    send_notification(CREDENTIALS, CONFIG_DICT['recipients'], corn_list)

if __name__ == "__main__":
    main()
