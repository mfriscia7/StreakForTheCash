import pymongo
from datetime import date, timedelta
from WebScraping import get_time_period


class StreakDB:

    def __init__(self, dbname):
        self._conn = pymongo.MongoClient('localhost', 27017)
        self._db = self._conn[dbname]
        self.posts = self._db.posts

    def add_date(self, date1):
        self.posts.insert_many(get_time_period(date1))

    def add_dates(self, date1, date2):
        while date1 <= date2:
            self.posts.insert_many(get_time_period(date1))
            print "Successfully logged: ", date1.isoformat()
            date1 += timedelta(days=1)

    def get_coll(self):
        return self.posts


if __name__ == "__main__":
    db = StreakDB("Streak")
    db.add_dates(date(2015, 1, 1), date(2015, 1, 10))

'''
con = pymongo.Connection()
db = con.test_database
people = db.people
people.insert({'name':'Harry'})
peeps = people.find()
#also can do
#peeps = people.find({'name':{'$regex':'.*[Mm]i.*'}})
for person in peeps:
    print person
#update
person = people.find_one({'food':'ham'})
person['food'] = eggs
people.save(person)
#remove
people.remove(person)
'''
