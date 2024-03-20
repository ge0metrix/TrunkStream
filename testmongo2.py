from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient("mongodb+srv://TrunkStreamer:1zxQx4BMrxueXT8q@adamtestmongo.yqkybba.mongodb.net/?retryWrites=true&w=majority")
result = client['TrunkStream']['Calls'].aggregate([
    {
        '$addFields': {
            'has_tones': '$tones.has_tones'
        }
    }, {
        '$match': {
            'has_tones': True, 
            'transcript': {
                '$ne': None
            }
        }
    }, {
        '$unwind': {
            'path': '$srcList', 
            'includeArrayIndex': 'string', 
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$project': {
            'talkgroup_tag': 1, 
            'talkgroup': 1, 
            'source': '$srcList.src', 
            'source_tag': '$srcList.tag', 
            'start_time': 1, 
            'stop_time': 1, 
            'shortname': 1, 
            'filepath': 1, 
            'quick_call': '$tones.quick_call', 
            'hi_low': '$tones.hi_low', 
            'long': '$tones.long', 
            'transcript': '$transcript.transcript'
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

for r in result:
    print(r)