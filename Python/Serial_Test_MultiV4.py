import serial #Import Serial Library
import time
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack


def collect_samples(serialPort,NO_SAMPLES,log):
    """ Saves samples collected from 3-Axis Accelerometers. Samples should be recieved in form (ID X Y Z Time /r/n) with a space to seperate the data. Invalid data is rejected and any samples lost this way are recorded and displayed to the user once the function finishes.
        All samples are collected from the port defined by the serialPort(string) parameter and the function will continue until it saves a number of samples defined by the NO_SAMPLES(int) parameter.
        All samples will be appended to the list specified by the log(list) parameter. This should either be an empty list or a list with 6 columns.
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
                
                # Split the ID, x, y, z, time and newline values into a list
                data_readings = data.split(" ", 6)
                print(data_readings)
                
                # A correct sample should contain 6 values and not include null and so this is used
                # to validate the data and record any samples that are discarded in this way
                if (len(data_readings) == 6 and '' not in data_readings):
                    # Discard newline characters before saving data
                    int_data_readings = list(map(int,data_readings[:5]))
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
    """ A function that takes a numpy array, given by the np_samples(numpy aray) parameter, of samples collected from 3-Axis Accelerometers in the form [ID,X,Y,Z,Time] and returns a numpy area of samples where each ID value has the same amount of samples. Each unique ID relates to an associated sensor and the total number of sensors should be given with the parameter NO_SENSORS(int).
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
    """ Sorts a numpy array of 3-Axis Accelerometer data in the form [ID,X,Y,Z,Time] into an array of the following form:
        
                Sensor 1      |Sensor 2      |.............|Sensor N
                X | Y| Z| Time| X| Y| Z| Time|.............|X |Y | Z| Time
    Sample 1      |  |  |     |  |  |  |     |.............|  |  |  |
    Sample 2      |  |  |     |  |  |  |     |.............|  |  |  |
       .                        .
       .                        .
       .                        .
       .                        .
    Sample N      |  |  |     |  |  |  |     |.............|  |  |  |
    
    A numpy array should be provided to the parameter np_data(numpy array) in the specified form where each ID appears the same number of times. The equalise_sample_numbers can be used to ensure this.
    The number of sensor ID's should also be provided as an int using the NO_SENSORS(int) parameter.
    """

    # Sorts the data into columns as follows X1,Y1,Z1,Time,X2,Y2,Z2,Time etc.... Each row is then a sample.
    # Sensor 1's samples are added to np_data_sorted first. The for loop then works through
    # each sensor and appends its X,Y,Z,Time values in the next 4 columns of np_data_sorted.
    np_data_sorted = np_data[:,[1,2,3,4]][np_data[:,0] == 1 ]
    for i in range(2,NO_SENSORS+1):
        np_temp = np_data[:,[1,2,3,4]][np_data[:,0] == i ]
        np_data_sorted = np.concatenate((np_data_sorted,np_temp), axis=1)
    
    return (np_data_sorted)

def ADC_to_g(np_data,NO_SENSORS):
    """ A function that takes a numpy array of ADC values that relate to N 3-Axis Accelerometers in the form [X1,Y1,Z1,Time,X2,Y2,Z2,Time.....XN,YN,ZN,Time] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter. The ADC values are then converted into g values using predefined constants m and b calculated during calibration. The following conversion formula is used:
            g= ADC/m + b
        A numpy array of dimension [n][(N*4)] should therfore be provided with np_data(numpy array) and a numpy array of the same dimensions is returned.
    """

    # CONVERSION holds the m and b values calculated during calibration for the X,Y and Z axes of each Sensor.
    CONVERSION = [ [102.006,101.074,103.061,-4.990,-5.025,-5.171],    # [ [mX1B,mY1B,mZ1B,bX1B,bY1B,bZ1B],
                   [99.936,101.946,102.793,-5.084,-4.993,-5.001],     #   [mX2,mY2,mZ2,bX2,bY2,bZ2],
                   [97.758,104.368,103.537,-5.211,-4.788,-5.229],    #   [mX3B,mY3B,mZ3B,bX3B,bY3B,bZ3B],
                   [99.842,101.169,100.999,-5.062,-5.020,-5.124],     #   [mX4,mY4,mZ4,bX4,bY4,bZ4],
                   [100.052,102.312,101.709,-5.087,-4.894,-5.126] ]   #   [mX5,mY5,mZ5,bX5,bY5,bZ5] ]
                   
    data = np_data.copy()

    # The conversion array is used to transform the samples from ADC to g
    for i in range(0,NO_SENSORS):
        for j in range(0,3):
            data[:,j+(4*i)] = ((data[:,j+(4*i)]/CONVERSION[i][j]) + CONVERSION[i][j+3])
    
    return(data)

