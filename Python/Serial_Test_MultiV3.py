import serial #Import Serial Library
import time
import datetime
import csv
import numpy as np

run = '1'
count = 0
badSamples = 0
NO_SAMPLES = 25
NO_SENSORS = 5
NO_AXES = 3
START = 'S'

HEADER = [ ['Sensor 1',' ',' ','Sensor 2',' ',' ','Sensor 3',' ',' ','Sensor 4',' ',' ','Sensor 5'],
           ['X','Y','Z','X','Y','Z','X','Y','Z','X','Y','Z','X','Y','Z'] ]

CONVERSION = [ [101.6879,101.7174,101.7665,-4.9693,-5.0167,-5.0736],
               [99.9355,101.946,102.7925,-5.0840,-4.9925,-5.0007],
               [102.498,103.065,104.0235,-4.9416,-4.9001,-4.9225],
               [99.842,101.169,100.999,-5.0621,-5.0204,-5.1243],
               [100.052,102.312,101.709,-5.8678,-4.8937,-5.1263] ]

data_log = []
length = []

try:
    arduinoSerial = serial.Serial('/dev/tty.usbserial-DN018OOF',9600, 5) #Create Serial port object called arduinoSerialData
    print("Connected to Arduino")
except:
    print("Failed to connect to Arduino")

arduinoSerial.reset_input_buffer()
arduinoSerial.reset_output_buffer()
time.sleep(5)   #Required for the XBee's to initialise

input('Please press Enter to begin')
arduinoSerial.write(b'S')

while (run == '1'):
	# If the input buffer is not empty read the data out into rawData using \n as a delimiter.
    if (arduinoSerial.inWaiting()>0):
        rawData = arduinoSerial.readline()
        # Decode the bytes into a string
        data = rawData.decode()
        # Split the ID, x, y, z and newline values and put in a list
        data_readings = data.split(" ", 5)
        print(data_readings)
        if (len(data_readings) == 5 and '' not in data_readings):
            int_data_readings = list(map(int,data_readings[:4]))
            data_log.append(int_data_readings)
        else:
            badSamples += 1

        # Take NO_SAMPLES samples then possibility to quit
        if (count == NO_SAMPLES):
            print('Lost Samples: ' + str(badSamples))
            run = input('Continue? (1:yes, 0:no)')
            count = 0
        count += 1

arduinoSerial.write(b'S')
arduinoSerial.close()

np_data_log = np.array(data_log)

for i in range(1,NO_SENSORS+1):
    length.append((np_data_log == i).sum())

np_difference = max(length) - np.array(length)

for i in range(0,NO_SENSORS):
    if (np_difference[i] != 0):
        for j in range(0,np_difference[i]):
            np_data_log = np.concatenate((np_data_log,[[i+1,0,0,0]]), axis=0)

np_data_sorted = np_data_log[:,[1,2,3]][np_data_log[:,0] == 1 ]
for i in range(2,NO_SENSORS+1):
    np_temp = np_data_log[:,[1,2,3]][np_data_log[:,0] == i ]
    np_data_sorted = np.concatenate((np_data_sorted,np_temp), axis=1)

np_data_g = np_data_sorted.astype(np.float16)

for i in range(0,NO_SENSORS):
    for j in range(0,NO_AXES):
        np_data_g[:,j+(3*i)] = ((np_data_g[:,j+(3*i)]/CONVERSION[i][j]) + CONVERSION[i][j+3])

timestamp = datetime.datetime.utcnow()
pathTime = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor1log-{:%d%b,%H.%M}.csv'.format(timestamp)

path = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensorlog.csv'

name = 'Sensor5(X-0g,Y-1g,Z-0g)'
pathName = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'+name+'.csv'

with open(path, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerows(HEADER)
    csv_write.writerows(np_data_g)















