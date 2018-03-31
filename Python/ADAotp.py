# -*- coding: UTF-8 -*-
"""
import <module_name>                        -->     Need to refer to <module_name> inorder to use inclued functions e.g. serial.Serial()
from <module_name> import <function_name>   -->     The <function_name> can be used directly without reference to its <module_name>
from <module_name> import *                 -->     All the the functions inclued in the <module_name>
                                                    can be used used directly without reference to its <module_name>
"""
import random # Used for create_plots function (test purpose)
import serial # Need to make a refrence to it in order to use one of its function e.g. serial.Serial()

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import Tkinter as tk
import ttk

import csv
import datetime
import os


T1_Arr=[]  # Create an empty array for saving temperatures values
I1_Arr=[]  # Create an empty array for saving current values
H1_Arr=[]  # Create an empty array for saving Hydrogen values
P1_Arr=[]  # Create an empty array for saving Hydrogen values

sensorList = [T1_Arr,I1_Arr,H1_Arr,P1_Arr]


LARGE_FONT = ("Verdana",12)
NORM_FONT = ("Verdana",10)
SMALL_FONT = ("Verdana",8)

style.use('seaborn-darkgrid')

# --- default values ---
portCOM = 'com14'
baudRate = 115200
sampleSize = 50

arduinoData = serial.Serial()    #Creating our serial object named arduinoData
# ---

dataFileName = 'Data_log.csv'
saveData = False
saveInitalData = False


f = Figure()

##a = f.add_subplot(111)
##b = f.add_subplot(111)
##c = f.add_subplot(111)
##d = f.add_subplot(111)

a = f.add_subplot(221)
b = f.add_subplot(222)
c = f.add_subplot(223)
d = f.add_subplot(224)

subPlotArr = [a,b,c,d]

# --------------------------
# function for test purposes only

def qf(stringtoprint): # print a text in the python shell
    print(stringtoprint)
    
def create_plots(plotNumber, amplitude): # create random x, y values ; need random lib
    xs = []
    ys = []

    for i in range(plotNumber):
        x = i
        y= random.randrange(amplitude)

        xs.append(x)
        ys.append(y)
    return xs, ys

# --------------------------


def choosePort(): # Allow the user to choose the serial port for serial communication
    
    if arduinoData.isOpen() == True:
        print (arduinoData.isOpen())
        popupmsg('Serial port {} already opened. Close connection prior to change port.'.format(portCOM))

    else:
        portComQ =tk.Tk()
        portComQ.wm_title('Serial port?')
        label = ttk.Label(portComQ, text = "Choose the serial port to listen.")
        label.pack(side="top", fill="x", pady=10)
        

        e = ttk.Entry(portComQ)
        e.insert(0,portCOM[3:]) # Getting the port number from the String
        e.pack()
        e.focus_set()

        def callback():
            global portCOM
            portCOM = 'com' + str(e.get())
            print('Port {} is now selected.'.format(portCOM))
            portComQ.destroy()
            
        b = ttk.Button(portComQ, text='Submit', width=10, command=callback)
        b.pack()
        tk.mainloop()
    

def chooseBaudRate(): # Allow the user to choose the baud rate of the serial communication
    if arduinoData.isOpen() == True:
        print (arduinoData.isOpen())
        popupmsg('Serial port {} already opened at {} baud. Close connection prior to change baud rate.'.format(portCOM,baudRate))

    else:
        baudRateQ =tk.Tk()
        baudRateQ.wm_title('Baud rate?')
        label = ttk.Label(baudRateQ, text = "Specify the baud rate value.")
        label.pack(side="top", fill="x", pady=10)

        e = ttk.Entry(baudRateQ)  
        e.insert(0,baudRate)
        e.pack()
        e.focus_set()

        def callback():
            global baudRate
            baudRate = e.get()
            print('{} baudrate is now selected'.format(baudRate))
            baudRateQ.destroy()
            
        b = ttk.Button(baudRateQ, text='Submit', width=10, command=callback)
        b.pack()
        tk.mainloop()


