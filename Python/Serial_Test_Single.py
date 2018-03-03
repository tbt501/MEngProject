import serial #Import Serial Library
import csv

run = '1'
count = 0

x_values = []
y_values = []
z_values = []
 
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
        x_values.append(readings[1])
        y_values.append(readings[2])  
        z_values.append(readings[3]) 

        for reading in readings:
        	print(reading, end="\t")
        print()

        # Take 1000 samples then possibility to quit
        if (count == 10):
        	run = input('Continue? (1:yes, 0:no)')
        	count = 0
        count += 1

arduinoSerial.close()

path = "/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/sensorlog.csv"

with open(path, 'w') as csv_file:
		csv_write = csv.writer(csv_file, dialect='excel')
		csv_write.writerow(('X','Y','Z'))
		for i in range(len(x_values)):
			csv_write.writerow((x_values[i],y_values[i],z_values[i]))













