from bs4 import BeautifulSoup
import requests
from datetime import date
import re
from pprint import pprint
import sys


def get_team_record(result, is_home_record, is_winner):
    if not is_home_record == []:
        home_record = is_home_record[0].text
        pattern = re.compile(r'\((\d+)-(\d+)-?(\d+)?\)')
        if pattern.search(home_record) is not None:
            rec = re.findall(pattern, home_record)[0]
            if 'record' not in result[is_winner]:
                result[is_winner]['record'] = {}
            result[is_winner]['record']['win'] = rec[0]
            result[is_winner]['record']['loss'] = rec[1]
            if not rec[2] == '':
                result[is_winner]['record']['draw'] = rec[2]


def get_team_name(i, home_team_won):
    team_name = i.select(
                        'table tbody')[0].select(
                        'tr td.mg-column3 span a')
    if team_name == []:
        team_name = i.select(
                            'table tbody')[0].select(
                            'tr td.mg-column3 span strong')
    pattern = re.compile(r'(?:\#\d+)?(?:\(\d+\))?\s?(.*)(?:\s\(\d+\-\d+(?:\-\d+)?\))')
    team_name_reg = pattern.findall(team_name[home_team_won].text)
    if team_name_reg == []:
        pattern = re.compile(r'(?:\#\d+)?(?:\(\d+\))?\s?(.*)')
        team_name_reg = pattern.findall(team_name[home_team_won].text)
    return team_name_reg[0]


