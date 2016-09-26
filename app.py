import logging
import random

from flask import Flask, render_template
from flask_ask import Ask, question, statement, session

from wiktionary import WiktionaryDictionary

app = Flask(__name__)
ask = Ask(app, "/")
log = logging.getLogger()
dictionary = WiktionaryDictionary()

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def welcome():
    welcome_msg = render_template('welcome' + str(random.randint(1, 3)))
    log.debug('Run welcome:' + welcome_msg)
    return question(welcome_msg)


def strip_whitespaces(xml):
    data3 = []
    data2 = xml.split('\n')
    for x in data2:
        y = x.strip()
        if y:
            data3.append(y)
    data4 = ''.join(data3)
    data5 = data4.replace("  ", "").replace("> <", "><")
    return data5

@ask.intent("WordSearchIntent")
def word_inquire(word):
    log.debug("Run word_inquire({})".format(word))
    definitions = dictionary.definitions(word)

    if not definitions:
        msg = render_template('word_not_found', word=word)
        log.debug(msg)
        return statement(msg)
    else:
        part_of_speech = definitions.keys()[0]
        definition = definitions[part_of_speech][0]
        log.debug(definition)
        msg = render_template('word_found', word=word, part_of_speech=part_of_speech, definition=definition,
                              trim_blocks=True)
        #msg = strip_whitespaces(msg)

        session.attributes['word'] = word
        session.attributes['definitions'] = definitions
        session.attributes['last_message'] = msg

        log.debug(msg)
        return question(msg)


@ask.intent("RepeatIntent")
def repeat():
    log.debug("Run repeat()")
    if 'word' not in session.attributes:
        msg = render_template('word_not_selected')
        return statement(msg)
    else:
        return question(session.attributes['last_message'])


@ask.intent("SummaryIntent")
def word_summary():
    log.debug("Run word_summary()")
    if not session.attributes['word']:
        msg = render_template('word_not_selected')
        return statement(msg)
    else:
        definitions = session.attributes['definitions']

        number_of_definitions = sum([len(i) for i in definitions.values()])
        available_parts_of_speech = definitions.keys()

        msg = render_template('word_summary', number_of_defitions=number_of_definitions,
                              available_parts_of_speech=available_parts_of_speech)
        #msg = strip_whitespaces(msg)
        session.attributes['last_message'] = msg
        return question(msg)


@ask.intent("AllDefinitionsIntent")
def all_definitions(part_of_speech):
    log.debug("Run all_definitions({})".format(part_of_speech))
    if not session.attributes['word']:
        msg = render_template('word_not_selected')
        return statement(msg)
    else:
        definitions = session.attributes['definitions']
        part_of_speech = part_of_speech.lower()

        if part_of_speech not in definitions:
            msg = render_template('part_of_speech_not_found')
            return question(msg)
        else:
            selected_definitions = definitions[part_of_speech]
            msg = render_template('all_definitions', part_of_speech=part_of_speech, definitions=selected_definitions)
            session.attributes['last_message'] = msg
        return question(msg)

if __name__ == '__main__':
    app.run(debug=True)
