from datetime import datetime

import config
import operator
import pickle
import firebase_api

highscores = [('Errol', 323), ('Scabbers', 444), ('Severus', 400), ('Irma', 333), ('Granger', 500), ('Grawp', 44),
              ('Umbridge', 77), ('Rosmerta', 555),
              ('Krum', 2111), ('Elphias', 8)]

upload_queue = []

__multiplier = 0
__decrease_timer = 0
__last_multi = 0


def load_highscores():
    global highscores
    try:
        with open(config.HIGHSCORE_FILE, 'rb') as f:
            highscores = pickle.load(f)
            highscores = sorted(highscores, key=lambda t: t[1], reverse=True)
            highscores = highscores[:10]
            print('high scores loaded.')
    except IOError:
        print('HIGHSCORES COULD NOT BE LOADED: {}'.format(IOError))
        highscores = sorted(highscores, key=lambda t: t[1], reverse=True)
        highscores = highscores[:10]
        save_highscores()


def highest_score():
    load_highscores()
    return sorted(highscores, key=operator.itemgetter(1), reverse=True)[0][1]


def lowest_score():
    load_highscores()
    return sorted(highscores, key=operator.itemgetter(1), reverse=False)[0][1]


def update_highscores(new_score=None):
    global highscores
    if new_score is not None:
        queue_score = new_score + (datetime.utcnow(),)
        update_queue(queue_score)
        new_score += (str(datetime.utcnow()), config.FREE_MODE, config.LOCATION, config.CABINET_ID)
        highscores.append(new_score)
    highscores = sorted(highscores, key=lambda t: t[1], reverse=True)
    highscores = highscores[:10]
    process_queue()


def load_queue():
    global upload_queue
    try:
        with open(config.UPLOAD_QUEUE, 'wb') as f:
            upload_queue = pickle.load(f)
    except IOError:
        upload_queue = []


def update_queue(entry=None):
    global upload_queue
    if entry is not None:
        upload_queue.append(entry)
    with open(config.UPLOAD_QUEUE, 'wb') as f:
        pickle.dump(upload_queue, f)


def process_queue():
    global upload_queue
    new_upload_queue = []
    for entry in upload_queue:
        try:
            firebase_api.upload_highscore(entry[1], entry[0], entry[2])
        except Exception as e:
            print(e)
            # copy to new list if not uploaded
            new_upload_queue.append(entry)
    print('uploaded {} scores to database'.format(len(upload_queue) - len(new_upload_queue)))
    upload_queue = new_upload_queue
    update_queue()  # saves to pickle file


def get_place(new):
    score_list = highscores.copy()
    score_list.append(('$new', new))
    score_list.sort(key=operator.itemgetter(1), reverse=True)
    score_list = [score[0] for score in score_list]
    place = score_list.index('$new') + 1
    place_string = ''
    if place in [4, 5, 6, 7, 8, 9, 10]:
        place_string = '{}th'.format(place)
    elif place is 1:
        place_string = '1st'
    elif place is 2:
        place_string = '2nd'
    elif place is 3:
        place_string = '3rd'
    return place_string.upper(), place


def save_highscores():
    with open(config.HIGHSCORE_FILE, 'wb') as f:
        pickle.dump(highscores, f)
        print('highscores saved to local file')


def increase_score(reason='hit_brick', no_combo=False):
    if no_combo:
        multi = 1
    else:
        multi = max(__multiplier, 1)
    if reason == 'hit_brick':
        add = 10
    elif reason == 'killed_brick':
        add = 20
    elif reason == 'phagocyte':
        add = 15
    elif reason == 'powerup':
        add = 85
    print('{} * {}'.format(add, multi))
    return add * multi


def increase_multiplier():
    global __multiplier
    global __decrease_timer
    __multiplier += 1
    __decrease_timer = 0


def decrease_multiplier(time_passed):
    # call this in game loop
    global __decrease_timer
    global __multiplier
    if __multiplier > 0:
        __decrease_timer += time_passed
        if __decrease_timer > 1000:
            __decrease_timer = 0
            __multiplier = 0


def reset_multiplier():
    global __multiplier
    __multiplier = 0


def is_combo():
    return __multiplier >= 2


def get_combo():
    return max(__multiplier, 1)


def get_new_combo():
    # this returns a new combo multiplier only once
    global __last_multi
    if __last_multi != __multiplier:
        return_multi = __last_multi
    else:
        return_multi = None
    __last_multi = __multiplier
    return return_multi


def get_penalty(score):
    penalty = score * 0.1
    if penalty > 100:
        convert_step = int(penalty / 100)
    else:
        convert_step = 1

    # the following is needed to avoid rounding issues
    factor = penalty / convert_step
    penalty = convert_step * int(factor)
    return -int(penalty), int(convert_step)


def get_bonus(bonus):
    boni = {
        'time_bonus': 300,
        'no_continue': 20000,
        'all_pus': 100000,
        'clear': 20000,
        'perfect': 1000000
    }
    return boni.get(bonus)


load_queue()
load_highscores()  # make sure highscores are loaded at boot!

