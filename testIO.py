import pyaudio
import sounddevice as sd
print(sd.query_devices())
pa = pyaudio.PyAudio()
print(pa.get_default_host_api_info())
