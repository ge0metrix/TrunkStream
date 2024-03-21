from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient("mongodb+srv://TrunkStreamer:1zxQx4BMrxueXT8q@adamtestmongo.yqkybba.mongodb.net/?retryWrites=true&w=majority")
"""result = client['TrunkStreamArchive']['Calls'].aggregate([
    {
        '$addFields': {
            'has_tones': '$tones.has_tones'
        }
    }, {
        '$match': {
            'has_tones': True
        }
    }
])
"""
"""
result = client['TrunkStreamArchive']['Calls'].aggregate([
    {
        '$addFields': {
            'has_tones': '$tones.has_tones'
        }
    }, {
        '$match': {
            'has_tones': True, 
            'talkgroup_tag': 'Westford Police'
        }
    }, {
        '$project': {
            'has_tones': 1, 
            'talkgroup_tag': 1, 
            'tones': 1, 
            'start_time': 1, 
            'quick_call': '$tones.quick_call', 
            'hi_low': '$tones.hi_low', 
            'long': '$tones.long'
        }
    }, {
        '$unwind': {
            'path': '$quick_call', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$unwind': {
            'path': '$hi_low', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$unwind': {
            'path': '$long', 
            'preserveNullAndEmptyArrays': True
        }
    }
])
x=0

for r in result:
    x += 1
    print(r)

print(x)"""


result = client['TrunkStream']['Calls_Archive'].aggregate([
    {
        '$match': {
            '$and': [
                {
                    'talkgroup_tag': 'Westford Police'
                }, {
                    'transcript': {
                        '$ne': None
                    }
                }
            ]
        }
    }, {
        '$project': {
            'talkgroup_tag': 1, 
            'start_time': 1, 
            'transcript': '$transcript.transcript'
        }
    }, {
        '$sort': {
            'start_time': -1
        }
    }
])

for r in result:
    print(r.get("start_time"), r.get("transcript"))