import PySimpleGUI as sg
import pyaudio
import numpy as np
import wave
import struct

""" RealTime Audio Basic FFT plot """

# VARS CONSTS:
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([])}

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('Black')
CanvasSizeWH = 800

#wav file 
wf = wave.open("DBS4.wav", 'rb')

layout = [[sg.Graph(canvas_size=(CanvasSizeWH, CanvasSizeWH),
                    graph_bottom_left=(-16, -16),
                    graph_top_right=(116, 116),
                    background_color='#B9B9B9',
                    key='graph')],
          [sg.ProgressBar(4000, orientation='h',
                          size=(20, 20), key='-PROG-')],
          [sg.Button('Listen', font=AppFont),
           sg.Button('Stop', font=AppFont, disabled=True),
           sg.Button('Exit', font=AppFont),
           sg.Button('Base', font=AppFont),
           sg.Button('Reset',font=AppFont)]]
_VARS['window'] = sg.Window('Dopple FFT Transform',
                            layout, finalize=True)

graph = _VARS['window']['graph']

# INIT vars:
CHUNK = 512  # Samples: 1024,  512, 256, 128
RATE = 1000  # Hz that are monitored
BUCKETS = 10 # splits 1000/10 as range of each bucket ie 100hz
SHIFTUP = 0 # Bucket size * this value is HZ ignored

INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 10  # In ms for the event loop
GAIN = 10
pAud = pyaudio.PyAudio()

#alrm and base vars used to signal an alarm
cb = 0
bData = [0]*(BUCKETS+1)
rData = [0]*(BUCKETS+1)
bMax = 0
rMax=0
alarmb = False
alarmdb = False
alertc = 0
dbc=0
rl = 50
bl = 250
# FUNCTIONS:


def drawAxis():
    graph.DrawLine((0, 50), (100, 50))  # Y Axis
    graph.DrawLine((0, 0), (0, 100))  # X Axis


def drawTicks():

    divisionsX = BUCKETS
    multi = int(RATE/divisionsX)
    offsetX = int(100/divisionsX)

    divisionsY = 10
    offsetY = int(100/divisionsY)

    for x in range(0, divisionsX+1):
        # print('x:', x)
        graph.DrawLine((x*offsetX, -3), (x*offsetX, 3))
        graph.DrawText(int((x*multi)), (x*offsetX, -10), color='black')

    for y in range(0, divisionsY+1):
        graph.DrawLine((-3, y*offsetY), (3, y*offsetY))


def drawAxesLabels():
    graph.DrawText('kHz', (50, 10), color='black')
    graph.DrawText('Scaled DB', (-5, 50), color='black', angle=90)


# def drawPlot():
#     # Divide horizontal axis space by data points :
#     barStep = (100/CHUNK)
#     x_scaled = ((_VARS['audioData']/100)*GAIN)+50

#     for i, x in enumerate(x_scaled):
#         graph.draw_rectangle(top_left=(i*barStep, x),
#                              bottom_right=(i*barStep+barStep, 50),
#                              fill_color='#B6B6B6')


