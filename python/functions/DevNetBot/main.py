import api.pyCiscoSpark as Spark
import logging
import requests
import _thread
logger = logging.getLogger()
logger.setLevel(logging.INFO)


####LINES NUMBERS NEEDING YOUR ATTENTION ARE
# LINE 13 | 14 | 97 | 98


### Step #1 Capture Your Bot Info Here ###
BotToken = '' # YOUR BOT TOKEN HERE
BotEmail = '' # YOUR BOT's EMAIL <XXXXXXX@sparkbot.io>


def handle(event, context):
    accessToken = BotToken
    logger.info('1 got event{}'.format(event))
    if 'detail-type' in event:
        logger.info('Timer Function Executed')
    else:
        if event['resource'] == 'memberships':
            on_bot_add(event, accessToken)
        else:
            decode_msg(event, accessToken)


def on_bot_add(data, at):
    logger.info('2 on bot add event{}'.format(data))
    welcome_text = '''## Hello! Welcome!
Want to know more about a specific Beer? I am your Beer Bot \n
Type **/Beer** followed by the name of the beer to find out more \n'''
    Spark.post_markdown(at, data['data']['roomId'], welcome_text)


def decode_msg(data, at):
    uri = 'https://api.ciscospark.com/v1/messages/' + data['data']['id']
    resp = Spark.get_message(at, data['data']['id'])
    logger.info('3 on get_message{}'.format(resp))
    resp['text'] = clean_text(resp['text'])
    if resp['personEmail'] != BotEmail: #Bot ID prevents infinit msg
        logger.info('4 on decode_msg{}'.format(resp))
        on_bot_chat(resp, at)


def on_bot_chat(data, at):
    trig = data['text'].split()
    logger.info('Trigger word'.format(trig[0].lower()))
    if trig[0].lower() in ['beer', 'beers', 'mybeer']:
        get_beer(data, at)
    else:
        Spark.post_markdown(at, data['roomId'], data['text'])


def get_beer(data, at):
    url = 'https://api.brewerydb.com/v2/search?type=beer&key=c647058759d0465fd66d2ff773ec7b7b&format=json&q='
    url = url + data['text']
    resp = requests.get(url)
    logger.info('5 got BeerDB{}'.format(resp.json()))

    name = 'N/A'
    abv = 'N/A'
    ibu = 'N/A'
    style = 'N/A'
    desc = 'N/A'
    icon = 'beer.png'

    beerInfo = resp.json()

    ## Check for Keys
    if 'abvMax' in beerInfo['data'][0]['style']:
        abv = beerInfo['data'][0]['style']['abvMax']
    if 'ibuMax' in beerInfo['data'][0]['style']:
        ibu = beerInfo['data'][0]['style']['ibuMax']
    if 'shortName' in beerInfo['data'][0]['style']:
        style = beerInfo['data'][0]['style']['shortName']
    if 'description' in beerInfo['data'][0]['style']:
        desc = beerInfo['data'][0]['style']['description']
    if 'labels' in beerInfo['data'][0]:
        icon = beerInfo['data'][0]['labels']['large']

    beer = '## ' + beerInfo['data'][0]['nameDisplay'] + "\n" +\
           '* ABV: **' + abv + '%**' + "\n" +\
           '* IBU: **' + ibu + '**' + "\n" +\
           '* Syle: **' + style + '**' + "\n" +\
           '* Desc: *' + desc + '*'

    _thread.start_new_thread(Spark.post_file, (at, data, icon))
    Spark.post_markdown(at, data['roomId'], beer)


def clean_text(txt):
    txt = txt.lower()
    txt = txt.replace(" ", "") ###### Add your bot name Here
    txt = txt.replace("@ ", "") ###### Add your bot name Here with @
    txt = txt.replace("?","")
    txt = txt.replace("/", "")
    txt = txt.replace("!", "")
    txt = txt.replace("/n/r", "")
    return txt