import serial #Import Serial Library
import time
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt


def collect_samples(serialPort,NO_SAMPLES,log):
    """ Saves samples collected from 3-Axis Accelerometers. Samples should be recieved in form (ID X Y Z /r/n) with a space to seperate the data. Invalid data is rejected and any samples lost this way are recorded and displayed to the user once the function finishes.
        All samples are collected from the port defined by the serialPort(string) parameter and the function will continue until it saves a number of samples defined by the NO_SAMPLES(int) parameter.
        All samples will be appended to the list specified by the log(list) parameter. This should either be an empty list or a list with 5 columns.
    """
    run = '1'
    badSamples = 0
    count = 0
    
    while (run == '1'):
        # If the input buffer is not empty read the data out into rawData using \n as a delimiter.
        if (serialPort.inWaiting()>0):
            rawData = serialPort.readline()
            
            # If invalid data is recieved this prevents program crash
            try:
                # Decode the bytes into a string
                data = rawData.decode()
                
                # Split the ID, x, y, z and newline values into a list
                data_readings = data.split(" ", 5)
                print(data_readings)
                
                # A correct sample should contain 5 values and not include null and so this is used
                # to validate the data and record any samples that are discarded in this way
                if (len(data_readings) == 5 and '' not in data_readings):
                    # Discard newline characters before saving data
                    int_data_readings = list(map(int,data_readings[:4]))
                    log.append(int_data_readings)
                else:
                    badSamples += 1
            except:
                print('Invalid data recieved')
            
            # Take NO_SAMPLES samples then possibility to quit
            if (count == NO_SAMPLES):
                print('Lost Samples: ' + str(badSamples))
                run = '0'
            count += 1

def equalise_sample_numbers(np_samples,NO_SENSORS):
    """ A function that takes a numpy array, given by the np_samples(numpy aray) parameter, of samples collected from 3-Axis Accelerometers in the form [ID,X,Y,Z] and returns a numpy area of samples where each ID value has the same amount of samples. Each unique ID relates to an associated sensor and the total number of sensors should be given with the parameter NO_SENSORS(int).
        The function operates by finding the sensor with the least samples and removing the last obtained samples from any other sensors that exceed this amount. This makes further data manipulation and sorting possible.
    """
    
    length = [] # Holds the amount of samples associated with each ID
            
    # Finds the number of samples for each sensor by checking ID and saves the amount in list
    for i in range(1,NO_SENSORS+1):
        length.append((np_samples[:,0] == i).sum())
    
    # Find the ID with the least samples and then calculate how many more samples each ID has
    # than the minimum, saving the difference in np_difference.
    np_difference = np.array(length) - min(length)

    # Removes the final values obtained for each sensor so that each sensor has the same
    # number of samples.
    for i in range(0,NO_SENSORS):
        if (np_difference[i] != 0):
            equal = 0;
            j = -1;
            while(equal < np_difference[i]):
                if (np_samples[j][0] == (i + 1)):
                    np_samples = np.delete(np_samples,j,0)
                    equal += 1
                j -= 1
    return (np_samples)

def sort_samples(np_data,NO_SENSORS):
    """ Sorts a numpy array of 3-Axis Accelerometer data in the form [ID,X,Y,Z] into an array of the following form:
        
                Sensor 1|Sensor 2|.............|Sensor N
                X | Y| Z| X| Y| Z|.............|X |Y |Z
    Sample 1      |  |  |  |  |  |.............|  |  |
    Sample 2      |  |  |  |  |  |.............|  |  |
       .                        .
       .                        .
       .                        .
       .                        .
    Sample N      |  |  |  |  |  |.............|  |  |
    
    A numpy array should be provided to the parameter np_data(numpy array) in the specified form where each ID appears the same number of times. The equalise_sample_numbers can be used to ensure this.
    The number of sensor ID's should also be provided as an int using the NO_SENSORS(int) parameter.
    """

    # Sorts the data into columns as follows X1,Y1,Z1,X2,Y2,Z2 etc.... Each row is then a sample.
    # Sensor 1's samples are added to np_data_sorted first. The for loop then works through
    # each sensor and appends its X,Y,Z values in the next 3 columns of np_data_sorted.
    np_data_sorted = np_data[:,[1,2,3]][np_data[:,0] == 1 ]
    for i in range(2,NO_SENSORS+1):
        np_temp = np_data[:,[1,2,3]][np_data[:,0] == i ]
        np_data_sorted = np.concatenate((np_data_sorted,np_temp), axis=1)
    
    return (np_data_sorted)

