import re
from collections import Counter
from .classes import Lyrics, LyricLine
from .utilities import validateTimecode, unpackTimecode
WORD = re.compile(r'\S+')

def text_to_vector(text):
    words = WORD.findall(
        re.sub('[?|$|.|!|,|[|\]|(|)|\']', '',
               re.sub('\(.*\)', '',
                      re.sub(ur'\p{P}+', '',
                             re.sub('<[^<]+?>', '', re.sub('<br\s*/?>|-|_', ' ', text.lower()
                                                           )
                                    )
                             )
                      )
               )
    )
    if len(words) < 3:
        words = list(words)

    return Counter(words)

def parse(lrc, **kwargs):

    lines = lrc.split('\n')
    lyrics = Lyrics()
    items = []
    timecode = None

    for i in range(len(lines)):
        if lines[i].startswith('[ar:'):
            lyrics.artist = lines[i].rstrip()[4:-1].lstrip()

        elif lines[i].startswith('[ti:'):
            lyrics.title = lines[i].rstrip()[4:-1].lstrip()

        elif lines[i].startswith('[al:'):
            lyrics.album = lines[i].rstrip()[4:-1].lstrip()

        elif lines[i].startswith('[by:'):
            lyrics.author = lines[i].rstrip()[4:-1].lstrip()

        elif lines[i].startswith('[length:'):
            lyrics.length = lines[i].rstrip()[8:-1].lstrip()

        elif lines[i].startswith('[offset:'):
            lyrics.offset = lines[i].rstrip()[8:-1].lstrip()

        elif lines[i].startswith('[re:'):
            lyrics.editor = lines[i].rstrip()[4:-1].lstrip()

        elif lines[i].startswith('[ve:'):
            lyrics.version = lines[i].rstrip()[4:-1].lstrip()

        elif len(lines[i].split(']')[0]) >= len('[0:0:0]'):
            if validateTimecode(lines[i].split(']')[0] + ']'):
                while validateTimecode(lines[i].split(']')[0] + ']'):
                    timecode = lines[i].split(']')[0] + ']'
                    text = ''.join(lines[i].split(']')[-1]).rstrip()
                    lyric_line = LyricLine(timecode, text=text)
                    items.append(lyric_line)

                    lines[i] = lines[i][len(timecode)::]
            elif timecode and len(text_to_vector(lines[i].strip())) == 0:
                lyric_line = LyricLine(timecode, text='')
                items.append(lyric_line)

        elif items and len(text_to_vector(lines[i].strip())) == 0:
            lyric_line = LyricLine(timecode, text='')
            items.append(lyric_line)


    # Override the parsed value with the specified value
    lyrics.__dict__.update(kwargs)

    lyrics.extend(sorted(items))

    if not lyrics.offset == "" and validateTimecode(lyrics.offset.split(']')[0] + ']'):
        offset_mins, offset_secs, offset_millis = unpackTimecode(lyrics.offset)
        for i in range(len(lyrics)):
            lyrics[i].shift(minutes=offset_mins, seconds=offset_secs,
                milliseconds=offset_millis)

    return lyrics
