# encoding: utf-8
import sys
import argparse
from workflow import Workflow, ICON_WEB, ICON_WARNING, ICON_INFO, web

#TODO
#add the legal

API_URL = 'http://jisho.org/api/v1/search/words'
MAX_CACHE_AGE = 86400 # seconds is 24 hours
MIN_QUERY_LENGTH = 1
log = None

def get_words(query):
    """Retrieve words from jisho.org

    Returns stuff

    """
    params = dict(keyword=query)
    r = web.get(API_URL, params)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by pinboard and extract the posts
    result = r.json()
    words = result['data']
    return words

def main(wf):
    # get the args
    query = wf.args[0]

    # log.debug(len(query))
    #
    # if not len(query):
    #     wf.add_item("Query too short.", "Keep typing...", icon=ICON_WARNING)
    #     # wf.add_item("Nothing found.", "Try a different query.", icon=ICON_WARNING)
    #     wf.send_feedback()
    #     return 0

    # determine whether we have ja or en input
    try:
       query.decode('ascii')
    except UnicodeEncodeError:
        query = query # this japanese input needs no quotations
    else:
        query = '"' + query + '"' # ascii input, that is en, needs quotations

    def wrapper():
        """`cached_data` can only take a bare callable
        (no args),
        so we need to wrap callables needing arguments
        with a function that needs no arguments.
        """
        return get_words(query)

    if query:
        words = wf.cached_data(query, wrapper, max_age=MAX_CACHE_AGE)

    # Tell the user there is nothing to show
    if not len(words):
        wf.add_item("Nothing found.", "Try a different query.", icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for word in words:
#        if 'japanese' in word & 'senses' in word:
        if all (k in word for k in ('japanese','senses')):
            # build the title string
            if 'word' in word['japanese'][0]:
                thisTitle = word['japanese'][0]['word']
            else:
                thisTitle = word['japanese'][0]['reading']

            thisSub = ""
            if 'reading' in word['japanese'][0]:
                thisSub += word['japanese'][0]['reading']

            for idx, sense in enumerate(word['senses']):
                thisSub += "  "
                thisSub += str(idx + 1)
                thisSub += ". "
                thisSub += ", ".join(sense['english_definitions'])

            wf.add_item(title=thisTitle,
                        subtitle=thisSub,
#                        modifier_subtitles={
#                                        u'shift': u'Subtext when shift is pressed',
#                                        u'fn': u'Subtext when fn is pressed',
#                                        u'ctrl': u'Subtext when ctrl is pressed',
#                                        u'alt': u'Subtext when alt is pressed',
#                                        u'cmd': u'Subtext when cmd is pressed'
#                                    },
                        arg=thisTitle,
                        valid=True,
                        largetext=thisTitle,
                        icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
