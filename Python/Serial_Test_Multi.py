import serial #Import Serial Library
import datetime
import csv

run = '1'
count = 0
NO_SAMPLES = 10
NO_SENSORS = 3
AXES = 3

x_values1 = []
y_values1 = []
z_values1 = []
x_values2 = []
y_values2 = []
z_values2 = []
x_values3 = []
y_values3 = []
z_values3 = []
x_values4 = []
y_values4 = []
z_values4 = []
x_values5 = []
y_values5 = []
z_values5 = []
#sensorValues = np.zeroes( (NO_SENSORS, NO_SAMPLES, AXES), dtype=np.int16 )
 
arduinoSerial = serial.Serial('/dev/tty.usbserial-DN018OOF',9600, 5) #Create Serial port object called arduinoSerialData
 
while (run == '1'):
	# If the input buffer is not empty read the data out into rawData using \n as a delimiter.
    if (arduinoSerial.inWaiting()>0):
        rawData = arduinoSerial.readline()
        # Decode the bytes into a string
        data = rawData.decode()
        # Split the ID, x, y, z and newline values and put in a list
        readings = data.split(" ", 5)  

        sensorID = readings[0]
        if sensorID == '1':
            x_values1.append(readings[1])
            y_values1.append(readings[2])
            z_values1.append(readings[3])
        elif sensorID == '2':
            x_values2.append(readings[1])
            y_values2.append(readings[2])
            z_values2.append(readings[3])
        elif sensorID == '3':
            x_values3.append(readings[1])
            y_values3.append(readings[2])
            z_values3.append(readings[3])
        elif sensorID == '4':
            x_values4.append(readings[1])
            y_values4.append(readings[2])
            z_values4.append(readings[3])
        elif sensorID == '5':
            x_values5.append(readings[1])
            y_values5.append(readings[2])
            z_values5.append(readings[3])
        
        for reading in readings:
        	print(reading, end="\t")
        print()

        # Take NO_SAMPLES samples then possibility to quit
        if (count == NO_SAMPLES):
        	run = input('Continue? (1:yes, 0:no)')
        	count = 0
        count += 1

arduinoSerial.close()

timestamp = datetime.datetime.utcnow()
path1 = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor1log-{:%d%b,%H.%M}.csv'.format(timestamp)
path2 = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor2log-{:%d%b,%H.%M}.csv'.format(timestamp)
path3 = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor3log-{:%d%b,%H.%M}.csv'.format(timestamp)
path4 = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor4log-{:%d%b,%H.%M}.csv'.format(timestamp)
path5 = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor5log-{:%d%b,%H.%M}.csv'.format(timestamp)

with open(path1, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerow(('Sensor 1',' '))
    csv_write.writerow(('X','Y','Z'))
    for i in range(len(x_values1)):
        csv_write.writerow((x_values1[i],y_values1[i],z_values1[i]))

with open(path2, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerow(('Sensor 2',' '))
    csv_write.writerow(('X','Y','Z'))
    for i in range(len(x_values2)):
        csv_write.writerow((x_values2[i],y_values2[i],z_values2[i]))

with open(path3, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerow(('Sensor 3',' '))
    csv_write.writerow(('X','Y','Z'))
    for i in range(len(x_values3)):
        csv_write.writerow((x_values3[i],y_values3[i],z_values3[i]))

with open(path4, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerow(('Sensor 4',' '))
    csv_write.writerow(('X','Y','Z'))
    for i in range(len(x_values4)):
        csv_write.writerow((x_values4[i],y_values4[i],z_values4[i]))

with open(path5, 'w') as csv_file:
    csv_write = csv.writer(csv_file, dialect='excel')
    csv_write.writerow(('Sensor 5',' '))
    csv_write.writerow(('X','Y','Z'))
    for i in range(len(x_values5)):
        csv_write.writerow((x_values5[i],y_values5[i],z_values5[i]))













