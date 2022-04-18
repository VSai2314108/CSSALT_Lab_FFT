import PySimpleGUI as sg
import pyaudio
import numpy as np
import wave
import struct

""" RealTime Audio Basic FFT plot """
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([])}

# Initialization of the graphical component of the application
AppFont = 'Any 16'
sg.theme('Black')
CanvasSizeWH = 800 #modify this value to increase or decrease dimentions of the window (400-1200)

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

# Variables that can be changes:
CHUNK = 512  # Values: 1024,  512, 256, 128 -> (dont modify) higher values create slower datapoints as more values are inputted to FFT matrix
RATE = 1000  # Hz that are monitored -> can be modified up to 44000
BUCKETS = 10 # splits RATE into this many groups -> can be modified experimentally
SHIFTUP = 0 # Number of Buckets on the lower edge of the spectrum that are ignored -> can be modified up to BUCKETS-1

INTERVAL = 1  #Default Value for sampling - don't change
TIMEOUT = 10  # Default Value for cycles - don't change
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
rl = 50 # number of cycles in each calculated period - can be changed - must be less than bl
bl = 250 # number of cycles in base line period - can be changed
graphDB = []
graphAVG = 1000
# FUNCTIONS - DO NOT MODIFY:
def drawAxis():
    graph.DrawLine((0, 0), (100, 0))  # Y Axis
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

def drawFFT():
    global graphDB
    global graphAVG

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
            #if(bucket >= SHIFTUP):
               #graph.draw_rectangle(top_left=(bucket*barStep, acc/dpinB+50),
                  # bottom_right=((bucket+1)*barStep, 50),
                   #fill_color='black')
            i=0
            for val in graphDB:
                graph.DrawCircle((i,(val/graphAVG)*50),1,fill_color='black',line_color='white')
                i=i+1
             
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

#Alarm function 
def alarm():
    global alertc
    global alarmb
    global cb
    global dbc
    global alarmdb
    r_Max = rData.index(max(rData[SHIFTUP+1:]))
    b_Max = bData.index(max(bData[SHIFTUP+1:]))
    graph.DrawText(r_Max,(30,100))
    graph.DrawText(b_Max,(20,100))
    graph.DrawText(cb,(10,100))
    #graph.DrawText(int(rMax),(30,50))
    #graph.DrawText(int(bMax),(20,50))
    bdif = 3; #difference in buckets for the alarm counter to be incremented -> change expeirmentally to alter sensitivity 
    ddif = 0.25; #this value times a hundred is percentage change in decibels to trigger alarm -> change experiemntally 
    fqcyc = 50; #number of cycles that the frequencey alarm counter must be triggered -> change expeirmentally to alter sensitivity
    dcyc = 10; #number of cycles that the decibels most be substantically different -> change experimentally
    if(abs(b_Max-r_Max)>=bdif and cb>=bl):
        alertc+=1
    if(((rMax-bMax)/bMax)>=ddif and cb>=bl):
        dbc+=1
    if(alertc>=fqcyc):
        alarmb = True
    if(dbc>=dcyc):
        alarmdb = True
    if(cb<=bl):
        graph.DrawText('Base', (50, 100), color='white')
    elif(alarmb):
        graph.DrawText('Alarm', (50, 100), color='red')
    else:
         graph.DrawText('Alarm', (50, 100), color='white')

#do not chane anything below this
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
    
def updateUI():
    global graphDB
    global graphAVG
    # Uodate volumne meter
    _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
    graphDB.append(float(np.amax(_VARS['audioData'])))
    if(len(graphDB)>=100):
        graphDB = graphDB[1:]
    if(len(graphDB)==0 or sum(graphDB)==0):
        graphAVG=100
    else:
        graphAVG = sum(graphDB)/len(graphDB)
    # Redraw plot
    graph.erase()
    drawAxis()
    #drawTicks()
    #drawAxesLabels()
    drawFFT()
    alarm()

# INIT:
drawAxis()
#drawTicks()
#drawAxesLabels()

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