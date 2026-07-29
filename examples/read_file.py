from marine4py.core.nmea import NMEASentence
from marine4py.core.error import ParseError

file = open('data.log', encoding='utf-8')

for line in file.readlines():
    try:
        msg = NMEASentence.parse(line, dialect="gps")
        print(repr(msg))
    except ParseError as e:
        print('Parse error: {}'.format(e))
        continue