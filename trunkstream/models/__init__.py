
from .call import *
from .source import *
from .frequency import *
from .tones import *

def mock_call(x:int=0) -> Call:
    import json
    from pprint import pprint
    j = '''
{
"id": ''' + str(x) + ''',
"freq": 483125000,
"start_time": 1709424137,
"stop_time": 1709424148,
"emergency": 0,
"priority": 0,
"mode": 0,
"duplex": 0,
"encrypted": 0,
"call_length": 11,
"talkgroup": 1,
"talkgroup_tag": "Westford Police",
"talkgroup_description": "",
"talkgroup_group_tag": "",
"talkgroup_group": "",
"audio_type": "analog",
"short_name": "Westford",
"freqList": [ {"freq": 483125000, "time": 1709424137, "pos": 0.00, "len": 6.43, "error_count": "0", "spike_count": "0"}, {"freq": 483125000, "time": 1709424143, "pos": 6.43, "len": 3.07, "error_count": "0", "spike_count": "0"}, {"freq": 483125000, "time": 1709424146, "pos": 9.50, "len": 1.57, "error_count": "0", "spike_count": "0"} ],
"srcList": [ {"src": 0, "time": 1709424137, "pos": 0.00, "emergency": 0, "signal_system": "", "tag": "Dispatch"}, {"src": 8960, "time": 1709424143, "pos": 6.43, "emergency": 0, "signal_system": "", "tag": ""}, {"src": 0, "time": 1709424146, "pos": 9.50, "emergency": 0, "signal_system": "", "tag": "Dispatch"} ]
}
'''
    data = json.loads(j)
    call = Call(**data)
    return(call)


#__all__ = ["Call", "mock_call", "Source", "Frequency", "DetectedTones", "QuickCall", "LongTone", "HiLow", "DTMFTone"]