def chooseSampleSize(): # Allow the user to choose the sample size of displayed values
    sampleSizeQ =tk.Tk()
    sampleSizeQ.wm_title('Sample size?')
    label = ttk.Label(sampleSizeQ, text = "Specify the sample size of displayed values.")
    label.pack(side="top", fill="x", pady=10)

    e = ttk.Entry(sampleSizeQ)
    e.insert(0,sampleSize)
    e.pack()
    e.focus_set()
    

    def callback():
        global sampleSize
        sampleSize = int(e.get())
        print('Sample size is now {}'.format(sampleSize))
        sampleSizeQ.destroy()

##    e.bind("<Return>", callback)
        
    b = ttk.Button(sampleSizeQ, text='Submit', width=10, command=callback)
    b.pack()
    tk.mainloop()
    

# --- Now working !!! ---
def openSerialPort(portCom, baudRate, openState): # Should open a serial communication with the portCom and baudRate defined
    global arduinoData
    
    if openState == True:
        if arduinoData.isOpen() == False:
            arduinoData.port = portCOM
            arduinoData.baudrate = baudRate
##            arduinoData.timeout = 1
            try:
                arduinoData.open()
            except:
                popupmsg('Unable to open serial port {}. Please check connection.'.format(arduinoData.port))
            else:
                print('Port {} is now opened'.format(arduinoData.port))
                
    elif openState == False:
        if arduinoData.isOpen() == True:
            try:
                arduinoData.close()
            except:
                popupmsg('Unable to close serial port {}. Please check connection.'.format(arduinoData.port))
            else:
                print('Port {} is now closed'.format(arduinoData.port))
        else:
            popupmsg('Serial port {} already closed.'.format(arduinoData.port))
            
# -----------------------    

    

def saveDataAsCSV(state): # Create a new csv file for saving data.
    global dataFileName
    global saveData
    if arduinoData.isOpen() == True:
        
        if state == True and saveData == False: # Create the file name.
            print("START recording data...")
            dataFileName = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
            saveData = True
            print(dataFileName)
            
        elif state == False and saveData == True: # Close the csv file and rename it with the actual time code format.
            saveData = False
            dataFileNameClosed = 'Data_log_ {date:%Y-%m-%d_%H-%M-%S}.csv'.format( date=datetime.datetime.now() )
            os.rename(dataFileName, dataFileNameClosed)
            print("STOP recording data and saving record as csv file.")
            print(dataFileNameClosed)
    else:
        popupmsg('No serial port opened. No data to record!')

        

def popupmsg(msg): # Popup the given message "msg"
    print(msg)
    popup = tk.Tk()

    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10, anchor="center")
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()
    

def clearSubPlot(subPlotToClear): # Clear all subplot in 
    for subPlot in subPlotToClear:
        subPlot.clear()
        

def storeSensorData(dataToStore, listToAppend ):    # Store received sensor values <dataToStore> to the list to append <listToAppend>
    for i in range(len(dataToStore)):
        listToAppend[i].append(float(dataToStore[i]))


def resizeSample(arrayListToResize, sampleSize):
    while(len(arrayListToResize[0])>sampleSize):     
        for i in range(len(arrayListToResize)):
            arrayListToResize[i].pop(0)         # If you have "sampleSize" or more points, delete the first one from the array
    
    