def scrape_page(link, date_obj):
    response = requests.get(link + ''.join(str(date_obj).split('-')))
    soup = BeautifulSoup(response.text, "lxml")
    props = [i for i in soup.select('div.matchup-container')]
    prop_num = 0

    full_results = []

    for i in props:

        result = {}
        err_msg = ''.join(['Error in ',
                           ''.join(str(date_obj).split('-')),
                           ' at prop \"', str(prop_num),
                           '\"\n\t',
                           'problem getting --> '])


        # if prop was not 'final', i.e. cancelled or postponed then skip here
        try:
            if i.select('table tbody')[0].select('tr td.mg-column5 div.matchupStatus a') == [] or \
                    not i.select('table tbody')[0].select('tr td.mg-column5 div.matchupStatus a')[0].text == 'Final':
                continue
        except Exception as e:
            print err_msg + '"Final" status of prop'
            print str(e)
            sys.exit(0)


        try:
            # Check if home team exists
            home_team_exists = 1 if i.select(
                                            'table tbody')[0].select(
                                            'tr td.mg-column3')[1].select(
                                            'span strong')[0].text[0] == '@' else 0
        except Exception as e:
            print err_msg + 'existence of home team'
            print str(e)
            sys.exit()


        try:
            # first add date
            start_time = re.findall('(\d+):(\d+) (\w+)', i.select('table tbody tr td.mg-column1 span.startTime')[0].text)[0]

            date = {'year': date_obj.year,
                    'month': date_obj.month,
                    'day': date_obj.day,
                    'time': {'hour': int(start_time[0]) + 12 if start_time[2] == 'PM' else int(start_time[0]),
                             'minute': int(start_time[1])}}
            result['date'] = date
        except Exception as e:
            print err_msg + 'date'
            print str(e)
            sys.exit()


        try:
            # Sport Type
            if not i.select('div.gamequestion strong') == []:
                desc = i.select('div.gamequestion strong')[0].text.split(':')
            elif not i.select('div.spons-bgGame div.left strong') == []:
                desc = i.select('div.spons-bgGame div.left strong')[0].text.split(':')
            else:
                desc = i.select('div.fanMatchupOfTheDay div.left strong')[0].text.split(':')
            result['sport'] = desc[0].strip()
            if len(desc) > 1:
                result['sport'] = desc[0].strip()
        except Exception as e:
            print err_msg + 'sport type'
            print str(e)
            sys.exit()


        try:
            # Sport Question
            if len(desc) < 2:
                result['question'] = desc[0].strip()
            else:
                result['question'] = desc[1].strip()
        except Exception as e:
            print err_msg + 'sport question'
            print str(e)
            sys.exit()


        try:
            # Network where prop is shown
            result['network'] = i.select('table tbody tr td.mg-column1 div.network')[0].text
        except Exception as e:
            print err_msg + 'network'
            print str(e)
            sys.exit()


        try:
            # Short Sport Descriptor (if exists)
            desc_region = i.select('table tbody')[0].select('tr td.mg-column2 div.sport-description')
            if len(desc_region) > 0:
                result['description'] = desc_region[0].text
            else:
                result['description'] = ''
        except Exception as e:
            print err_msg + 'sport description'
            print str(e)
            sys.exit()



        try:
            # Did the home team win?
            home_team_won = False if i.select(
                                                'table tbody')[0].select(
                                                'tr td.mg-column3 span')[0].find('img') else True
            result['home_team_won'] = home_team_won
        except Exception as e:
            print err_msg + 'which team won'
            print str(e)
            sys.exit()


        try:
            # Winning Side
            result['winner'] = {}

            result['winner']['team'] = get_team_name(i, home_team_won)
        except Exception as e:
            print err_msg + 'winning side'
            print str(e)
            sys.exit()


        try:
            # Losing Side
            result['loser'] = {}

            result['loser']['team'] = get_team_name(i, not home_team_won)
        except Exception as e:
            print err_msg + 'losing side'
            print str(e)
            sys.exit()


        try:
            # Get team ranking
            pattern = re.compile(r'#(\d+)')
            home_rank = i.select(
                                'table tbody')[0].select(
                                'tr td.mg-column3')[home_team_won].select(
                                'span strong')[0].text

            not_home_rank = i.select(
                                    'table tbody')[0].select(
                                    'tr td.mg-column3')[not home_team_won].select(
                                    'span strong')[0].text

            if pattern.search(home_rank) is not None:
                result['winner']['ranking'] = int(re.findall(pattern, home_rank)[0])
            if pattern.search(not_home_rank) is not None:
                result['loser']['ranking'] = int(re.findall(pattern, not_home_rank)[0])
        except Exception as e:
            print err_msg + 'team ranking if it exists'
            print str(e)
            sys.exit()


        try:
            # Get team current record
            home_record = i.select(
                                    'table tbody')[0].select(
                                    'tr td.mg-column3')[home_team_won].select(
                                    'span span#oppAddlText')

            not_home_record = i.select(
                                        'table tbody')[0].select(
                                        'tr td.mg-column3')[not home_team_won].select(
                                        'span span#oppAddlText')

            get_team_record(result, home_record, 'winner')
            get_team_record(result, not_home_record, 'loser')
        except Exception as e:
            print err_msg + 'team win/loss record if exists'
            print str(e)
            exit(0)

        if home_team_exists:
            result['winner']['home'] = 1 if home_team_won else 0
            result['loser']['home'] = 0 if home_team_won else 1

        try:
            # Winning Side Score
            score = i.select('table tbody')[0].select('tr td.mg-column4')[home_team_won].text
            if not score == '--':
                result['winner']['score'] = float(score)
        except Exception as e:
            print err_msg + 'winning score'
            print str(e)
            sys.exit()


        try:
            # Losing Side Score
            score = i.select('table tbody')[0].select('tr td.mg-column4')[not home_team_won].text
            if not score == '--':
                result['loser']['score'] = float(score)
        except Exception as e:
            print err_msg + 'losing score'
            print str(e)
            sys.exit()


        # if the result was a draw, do not record this prop
        if ('score' in result['winner'] and
                result['winner']['score'] == result['loser']['score']):
            continue


        try:
            # Winning Side Percentage Picked
            result['winner']['percent'] = float(i.select(
                                                        'table tbody')[0].select(
                                                        'tr td.mg-column6 span.wpw')[home_team_won].text.strip('%'))
        except Exception as e:
            print err_msg + 'winning percentage picked'
            print str(e)
            sys.exit()


        try:
            # Losing Side Percentage Picked
            result['loser']['percent'] = float(i.select(
                                                        'table tbody')[0].select(
                                                        'tr td.mg-column6 span.wpw')[not home_team_won].text.strip('%'))
        except Exception as e:
            print err_msg + 'losing percentage picked'
            print str(e)
            sys.exit()


        try:
            # Winning Team Stipulation
            j = i.select('table tbody')[0].findAll(
                                                    'tr')[home_team_won].select(
                                                    'td.mg-column3 span')[1].select(
                                                    'strong')[0].text.split(':')
            if len(j) > 1:
                result['winner']['stip'] = i.select(
                                                    'table tbody')[0].findAll('tr')[home_team_won].select(
                                                    'td.mg-column3 span')[1].select(
                                                    'strong')[0].text.split(':')[1].strip()
        except Exception as e:
            print err_msg + 'winning team stipulation if exists'
            print str(e)
            sys.exit()


        try:
            # Loser Team Stipulation
            k = i.select('table tbody')[0].findAll(
                                                    'tr')[not home_team_won].select(
                                                    'td.mg-column3 span')[1].select(
                                                    'strong')[0].text.split(':')
            if len(k) > 1:
                result['loser']['stip'] = i.select(
                                                    'table tbody')[0].findAll('tr')[not home_team_won].select(
                                                    'td.mg-column3 span')[1].select(
                                                    'strong')[0].text.split(':')[1].strip()
        except Exception as e:
            print err_msg + 'losing team stipulation if exists'
            print str(e)
            sys.exit()

        try:
            # Popularity of pick
            result['popularity'] = float(re.findall('(\d+.\d+)%', i.select(
                                                                            'table tbody')[0].select(
                                                                            'tr td.mg-column7 div div')[0]['title'])[0])
        except Exception as e:
            print err_msg + 'popularity of pick'
            print str(e)
            sys.exit()

        full_results.append(result)
        prop_num += 1
        #pprint(result)
    return full_results


def get_time_period(start):
    assert start <= date.today()
    assert start >= date(2008, 8, 25)

    # 'http://streak.espn.go.com/en/?date=yyyymmdd'
    return scrape_page('http://streak.espn.go.com/en/?date=', start)

'''
result = 'Georgia Southern Eagles (56-11)'
pattern = re.compile(r'(?:\#\d+)?(?:\(\d+\))?\s?(.*)(?:\s\(\d+\-\d+(?:\-\d+)?\))')
print pattern.findall(result)


team1 = '#6 Roberto Bautista-Agut'
team2 = 'Roberto Bautista-Agut'
team3 = '15 or fewer'
print pattern.findall(team1)
print pattern.findall(team2)
print pattern.findall(team3)


date1 = date(2015, 2, 10)
date2 = date(2016, 2, 10)
from datetime import timedelta
#get_time_period(date(2008, 9, 3))
while date1 <= date2:
    get_time_period(date1)
    print "Successfully logged: ", date1.isoformat()
    date1 += timedelta(days=1)
'''