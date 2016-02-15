from main import get_db
import re


def get_teams():
    # makes a dictionary of teams to analyse and consolidate
    # i.e. put together 'Tottenham' and 'Tottenham Hotspur'
    db = get_db()
    d = set()

    result = db.find({}, {"_id": 0, 'winner.team': 1, 'description': 1})
    for i in result:
        d.add((i['description'].split(' ')[0], sub_common_names(i['winner']['team'])))

    result = db.find({}, {"_id": 0, 'loser.team': 1, 'description': 1})
    for i in result:
        d.add((i['description'].split(' ')[0], sub_common_names(i['loser']['team'])))

    to_remove = []

    disclude = ['v. ', 'vs. ', ' v ', '@', ' or ', ' OR ', ' AND ',
                'or Fewer', 'or Lower', 'or More', '+', 'Any Other', ',',
                '1st ', '2nd ', '3rd', '1-', '(USA)', ' - ', 'Touchdown',
                'Strikeout']

    for item in d:
        if any(i in item[1] for i in disclude):
            to_remove.append(item)
        elif item[1] == 'Yes' or item[1] == 'No':
            to_remove.append(item)

    for k in to_remove:
        d.remove(k)

    f = open("teams", "w")
    for sport, team in d:
        for s2, t2 in d:
            if team in t2 and not team == t2:
                j = sport + '|' + team + '-------' + s2 + '|' + t2
                f.write("%s\n" % j.encode('ascii', 'ignore'))
    f.close()
    # f = open("teams", "w")
    # for j in d:
    #     f.write("%s\n" % j.encode('ascii', 'ignore'))
    # f.close()


def sub_common_names(phrase):
    catalog = []
    # changes St., St to State
    catalog.append([[r'\sSt\.?(\s|$)'], ' State '])
    # changes U-19 or U20 to U19 and U20
    catalog.append([[r'U-'], r'U'])

    for arr in catalog:
        for i in arr[0]:
            if not re.compile(i).findall(phrase) == []:
                phrase = re.sub(i, arr[1], phrase)
    return phrase.strip()

#print sub_common_names('Cal St Bruins,NCB')


def update_teams(old, new):
    print 1

#get_teams()
# db = get_db()
# w = db.find({'date.day': 1, 'date.month': 2, 'date.year': 2016, 'winner.percent': {'$gte': 98.0}}).count()
# l = db.find({'date.day': 1, 'date.month': 2, 'date.year': 2016, 'loser.percent': {'$gte': 98.0}}).count()
# print l
# print w
# print float(l)/(w+l)


# s = set()
#
# r = db.find({'winner.team': {'$regex': 'Alabama St(?:\.|ate)'}}, {'winner': 1})
# for i in r:
#     print i['winner']['team']
 # for i in r:
 #     s.add(i)
# print len(s)