def animate(i): # This function create graph, read data from serial port and update the graph
    if arduinoData.isOpen() == True:
        while (arduinoData.inWaiting()==0):     # Wait here until there is data
            pass
            
        arduinoString = arduinoData.readline()  # read the line of text from the serial port
        dataArray = arduinoString.split(',')    # Split it into an array called dataArray

        storeSensorData(dataArray, sensorList)
        
        clearSubPlot(subPlotArr) # clean the last graph in order to allow the new values to be drawn

        
        a.plot(T1_Arr, 'ro-', label=u'Temp °C' , linewidth=0.5 , markersize=2)   # plot the temperature data
        a.set_title('Temperature')
        a.set_ylim(10,80)
        a.set_ylabel (u'Temperature (°C)')
        
        b.plot(I1_Arr, 'b^-', label='Current mA', linewidth=1 , markersize=2) # plot the current data
        b.set_title('Current')
        b.set_ylim(0,1000)
        b.set_ylabel ('current (mA)')
        
        c.plot(H1_Arr, 'g^-', label='Hydrogen', linewidth=1 , markersize=2) # plot hydrogen data
        c.set_title('Hydrogen')
        c.set_ylim(0,1000)
        c.set_ylabel ('Hydrogen (ppm)')
        
        d.plot(P1_Arr, 'm^-', label='Pressure', linewidth=1 , markersize=2) # plot pressure data
        d.set_title('Pressure')
        d.set_ylim(0,100)
        d.set_ylabel ('Pressure (KPa)')

        
        if (len(sensorList[0]) > sampleSize):
               resizeSample(sensorList, sampleSize)
            

        if saveData ==True: # --- Saving data as csv file --- (see saveDataAsCSV)
            global saveInitalData
            myFile = open(dataFileName,'ab')
            
            if saveInitalData == False:
                try:
                    theWriter = csv.writer(myFile, dialect='excel')
                    i = 0
                    while  i < len(T1_Arr):
                        theWriter.writerow([T1_Arr[i],I1_Arr[i],H1_Arr[i],P1_Arr[i]])
                        i += 1
                    saveInitalData = True
                finally:
                    myFile.close()
                    
            else:
                try:
                    theWriter = csv.writer(myFile, dialect='excel')  
                    theWriter.writerow([T1,I1,H1,P1])
                finally:
                    myFile.close()


class DataLogApp(tk.Tk): # Design of the main application and menubar

    def __init__(self, *arg, **kwargs):

        tk.Tk.__init__(self, *arg, **kwargs)

        tk.Tk.wm_title(self, "Analogue Data Acquisition of the poor")

        container = tk.Frame(self)
        container.pack(side='top', fill="both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0,weight=1)

        menubar = tk.Menu(container)                        # create a container named "menubar" that will contain all menu items
        
        # --- File menu ---
        filemenu = tk.Menu(menubar, tearoff=0)              # create a Menu element named "filemenu"
        filemenu.add_command(label="Save settings", command = lambda: popupmsg("Not supported just yet!")) # add a command button/label labelled "Save setting"
        filemenu.add_separator()                            # add a separator horizontal line in the menu "filemenu"
        filemenu.add_command(label="Exit", command = quit)  # add a command button/label labelled "Exit" and assign the quit command to it
        menubar.add_cascade(label="File", menu=filemenu)    # add the filemenu element to the menubar element

        # --- Record data menu ---
        data_menu = tk.Menu(menubar, tearoff=1)       # create a Menu element named "data_menu"
        data_menu.add_command(label="Start record",   # add a command button/label labelled
                                command = lambda: saveDataAsCSV(True)) 
        data_menu.add_command(label="Stop record",    # add a command button/label labelled
                                command = lambda: saveDataAsCSV(False)) 
        data_menu.add_command(label="Sample size",  # add a command button/label labelled
                                command = chooseSampleSize) 
        data_menu.add_command(label="Clear data",       # add a command button/label labelled 
                                command = lambda: popupmsg("Not supported just yet!")) 
        menubar.add_cascade(label="Data",               # add the data_menu element to the menubar element
                                 menu=data_menu)

        
        # --- Serial port communication menu ---
        serialPort_menu = tk.Menu(menubar, tearoff=1)               # create a Menu element named "serialPort_menu"
        serialPort_menu.add_command(label='Choose port ...',    # add a command button/label labelled "Choose serial port"
                                command = choosePort)
        serialPort_menu.add_command(label= 'Choose baud rate... ', # add a command button/label labelled "Choose baud rate"
                                command = chooseBaudRate)
        serialPort_menu.add_command(label='Open Serial COM...',     # add a command button/label labelled "Start listening"
                                command = lambda: openSerialPort(portCOM,baudRate,True))
        serialPort_menu.add_command(label='Close Serial COM...',     # add a command button/label labelled "Start listening"
                                command = lambda: openSerialPort(portCOM,baudRate,False))
 
        menubar.add_cascade(label="Serial port",                    # add the serialPort_menu element to the menubar element
                                 menu=serialPort_menu) 

        

        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, graph_Page):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        



