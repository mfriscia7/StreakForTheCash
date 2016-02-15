from main import get_db

db = get_db()
w = len(db.find({'winner.team': {'$regex': 'Tottenham'}}, {}))
