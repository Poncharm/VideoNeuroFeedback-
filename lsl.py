# External Libraries
from pylsl import StreamInlet, resolve_streams

def list_lsl_streams():
    return resolve_streams()

def get_speed_from_stream(stream_info):
    inlet = StreamInlet(stream_info)
    speed, timestamp = inlet.pull_sample()
    return speed[0]
