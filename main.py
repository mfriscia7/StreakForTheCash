from MongoFile import StreakDB
from datetime import date
import pymongo

'''
{'date': {'day': 7,
        'month': 5,
        'time': {'hour': 22,
                'minute': 15
                    }
        'year': 2015
        },
'description': u'MLB',
'home_team_won': False,
'loser': {'percent': 89.7,
            'record': {'loss': u'15',
                        'win': u'14'
                            },
            'score': 2.0,
            'team': u'San Francisco Giants'
            },
'network': u'',
'popularity': 83.38,
'question': u'Who will WIN this matchup?',
'sport': u'MLB',
'winner': {'percent': 10.3,
            'record': {'loss': u'15', 'win': u'14'},
            'score': 7.0,
            'team': u'Miami Marlins'
                }
        }
'''


def create_db():
    db = StreakDB('Streak')
    db.add_dates(date(2008, 8, 25), date(2016, 2, 11))
    return db


def drop_db():
    client = pymongo.MongoClient('localhost', 27017)
    client.drop_database('Streak')


def get_db():
    s = StreakDB('Streak')
    return s.get_coll()

#create_db()
#drop_db()

#db = get_db()
#r = db.find({'winner.team': 'Tottenham Hotspur'})
#for i in r:
#    print i