def ADC_to_g(np_data,NO_SENSORS):
    """ A function that takes a numpy array of ADC values that relate to N 3-Axis Accelerometers in the form [X1,Y1,Z1,X2,Y2,Z2.....XN,YN,ZN] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter. The ADC values are then converted into g values using predefined constants m and b calculated during calibration. The following conversiion formula is used:
            g= ADC/m + b
        A numpy array of dimension [n][(N*3)] should therfore be provided with np_data(numpy array) and a numpy array of the same dimensions is returned.
    """

    # CONVERSION holds the m and b values calculated during calibration for the X,Y and Z axes of each Sensor.
    CONVERSION = [ [102.006,101.074,103.061,-4.990,-5.025,-5.171],    # [ [mX1B,mY1B,mZ1B,bX1B,bY1B,bZ1B],
                   [99.936,101.946,102.793,-5.084,-4.993,-5.001],     #   [mX2,mY2,mZ2,bX2,bY2,bZ2],
                   [102.498,103.065,104.024,-4.942,-4.900,-4.923],    #   [mX3,mY3,mZ3,bX3,bY3,bZ3],
                   [99.842,101.169,100.999,-5.062,-5.020,-5.124],     #   [mX4,mY4,mZ4,bX4,bY4,bZ4],
                   [100.052,102.312,101.709,-5.087,-4.894,-5.126] ]   #   [mX5,mY5,mZ5,bX5,bY5,bZ5] ]

    # The conversion array is used to transform the samples from ADC to g
    for i in range(0,NO_SENSORS):
        for j in range(0,3):
            np_data[:,j+(3*i)] = ((np_data[:,j+(3*i)]/CONVERSION[i][j]) + CONVERSION[i][j+3])
    
    return (np_data)

def save_as_csv(path,data,NO_SENSORS):
    """ Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,X2,Y2,Z2.....XN,YN,ZN] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*3)] should therfore be provided with np_data(numpy array).
        The array is saved to a CSV file of path defined by the path(string) parameter and given a header as below. The NO_SENSORS should not exceed 5 due to the addition of the header.
    """

    HEADER1 = [ ['Sensor 1',' ',' '],
                ['X','Y','Z'] ]
    HEADER2 = [ ['Sensor 1',' ',' ','Sensor 2',' ',' '],
                ['X','Y','Z','X','Y','Z'] ]
    HEADER3 = [ ['Sensor 1',' ',' ','Sensor 2',' ',' ','Sensor 3',' ',' '],
                ['X','Y','Z','X','Y','Z','X','Y','Z'] ]
    HEADER4 = [ ['Sensor 1',' ',' ','Sensor 2',' ',' ','Sensor 3',' ',' ','Sensor 4',' ',' '],
                ['X','Y','Z','X','Y','Z','X','Y','Z','X','Y','Z'] ]
    HEADER5 = [ ['Sensor 1',' ',' ','Sensor 2',' ',' ','Sensor 3',' ',' ','Sensor 4',' ',' ','Sensor 5'],
                ['X','Y','Z','X','Y','Z','X','Y','Z','X','Y','Z','X','Y','Z'] ]

    HEADERS = [HEADER1,HEADER2,HEADER3,HEADER4,HEADER5]

    HEADER = HEADERS[NO_SENSORS - 1]

    # The  data is saved as a CSV file using the given path
    with open(path, 'w') as csv_file:
        csv_write = csv.writer(csv_file, dialect='excel')
        csv_write.writerows(HEADER)
        csv_write.writerows(data)

def plot_multifig(data,NO_SENSORS,dataSelection):
    """ Plots 3-Axis accelerometer data on seperate graphs per sensor each in a seperate figure. The next figure will appear once the first figure is closed.
        Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,X2,Y2,Z2.....XN,YN,ZN] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*3)] should therfore be provided with data(numpy array).
        The dataSeelction parameter should be 0 or 1 and sets the Y axis to either 0-1024 ADC or -3-3 g respectively.
        """
    # Axis options
    yAxisLimits = [[0,1024],[-3,3]]
    
    # Plots a seperate graph for each sensor
    for i in range(0,NO_SENSORS):
        plt.figure(i + 1)
        plt.title('Sensor ' + str(i + 1))
        plt.plot(data[:,(0 + (3 * i))],label='X Axis')
        plt.plot(data[:,(1 + (3 * i))],label='Y Axis')
        plt.plot(data[:,(2 + (3 * i))],label='Z Axis')
        plt.ylim(yAxisLimits[dataSelection][0],yAxisLimits[dataSelection][1])
        plt.xlabel('Sample Index')
        plt.ylabel('Acceleration/g')
        plt.legend()
        plt.show()
    