def read_csv(path):
    """ Reads the csv file from the given path(string) and returns it as a list
    """
    csv_data =[]
    
    with open(path, 'r') as csv_file:
        csv_read = csv.reader(csv_file, dialect='excel')
        for row in csv_read:
            csv_data.append(row)

    return(csv_data)

def save_as_csv(path,data,NO_SENSORS):
    """ Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,Time,X2,Y2,Z2,Time.....XN,YN,ZN,Time] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*4)] should therfore be provided with np_data(numpy array).
        The array is saved to a CSV file of path defined by the path(string) parameter and given a header as below. The NO_SENSORS should not exceed 5 due to the addition of the header.
    """

    HEADER1 = [ ['Sensor 1'],
                ['X','Y','Z','Time/ms'] ]
    HEADER2 = [ ['Sensor 1',' ',' ',' ','Sensor 2'],
                ['X','Y','Z','Time/ms','X','Y','Z','Time/ms'] ]
    HEADER3 = [ ['Sensor 1',' ',' ',' ','Sensor 2',' ',' ',' ','Sensor 3'],
                ['X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms'] ]
    HEADER4 = [ ['Sensor 1',' ',' ',' ','Sensor 2',' ',' ',' ','Sensor 3',' ',' ',' ','Sensor 4'],
                ['X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms'] ]
    HEADER5 = [ ['Sensor 1',' ',' ',' ','Sensor 2',' ',' ',' ','Sensor 3',' ',' ',' ','Sensor 4',' ',' ',' ','Sensor 5'],
                ['X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms','X','Y','Z','Time/ms'] ]

    HEADERS = [HEADER1,HEADER2,HEADER3,HEADER4,HEADER5]

    HEADER = HEADERS[NO_SENSORS - 1]

    # The  data is saved as a CSV file using the given path
    with open(path, 'w') as csv_file:
        csv_write = csv.writer(csv_file, dialect='excel')
        csv_write.writerows(HEADER)
        csv_write.writerows(data)

def plot_multifig(data,NO_SENSORS,dataSelection):
    """ Plots 3-Axis accelerometer data on seperate graphs per sensor each in a seperate figure. The next figure will appear once the first figure is closed.
        Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,Time,X2,Y2,Z2,Time.....XN,YN,ZN,Time] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*4)] should therfore be provided with data(numpy array).
        The dataSeelction parameter should be 0 or 1 and sets the Y axis to either 0-1024 ADC or -3-3 g respectively.
        """
        
    # Axis options
    yAxisLimits = [[0,1024],[-3,3]]
    
    # Plots a seperate graph for each sensor
    for i in range(0,NO_SENSORS):
        plt.figure(i + 1)
        plt.title('Sensor ' + str(i + 1))
        plt.plot(data[:,(3 + (4 * i))],data[:,(0 + (4 * i))],label='X Axis')
        plt.plot(data[:,(3 + (4 * i))],data[:,(1 + (4 * i))],label='Y Axis')
        plt.plot(data[:,(3 + (4 * i))],data[:,(2 + (4 * i))],label='Z Axis')
        plt.ylim(yAxisLimits[dataSelection][0],yAxisLimits[dataSelection][1])
        plt.xlabel('Time/s')
        plt.ylabel('Acceleration/g')
        plt.legend()
        plt.show()
    