class StartPage(tk.Frame): # Start page ...

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="""Analogue Data Acquisition of the poor application
        Use at your own risk.
        There is no promise of waranty.""", font= LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self,
                            text="Agree",
                            command=lambda: controller.show_frame(graph_Page))
        button1.pack()
        button2 = ttk.Button(self,
                            text="Disagree",
                            command=quit)
        button2.pack()




class graph_Page(tk.Frame): # Page of the monitoring graph

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

##        container = tk.Frame(self)
        
        self.rowconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        
        tk.Label(self, text = 'Monitoring Page', font=("Verdana",14), padx =10, pady =15).grid(row=0,column=3, rowspan =2)

        self.recordDataLbl = tk.Label(self, text = 'Record data as .csv',font=("Verdana",12))
        self.startBtn = tk.Button(self, text = 'START',  padx =10, pady =5,command = self.startBtnClick)
        self.stopBtn = tk.Button(self, text = 'STOP', background= "red",relief="sunken", padx =10, pady =5,command = self.stopBtnClick)
##        self.serialLbl = tk.Label(self, text = 'Serial',font=("Verdana",12))
##        self.portComLbl = tk.Label(self, text = 'COM14', padx =5, pady =5)
##        self.baudRateLbl = tk.Label(self, text = '115200', padx =5, pady =5)
##        self.connectionLbl = tk.Label(self, text = 'OPEN', bg='green', padx =10, pady =5)

        # création d'un widget 'Canvas' pour l'affichage des graphiques :
##        can1 = tk.Canvas(self, width =160, height =160, bg ='white')

        self.recordDataLbl.grid(row = 0, column = 0, columnspan = 3)
##        self.serialLbl.grid(row = 0, column = 4, columnspan = 3)
##        backBtn.grid(row = 1, column = 0)
        self.startBtn.grid(row = 1, column = 1)
        self.stopBtn.grid(row = 1, column =2 )
##        self.portComLbl.grid(row=1,column=4, sticky='e')
##        self.baudRateLbl.grid(row=1,column=5)
##        self.connectionLbl.grid(row=1,column=6)

##        can1.grid(row =1, column =0, columnspan =7, padx =5, pady =5, sticky='nswe')
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw

        self.canvas.get_tk_widget().grid(row =2, column =0)

##        toolbar = NavigationToolbar2TkAgg(can1, self)
##        toolbar.update()
        self.canvas._tkcanvas.grid(row =2, column =0, columnspan =7, padx =5, pady =5, sticky='nswe')

    def startBtnClick (self):
        if arduinoData.isOpen() == True:
            self.startBtn.configure(background= "green",relief="sunken")
            self.stopBtn.configure(background= "SystemButtonFace",relief="raised")
            saveDataAsCSV(True)
        else:
            popupmsg('No serial port opened. No data to record!')

    def stopBtnClick (self):
        self.startBtn.configure(background= "SystemButtonFace",relief="raised")
        self.stopBtn.configure(background= "red",relief="sunken")
        saveDataAsCSV(False)


##        canvas = FigureCanvasTkAgg(f, self)
##        canvas.draw
##
##        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
##
##        toolbar = NavigationToolbar2TkAgg(canvas, self)
##        toolbar.update()
##        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        
        

app = DataLogApp()
app.geometry("1280x720")
ani = animation.FuncAnimation(f, animate, interval=500)
app.mainloop()
