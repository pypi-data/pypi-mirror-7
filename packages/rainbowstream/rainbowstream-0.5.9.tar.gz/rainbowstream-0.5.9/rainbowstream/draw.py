import random
import itertools
import requests
import datetime
import time
import re

from twitter.util import printNicely
from functools import wraps
from pyfiglet import figlet_format
from dateutil import parser
from .c_image import *
from .colors import *
from .config import *
from .db import *
from .py3patch import *


db = RainbowDB()
g = {}


def init_cycle():
    """
    Init the cycle
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    return itertools.cycle(colors_shuffle)


def start_cycle():
    """
    Notify from rainbow
    """
    g['cyc'] = init_cycle()
    g['cache'] = {}


def order_rainbow(s):
    """
    Print a string with ordered color with each character
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    colored = [colors_shuffle[i % 7](s[i]) for i in xrange(len(s))]
    return ''.join(colored)


def random_rainbow(s):
    """
    Print a string with random color with each character
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    colored = [random.choice(colors_shuffle)(i) for i in s]
    return ''.join(colored)


def Memoize(func):
    """
    Memoize decorator
    """
    @wraps(func)
    def wrapper(*args):
        if args not in g['cache']:
            g['cache'][args] = func(*args)
        return g['cache'][args]
    return wrapper


@Memoize
def cycle_color(s):
    """
    Cycle the colors_shuffle
    """
    return next(g['cyc'])(s)


def ascii_art(text):
    """
    Draw the Ascii Art
    """
    fi = figlet_format(text, font='doom')
    print('\n'.join(
        [next(g['cyc'])(i) for i in fi.split('\n')]
    ))


def check_config():
    """
    Check if config is changed
    """
    changed = False
    data = get_all_config()
    for key in c:
        if key in data:
            if data[key] != c[key]:
                changed = True
    if changed:
        reload_config()


def validate_theme(theme):
    """
    Validate a theme exists or not
    """
    # Theme changed check
    files = os.listdir(os.path.dirname(__file__) + '/colorset')
    themes = [f.split('.')[0] for f in files if f.split('.')[-1] == 'json']
    return theme in themes


def reload_theme(current_config):
    """
    Check current theme and update if necessary
    """
    exists = db.theme_query()
    themes = [t.theme_name for t in exists]
    if current_config != themes[0]:
        config = os.path.dirname(
            __file__) + '/colorset/' + current_config + '.json'
        # Load new config
        data = load_config(config)
        if data:
            for d in data:
                c[d] = data[d]
        # Restart color cycle and update db/config
        start_cycle()
        db.theme_update(current_config)
        set_config('THEME', current_config)


def color_func(func_name):
    """
    Call color function base on name
    """
    if str(func_name).isdigit():
        return term_color(int(func_name))
    return globals()[func_name]


def draw(t, keyword=None, check_semaphore=False, fil=[], ig=[]):
    """
    Draw the rainbow
    """

    # Check the semaphore lock (stream process only)
    if check_semaphore:
        if db.semaphore_query_pause():
            return
        while db.semaphore_query_lock():
            time.sleep(0.5)

    # Check config and theme
    check_config()
    reload_theme(c['THEME'])

    # Retrieve tweet
    tid = t['id']
    text = t['text']
    screen_name = t['user']['screen_name']
    name = t['user']['name']
    created_at = t['created_at']
    favorited = t['favorited']
    date = parser.parse(created_at)
    date = date - datetime.timedelta(seconds=time.timezone)
    clock_format = '%Y/%m/%d %H:%M:%S'
    try:
        clock_format = c['FORMAT']['TWEET']['CLOCK_FORMAT']
    except:
        pass
    clock = date.strftime(clock_format)

    # Pull extended retweet text
    try:
        text = 'RT @' + t['retweeted_status']['user']['screen_name'] + ': ' +\
            t['retweeted_status']['text']
    except:
        pass

    # Unescape HTML character
    text = unescape(text)

    # Get expanded url
    try:
        expanded_url = []
        url = []
        urls = t['entities']['urls']
        for u in urls:
            expanded_url.append(u['expanded_url'])
            url.append(u['url'])
    except:
        expanded_url = None
        url = None

    # Get media
    try:
        media_url = []
        media = t['entities']['media']
        for m in media:
            media_url.append(m['media_url'])
    except:
        media_url = None

    # Filter and ignore
    screen_name = '@' + screen_name
    if fil and screen_name not in fil:
        return
    if ig and screen_name in ig:
        return

    # Get rainbow id
    res = db.tweet_to_rainbow_query(tid)
    if not res:
        db.tweet_store(tid)
        res = db.tweet_to_rainbow_query(tid)
    rid = res[0].rainbow_id

    # Format info
    name = cycle_color(name)
    nick = color_func(c['TWEET']['nick'])(screen_name)
    clock = clock
    id = str(rid)
    fav = ''
    if favorited:
        fav = color_func(c['TWEET']['favorited'])(u'\u2605')

    tweet = text.split()
    # Replace url
    if expanded_url:
        for index in range(len(expanded_url)):
            tweet = lmap(
                lambda x: expanded_url[index]
                if x == url[index]
                else x,
                tweet)
    # Highlight RT
    tweet = lmap(
        lambda x: color_func(c['TWEET']['rt'])(x)
        if x == 'RT'
        else x,
        tweet)
    # Highlight screen_name
    tweet = lmap(lambda x: cycle_color(x) if x[0] == '@' else x, tweet)
    # Highlight link
    tweet = lmap(
        lambda x: color_func(c['TWEET']['link'])(x)
        if x[0:4] == 'http'
        else x,
        tweet)
    # Highlight hashtag
    tweet = lmap(
        lambda x: color_func(c['TWEET']['hashtag'])(x)
        if x.startswith('#')
        else x,
        tweet)
    # Highlight keyword
    tweet = ' '.join(tweet)
    if keyword:
        roj = re.search(keyword, tweet, re.IGNORECASE)
        if roj:
            occur = roj.group()
            ary = tweet.split(occur)
            delimiter = color_func(c['TWEET']['keyword'])(occur)
            tweet = delimiter.join(ary)

    # Load config formater
    try:
        formater = c['FORMAT']['TWEET']['DISPLAY']
        formater = name.join(formater.split("#name"))
        formater = nick.join(formater.split("#nick"))
        formater = fav.join(formater.split("#fav"))
        formater = tweet.join(formater.split("#tweet"))
        # Change clock word
        word = [w for w in formater.split() if '#clock' in w][0]
        delimiter = color_func(c['TWEET']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [w for w in formater.split() if '#id' in w][0]
        delimiter = color_func(c['TWEET']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
    except:
        printNicely(red('Wrong format in config.'))
        return

    # Draw
    printNicely(formater)

    # Display Image
    if c['IMAGE_ON_TERM'] and media_url:
        for mu in media_url:
            try:
                response = requests.get(mu)
                image_to_display(BytesIO(response.content))
            except Exception:
                printNicely(red('Sorry, image link is broken'))


def print_message(m, check_semaphore=False):
    """
    Print direct message
    """

    # Check the semaphore lock (stream process only)
    if check_semaphore:
        if db.semaphore_query_pause():
            return
        while db.semaphore_query_lock():
            time.sleep(0.5)

    # Retrieve message
    sender_screen_name = '@' + m['sender_screen_name']
    sender_name = m['sender']['name']
    text = unescape(m['text'])
    recipient_screen_name = '@' + m['recipient_screen_name']
    recipient_name = m['recipient']['name']
    mid = m['id']
    date = parser.parse(m['created_at'])
    date = date - datetime.timedelta(seconds=time.timezone)
    clock_format = '%Y/%m/%d %H:%M:%S'
    try:
        clock_format = c['FORMAT']['MESSAGE']['CLOCK_FORMAT']
    except:
        pass
    clock = date.strftime(clock_format)

    # Get rainbow id
    res = db.message_to_rainbow_query(mid)
    if not res:
        db.message_store(mid)
        res = db.message_to_rainbow_query(mid)
    rid = res[0].rainbow_id

    # Draw
    sender_name = cycle_color(sender_name)
    sender_nick = color_func(c['MESSAGE']['sender'])(sender_screen_name)
    recipient_name = cycle_color(recipient_name)
    recipient_nick = color_func(
        c['MESSAGE']['recipient'])(recipient_screen_name)
    to = color_func(c['MESSAGE']['to'])('>>>')
    clock = clock
    id = str(rid)

    text = ''.join(lmap(lambda x: x + '  ' if x == '\n' else x, text))

    # Load config formater
    try:
        formater = c['FORMAT']['MESSAGE']['DISPLAY']
        formater = sender_name.join(formater.split("#sender_name"))
        formater = sender_nick.join(formater.split("#sender_nick"))
        formater = to.join(formater.split("#to"))
        formater = recipient_name.join(formater.split("#recipient_name"))
        formater = recipient_nick.join(formater.split("#recipient_nick"))
        formater = text.join(formater.split("#message"))
        # Change clock word
        word = [w for w in formater.split() if '#clock' in w][0]
        delimiter = color_func(c['MESSAGE']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [w for w in formater.split() if '#id' in w][0]
        delimiter = color_func(c['MESSAGE']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
    except:
        printNicely(red('Wrong format in config.'))
        return

    # Draw
    printNicely(formater)


def show_profile(u):
    """
    Show a profile
    """
    # Retrieve info
    name = u['name']
    screen_name = u['screen_name']
    description = u['description']
    profile_image_url = u['profile_image_url']
    location = u['location']
    url = u['url']
    created_at = u['created_at']
    statuses_count = u['statuses_count']
    friends_count = u['friends_count']
    followers_count = u['followers_count']

    # Create content
    statuses_count = color_func(
        c['PROFILE']['statuses_count'])(
        str(statuses_count) +
        ' tweets')
    friends_count = color_func(
        c['PROFILE']['friends_count'])(
        str(friends_count) +
        ' following')
    followers_count = color_func(
        c['PROFILE']['followers_count'])(
        str(followers_count) +
        ' followers')
    count = statuses_count + '  ' + friends_count + '  ' + followers_count
    user = cycle_color(
        name) + color_func(c['PROFILE']['nick'])(' @' + screen_name + ' : ') + count
    profile_image_raw_url = 'Profile photo: ' + \
        color_func(c['PROFILE']['profile_image_url'])(profile_image_url)
    description = ''.join(
        lmap(lambda x: x + ' ' * 4 if x == '\n' else x, description))
    description = color_func(c['PROFILE']['description'])(description)
    location = 'Location : ' + color_func(c['PROFILE']['location'])(location)
    url = 'URL : ' + (color_func(c['PROFILE']['url'])(url) if url else '')
    date = parser.parse(created_at)
    date = date - datetime.timedelta(seconds=time.timezone)
    clock = date.strftime('%Y/%m/%d %H:%M:%S')
    clock = 'Join at ' + color_func(c['PROFILE']['clock'])(clock)

    # Format
    line1 = u"{u:>{uw}}".format(
        u=user,
        uw=len(user) + 2,
    )
    line2 = u"{p:>{pw}}".format(
        p=profile_image_raw_url,
        pw=len(profile_image_raw_url) + 4,
    )
    line3 = u"{d:>{dw}}".format(
        d=description,
        dw=len(description) + 4,
    )
    line4 = u"{l:>{lw}}".format(
        l=location,
        lw=len(location) + 4,
    )
    line5 = u"{u:>{uw}}".format(
        u=url,
        uw=len(url) + 4,
    )
    line6 = u"{c:>{cw}}".format(
        c=clock,
        cw=len(clock) + 4,
    )

    # Display
    printNicely('')
    printNicely(line1)
    if c['IMAGE_ON_TERM']:
        try:
            response = requests.get(profile_image_url)
            image_to_display(BytesIO(response.content))
        except:
            pass
    else:
        printNicely(line2)
    for line in [line3, line4, line5, line6]:
        printNicely(line)
    printNicely('')


def print_trends(trends):
    """
    Display topics
    """
    for topic in trends[:c['TREND_MAX']]:
        name = topic['name']
        url = topic['url']
        line = cycle_color(name) + ': ' + color_func(c['TREND']['url'])(url)
        printNicely(line)
    printNicely('')


def print_list(group):
    """
    Display a list
    """
    for g in group:
        # Format
        name = g['full_name']
        name = color_func(c['GROUP']['name'])(name + ' : ')
        member = str(g['member_count'])
        member = color_func(c['GROUP']['member'])(member + ' member')
        subscriber = str(g['subscriber_count'])
        subscriber = color_func(
            c['GROUP']['subscriber'])(
            subscriber +
            ' subscriber')
        description = g['description'].strip()
        description = color_func(c['GROUP']['description'])(description)
        mode = g['mode']
        mode = color_func(c['GROUP']['mode'])('Type: ' + mode)
        created_at = g['created_at']
        date = parser.parse(created_at)
        date = date - datetime.timedelta(seconds=time.timezone)
        clock = date.strftime('%Y/%m/%d %H:%M:%S')
        clock = 'Created at ' + color_func(c['GROUP']['clock'])(clock)

        # Create lines
        line1 = ' ' * 2 + name + member + '  ' + subscriber
        line2 = ' ' * 4 + description
        line3 = ' ' * 4 + mode
        line4 = ' ' * 4 + clock

        # Display
        printNicely('')
        printNicely(line1)
        printNicely(line2)
        printNicely(line3)
        printNicely(line4)

    printNicely('')


def show_calendar(month, date, rel):
    """
    Show the calendar in rainbow mode
    """
    month = random_rainbow(month)
    date = ' '.join([cycle_color(i) for i in date.split(' ')])
    today = str(int(os.popen('date +\'%d\'').read().strip()))
    # Display
    printNicely(month)
    printNicely(date)
    for line in rel:
        ary = line.split(' ')
        ary = lmap(
            lambda x: color_func(c['CAL']['today'])(x)
            if x == today
            else color_func(c['CAL']['days'])(x),
            ary)
        printNicely(' '.join(ary))


# Start the color cycle
start_cycle()