def plot_singlefig(data,NO_SENSORS,dataSelection):
    """ Plots 3-Axis accelerometer data on seperate graphs per sensor but displays them all in one figure.
        Takes a numpy array of 3-Axis Accelerometer data of the form [X1,Y1,Z1,Time,X2,Y2,Z2,Time.....XN,YN,ZN,Time] with any number of rows that relate to the number of samples for each sensor and N defined by the NO_SENSORS(int) parameter.
        A numpy array of dimension [n][(N*4)] should therfore be provided with data(numpy array).
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
        plt.plot(data[:,(3 + (4 * i))],data[:,(0 + (4 * i))],label='X Axis')
        plt.plot(data[:,(3 + (4 * i))],data[:,(1 + (4 * i))],label='Y Axis')
        plt.plot(data[:,(3 + (4 * i))],data[:,(2 + (4 * i))],label='Z Axis')
        plt.ylim(yAxisLimits[dataSelection][0],yAxisLimits[dataSelection][1])
        plt.xlabel('Time/s')
        plt.ylabel('Acceleration/g')
        plt.legend()
    plt.show()

def main():
    
    # Each sample takes around 30ms. So 2000 is 1 minute.
    NO_SAMPLES = 20000
    NO_SENSORS = 5

    data_log = []
    saved_data = []

    port = '/dev/tty.usbserial-DN018OOF'
    connected = '0'
    sample = '1'
    finish = '0'
    modeSelect = '0'
    
    # Different filenames for the csv file
    timestamp = datetime.datetime.utcnow()
    name = 'NormalOperation-10min'
    
    path = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensorlog'
    pathTime = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor1log-{:%d%b,%H.%M}'.format(timestamp)
    pathName = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'+name
    
    
    currentPath = pathName+'.csv'

    modeSelect = input('Please select the mode:\n0:Collect Samples\n1:Manipulate Data\n')
    if (modeSelect == '0'):
        while (connected == '0'):
            input('Press a button to attempt connection with Arduino')
            try:
                # Create Serial port object called arduinoSerial with a 5 second timeout
                arduinoSerial = serial.Serial(port,9600, timeout=5)
                print("Connected to Arduino")
                connected = '1'
            except:
                print("Failed to connect to Arduino")

        print("Initialising...")
        # These commands clear any samples/commands left in the buffers
        time.sleep(2)
        arduinoSerial.reset_input_buffer()
        arduinoSerial.reset_output_buffer()
        time.sleep(6)   # Required for the XBee's to initialise
        
        input('Please press a button to begin sampling')
        arduinoSerial.write(b'S')   # Send 'S' to tell the arduino to start taking/sending samples

        # Sampling loop
        while (sample == '1'):
            collect_samples(arduinoSerial,NO_SAMPLES,data_log)
            sample = input('Continue? (1:yes, Other:no)\n') # User ends/continues sampling loop
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
        np_data_ADC = np_data_sorted.astype(np.float32)

        # Converts the samples from ADC to g
        np_data_g = ADC_to_g(np_data_ADC,NO_SENSORS)
        
        # Convert the ms to s before saving to the csv
        np_data_g[:,[3,7,11,15,19]] = np_data_g[:,[3,7,11,15,19]]/1000
        np_data_ADC[:,[3,7,11,15,19]] = np_data_ADC[:,[3,7,11,15,19]]/1000

        # Save the given data to Excel CSV
        save_as_csv(currentPath,np_data_g,NO_SENSORS)

        # This loop allows the user to look at the data in various formats before exiting the program
        while(finish == '0'):
            
            # Allows the choice between using the data as in ADC or g format
            dataSelection = input('Which data do you want to use:\n0:ADC\n1:g\n')
            if (dataSelection == '0'):
                data = np_data_ADC
            elif(dataSelection == '1'):
                data = np_data_g
            else:
                data = np_data_g

            # Allows the choice between different display options
            selection = input('Which option:\n0:Single figure.\n1:Seperate figures.\n2:Manipulate Data\n3:Finish\n')
            if (selection == '0'):
                plot_singlefig(data,NO_SENSORS,int(dataSelection)) # Plots all sensor graphs in one figure
            elif (selection == '1'):
                plot_multifig(data,NO_SENSORS,int(dataSelection)) # Plots each sensor graph in a seperate figure one after the other
            elif (selection == '2'):
                modeSelect = '1'
                finish = '1'
            elif (selection == '3'):
                finish = '1'


    if (modeSelect == '1'):
        
        # Read out the data from scecified file
        saved_data = read_csv(currentPath)
        
        # Remove the header, select a portion of data and convert the data to a float32 numpy array for manipulation
        np_saved_data = np.array(saved_data[2:1802]).astype(np.float32)
        
        # Create a copy of the data for interpolation
        np_interpol_data = np_saved_data.copy()
        
        # Interpolate the data
        for i in range(0,NO_SENSORS):
            # Create a time array fopr each sensor that has the same start and end time as the data but with a constant interval
            np_temp = np.linspace(0,np_interpol_data[-1][3+(i*4)],np_interpol_data.shape[0])
            for j in range(0,3):
                # Use the constant interval time data to interpolate the corresponding x,y and z values from the original data
                np_interpol_data[:,j+(4*i)] = np.interp(np_temp,np_interpol_data[:,3+(i*4)],np_interpol_data[:,j+(i*4)])
            # Replace the original sample times with the constant interval sample times for each sensor
            np_interpol_data[:,3+(i*4)] = np_temp
        
        # Save the interpolated data to CSV
        save_as_csv(pathName+'(Interpolated).csv',np_interpol_data,NO_SENSORS)
        
        # Create a copy of the interpolated data for FFT
        np_fft_data = np_interpol_data.copy()
        
        # Perform an FFT on the X,Y and Z values for each sensor and save the magnitude
        for i in range(0,NO_SENSORS):
            for j in range(0,3):
                np_fft_data[:,j+(4*i)] = abs(fftpack.fft(np_fft_data[:,j+(4*i)]))
        
        # Get number of samples
        N = np_fft_data.shape[0]
        # Get the time interval for each sensor
        dt = np_fft_data[[1],[3,7,11,15,19]] - np_fft_data[[0],[3,7,11,15,19]]
        print(dt)
        # Find the smapling frequency for each sensor
        fs = 1/dt

        # Produce the frequency data corresponding to the FFT
        for i in range(0,NO_SENSORS):
            np_fft_data[:,3+(i*4)] = fftpack.fftfreq(N) * fs[i]

        # Remove values above the Nyquist Frequency N/2
        np_ffthalf_data = np_fft_data[:int(N/2)]

        # Plot the FFT values
        plt.figure(1)
        for i in range(0,NO_SENSORS):
            # The figure is seperated into subplots using the parameter. 231 means 2 rows, 3 columns, subplot 1
            plt.subplot(231 + i)
            plt.title('Sensor ' + str(i + 1))
            plt.plot(np_ffthalf_data[:,(3 + (4 * i))],np_ffthalf_data[:,(0 + (4 * i))],label='X Axis')
            plt.plot(np_ffthalf_data[:,(3 + (4 * i))],np_ffthalf_data[:,(1 + (4 * i))],label='Y Axis')
            plt.plot(np_ffthalf_data[:,(3 + (4 * i))],np_ffthalf_data[:,(2 + (4 * i))],label='Z Axis')
            plt.xlabel('Freq/Hz')
            plt.ylabel('Magnitude')
            plt.legend()
        plt.show()

        # Save the FFT values to CSV
        save_as_csv(pathName+'(FFT).csv',np_ffthalf_data,NO_SENSORS)
        
        # This loop allows the user to look at the data in various formats before exiting the program
        finish = '0'
        while(finish == '0'):
            
            # Allows the choice between different display options
            selection = input('Which option:\n0:Single figure.\n1:Seperate figures.\n2:Finish\n')
            if (selection == '0'):
                plot_singlefig(np_saved_data,NO_SENSORS,1) # Plots all sensor graphs in one figure
            elif (selection == '1'):
                plot_multifig(np_saved_data,NO_SENSORS,1) # Plots each sensor graph in a seperate figure one after the other
            elif (selection == '2'):
                finish = '1'

main()

if(0):
    # Number of samplepoints
    N = 600
    # sample spacing
    T = 1.0 / 800.0
    x = np.linspace(0.0, N*T, N) # Create an array from 0 - N*T with N points between
    print (x)
    y = np.sin(50*2.0*np.pi*x)
    print (y)
    yf = scipy.fftpack.fft(y)
    print (yf)
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    print (xf)
    # The figure is seperated into subplots using the parameter. 231 means 2 rows, 3 columns, subplot 1
    plt.subplot(211)
    plt.plot(x,y)
    plt.subplot(212)
    plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))

    plt.show()