def plot_singlefig(data,NO_SENSORS,dataSelection):
    """ Plots 3-Axis accelerometer data on seperate graphs per sensor but displays them all in one figure.
        Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,X2,Y2,Z2.....XN,YN,ZN] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*3)] should therfore be provided with data(numpy array).
        The dataSeelction parameter should be 0 or 1 and sets the Y axis to either 0-1024 ADC or -3-3 g respectively.
        """
    
    # Axis options
    yAxisLimits = [[0,1024],[-3,3]]
    
    # Plots graphs for each sensor on 1 figure
    plt.figure(1)
    for i in range(0,NO_SENSORS):
        # The figure is seperated into subplots using the parameter. 231 means 2 rows, 3 columns, subplot 1
        plt.subplot(231 + i)
        plt.title('Sensor ' + str(i + 1))
        plt.plot(data[:,(0 + (3 * i))],label='X Axis')
        plt.plot(data[:,(1 + (3 * i))],label='Y Axis')
        plt.plot(data[:,(2 + (3 * i))],label='Z Axis')
        plt.ylim(yAxisLimits[dataSelection][0],yAxisLimits[dataSelection][1])
        plt.xlabel('Sample Index')
        plt.ylabel('Acceleration/g')
        plt.legend()
    plt.show()

def main():
    
    NO_SAMPLES = 200
    NO_SENSORS = 5

    data_log = []

    port = '/dev/tty.usbserial-DN018OOF'
    connected = '0'
    sample = '1'
    finish = '0'

    while (connected == '0'):
        input('Press a button to attempt connection with Arduino')
        try:
            # Create Serial port object called arduinoSerial with a 5 second timeout
            arduinoSerial = serial.Serial(port,9600, timeout=5)
            print("Connected to Arduino")
            # These commands clear any samples/commands left in the buffers
            arduinoSerial.reset_input_buffer()
            arduinoSerial.reset_output_buffer()
            connected = '1'
        except:
            print("Failed to connect to Arduino")

    print("Initialising...")
    time.sleep(8)   # Required for the XBee's to initialise

    input('Please press a button to begin sampling')
    arduinoSerial.write(b'S')   # Send 'S' to tell the arduino to start taking/sending samples

    # Sampling loop
    while (sample == '1'):
        collect_samples(arduinoSerial,NO_SAMPLES,data_log)
        sample = input('Continue? (1:yes, Other:no)') # User ends/continues sampling loop
        #sample = '0' # Sampling finishes after NO_SAMPLES have been taken

    arduinoSerial.write(b'S') # Send 2nd 'S' to tell the Arduino to stop
    arduinoSerial.close()

    # Create a Numpy array of the collected sample data
    np_data_log = np.array(data_log)
                           
    # This function removes samples so each sensor has the same amount
    np_data_log_eq = equalise_sample_numbers(np_data_log,NO_SENSORS)

    # Sorts the samples into columns by sensor ID [[1X1,1Y1,1Z1,1X2...],[2X1,2Y1,2Z1,2X2...],.....]
    np_data_sorted = sort_samples(np_data_log_eq,NO_SENSORS)

    # Converts the samples to float for conversion
    np_data_ADC = np_data_sorted.astype(np.float16)

    # Converts the samples from ADC to g
    np_data_g = ADC_to_g(np_data_ADC,NO_SENSORS)

    # Different filenames for the csv file
    timestamp = datetime.datetime.utcnow()
    name = 'Sensor1B(X-1,Y-0,Z-0)'

    path = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensorlog.csv'
    pathTime = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor1log-{:%d%b,%H.%M}.csv'.format(timestamp)
    pathName = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'+name+'.csv'

    # Save the given data to Excel CSV
    save_as_csv(pathName,np_data_g,NO_SENSORS)

    # This loop allows the user to look at the data in various formats before exiting the program
    while(finish == '0'):
        
        # Allows the choice between using the data as in ADC or g format
        dataSelection = input('Which data do you want to use:\n0:ADC\n1:g\n')
        if (dataSelection == '0'):
            data = np_data_sorted
        elif(dataSelection == '1'):
            data = np_data_g
        else:
            data = np_data_g
        
        # Allows the choice between different display options
        selection = input('Which option:\n0:Single figure.\n1:Seperate figures.\n2:Finish\n')
        if (selection == '0'):
            plot_singlefig(data,NO_SENSORS,int(dataSelection)) # Plots all sensor graphs in one figure
        elif (selection == '1'):
            plot_multifig(data,NO_SENSORS,int(dataSelection)) # Plots each sensor graph in a seperate figure one after the other
        elif (selection == '2'):
            finish = '1'

main()