def drawFFT():

    # Not the most elegant implementation but gets the job done.
    # Note that we are using rfft instead of plain fft, it uses half
    # the data from pyAudio while preserving frequencies thus improving
    # performance, you might also want to scale and normalize the fft data
    # Here I am simply using hardcoded values/variables which is not ideal.

    barStep = 100/BUCKETS  # Needed to fit the data into the plot.
    fft_data = np.fft.rfft(_VARS['audioData'])  # The proper fft calculation
    fft_data = np.absolute(fft_data)  # Get rid of negatives
    fft_data = (50*fft_data)/np.amax(fft_data)  # normalize data to 0-1 range and scale by max(abs(y-axis))
    dpinB = int((CHUNK/2)/BUCKETS)
    #baseline
    global cb
    global rData
    global bData
    global rl
    global bl
    global bMax
    global rMax
    
    #bucket and display
    counter = 0
    acc = 0
    bucket=0
    
    #counter operations
    if(cb%rl==0):
        rData = [0]*(BUCKETS+1)
        rMax = 0
    for i, x in enumerate(fft_data):
        if (counter == dpinB):
            if(bucket >= SHIFTUP):
                graph.draw_rectangle(top_left=(bucket*barStep, acc/dpinB+50),
                    bottom_right=((bucket+1)*barStep, 50),
                    fill_color='black')
            #modify base or and data
            if(cb<bl):
                bData[bucket]=bData[bucket]+((acc/dpinB)/bl)
                bMax += ((acc/dpinB)/bl)
            rData[bucket]=(rData[bucket]+((acc/dpinB)/rl))
            rMax += ((acc/dpinB)/rl)

                
           #increment the bucket variables     
            counter = 1
            acc = x
            bucket +=1
        else:
            acc+=x
            counter+=1
    myState = _VARS['window']['Stop']
    if(str(myState.Widget['state']) == 'normal'):
        cb+=1

def alarm():
    global alertc
    global alarmb
    global cb
    global dbc
    global alarmdb
    r_Max = rData.index(max(rData[SHIFTUP+1:]))
    b_Max = bData.index(max(bData[SHIFTUP+1:]))
    graph.DrawText(r_Max,(30,80))
    graph.DrawText(b_Max,(20,80))
    graph.DrawText(cb,(10,80))
    #graph.DrawText(int(rMax),(30,50))
    #graph.DrawText(int(bMax),(20,50))
    if(abs(b_Max-r_Max)>=3 and cb>=bl):
        alertc+=1
    if(((rMax-bMax)/bMax)>=0.25 and cb>=bl):
        dbc+=1
    if(alertc>=50):
        alarmb = True
    if(dbc>=10):
        alarmdb = True
    if(cb<=bl):
        graph.DrawText('Base', (50, 80), color='white')
    elif(alarmb):
        graph.DrawText('Alarm', (50, 80), color='red')
    else:
         graph.DrawText('Alarm', (50, 80), color='white')

def reset():
    global alertc
    global alarmb
    global dbc
    global alarmdb
    alertc = 0
    dbc = 0
    alaramdb = False
    alarmb = False
    

# PYAUDIO STREAM :
def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Stop').Update(disabled=True)
        _VARS['window'].FindElement('Listen').Update(disabled=False)


def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)


def listen():
    _VARS['window'].FindElement('Stop').Update(disabled=False)
    _VARS['window'].FindElement('Listen').Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)
    _VARS['stream'].start_stream()
    

    
    
# def callbacktwo(in_data, frame_count, time_info, status):
#     data = wf.readframes(CHUNK)
#     data_unpacked = struct.unpack('{n}h'.format(n= len(data)/2 ), data) 
#     data_np = np.array(data_unpacked) 
#     data_fft = np.fft.fft(data_np)
#     _VARS['audioData'] = data_fft
#     return (in_data, pyaudio.paContinue)

# def filefunc():
#     _VARS['window'].FindElement('Stop').Update(disabled=False)
#     _VARS['window'].FindElement('Ffile').Update(disabled=True)
#     _VARS['stream'] = pAud.open(format =
#                 pAud.get_format_from_width(wf.getsampwidth()),
#                 channels = wf.getnchannels(),
#                 rate = wf.getframerate(),
#                 input = False,
#                 output = True,
#                 stream_callback=callbacktwo)


def updateUI():
    # Uodate volumne meter
    _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
    # Redraw plot
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()
    drawFFT()
    alarm()

# INIT:
drawAxis()
drawTicks()
drawAxesLabels()

# MAIN LOOP
while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    if event == 'Listen':
        listen()
    if event == 'Base':
        cb = 0
        bData = [0]*(BUCKETS+1)
    if event == 'Reset':
        reset()
    if event == 'Stop':
        stop()
    elif _VARS['audioData'].size != 0:
        updateUI()


_VARS['window'].close()