import api.pyCiscoSpark as Spark
import logging
import requests
import _thread
logger = logging.getLogger()
logger.setLevel(logging.INFO)


### Step #1 Capture Your Bot Info Here ###
BotToken = '' # YOUR BOT TOKEN HERE
BotID = '' # YOUR BOT ID HERE


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
    if resp['personId'] != BotID: #Bot ID prevents infinit msg
        logger.info('4 on decode_msg{}'.format(resp))
        on_bot_chat(resp, at)


def on_bot_chat(data, at):
    trig = data['text'].split()
    logger.info('Trigger word'.format(trig[0].lower()))
    if trig[0].lower() in ['beer', 'beers', 'mybeer']:
        pass
        #get_beer(data, at)
    else:
        Spark.post_markdown(at, data['roomId'], data['text'])


def get_beer(data, at):
    url = 'https://api.brewerydb.com/v2/search?type=beer&key=c647058759d0465fd66d2ff773ec7b7b&format=json&q='
    url = url + data['text']
    resp = requests.get(url)
    logger.info('5 got BeerDB{}'.format(resp.json()))

    beerInfo = resp.json()
    beer = '## ' + beerInfo['data'][0]['nameDisplay'] + "\n" +\
           '* ABV: **' + beerInfo['data'][0]['style']['abvMax'] + '%**' + "\n" +\
           '* IBU: **' + beerInfo['data'][0]['style']['ibuMax'] + '**' + "\n" +\
           '* Syle: **' + beerInfo['data'][0]['style']['shortName'] + '**' + "\n" +\
           '* Desc: *' + beerInfo['data'][0]['style']['description'] + '*'

    beerIcon = beerInfo['data'][0]['labels']['large']
    _thread.start_new_thread(post_logo, (at, data, beerIcon))
    Spark.post_markdown(at, data['roomId'], beer)


def post_logo(at, data, beerIcon):
    Spark.post_file(at, data['roomId'], beerIcon)


def clean_text(txt):
    txt = txt.lower()
    txt = txt.replace("testtie ", "") ###### Add your bot name Here
    txt = txt.replace("@testtie ", "") ###### Add your bot name Here with @
    txt = txt.replace("?","")
    txt = txt.replace("/", "")
    txt = txt.replace("!", "")
    txt = txt.replace("/n/r", "")
    return txt