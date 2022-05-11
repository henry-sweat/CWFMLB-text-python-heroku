import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client
import os

url = os.environ.get('URL')

def scrape(webpage):
    r = requests.get(webpage)
    soup = BeautifulSoup(r.content, 'html.parser')

    header = soup.find_all('pre')[0].get_text()
    body = soup.find_all('pre')[1].get_text()

    reportDate = re.findall("EDT\s\D{3,4}\s(.+20\d{2})", header)[0]

    reportTime = re.findall("(\d{3,4}\s\D{2})\sEDT", header)[0]

    reportName = re.findall("Coa.+ida", header)[0]

    synopsis = re.findall("SYNOPSIS\n(.+)\n\n\nGULF", header, flags=re.DOTALL)[0].replace('\n',' ')

    westWall = re.findall("(\d{2})\snaut.+Ponce", header)[0]

    #area = re.findall("Fla.+ine", body)[0]

    areaForecast = re.findall("(.+)\n\n", body, flags=re.DOTALL)[0]

    print(len(areaForecast))

    # TWILIO FUNCTIONALITY
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=f'{reportName}\n{reportTime} || {reportDate}\n\nSynopsis: {synopsis}\n\nThe approximate location of the west wall'
             f' of the Gulf Stream is {westWall} nautical miles east of Ponce Inlet\n\n',
        from_=os.environ.get('TWILIO_PHONE_NUMBER'),
        to=os.environ.get('PHONE_NUMBER')
    )

    #print(message.sid)

    if len(areaForecast) > 1599:
        last_break = areaForecast[:1500].rfind("\n\n")
        message = client.messages \
            .create(
            body=f'{areaForecast[:last_break]}',
            from_=config.TWILIO_PHONE_NUMBER,
            to=config.PHONE_NUMBER
            )
        #print(message.sid)

        message = client.messages \
            .create(
            body=f'{areaForecast[last_break:]}',
            from_=config.TWILIO_PHONE_NUMBER,
            to=config.PHONE_NUMBER
        )
        #print(message.sid)
    else:
        message = client.messages \
            .create(
            body=f'{areaForecast}',
            from_=config.TWILIO_PHONE_NUMBER,
            to=config.PHONE_NUMBER
        )
        #print(message.sid)


if __name__ == '__main__':
    scrape(url)

