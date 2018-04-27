import serial #Import Serial Library
import time
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy import fftpack
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split


def collect_samples(serialPort,NO_SENSORS,NO_SAMPLES,log):
    """ Saves samples collected from 3-Axis Accelerometers. Samples should be recieved in form (ID X Y Z Time /r/n) with a space to seperate the data. Invalid data is rejected and any samples lost this way are recorded and displayed to the user once the function finishes.
        All samples are collected from the port defined by the serialPort(string) parameter and the function will continue until it saves a number of samples defined by the NO_SAMPLES(int) parameter.
        All samples will be appended to the list specified by the log(list) parameter. This should either be an empty list or a list with 6 columns.
    """
    run = '1'
    timeout = '0'
    desynchronised = '0'
    badSamples = 0
    count = 1
    log_temp = []
    temp = [0] * 20
    NO_FIELDS = (NO_SENSORS * 3) + 1
    
    while (run == '1'):
        # If the input buffer is not empty read the data out into rawData using \n as a delimiter.
        if (serialPort.inWaiting()>0):
            rawData = serialPort.readline()
            print(rawData)
            
            # If invalid data is recieved this prevents program crash
            try:
                # Decode the bytes into a string
                data = rawData.decode()
                
                if (count >= (NO_SAMPLES + 1)):
                    endTime_temp = data.split(" ", 2)
                    if (len(endTime_temp) == 2 and '' not in endTime_temp):
                        endTime = int(endTime_temp[0])
                    else:
                        endTime = 783
                        print('Time not recieved. Calculated: ' + str(endTime))
                    print(str(endTime))
                    print('Lost Samples: ' + str(badSamples))
                    run = '0'
            
                else:
                    data_readings = data.split(" ", NO_FIELDS)
                    
                    # A correct sample should contain 16 values and not include null and so this is used
                    # to validate the data and record any samples that are discarded in this way
                    if (len(data_readings) == NO_FIELDS and '' not in data_readings):
                        # Discard newline characters before saving data
                        int_data_readings = list(map(int,data_readings[:(NO_FIELDS - 1)]))
                        log_temp.append(int_data_readings)
                        serialPort.write(b'T')
                        print('Send T')
                        count += 1
                    else:
                        badSamples += 1
                        serialPort.write(b'F')
                        print('Send F')
    
            except Exception as e:
                print(e)

    samplingPeriod = (endTime/NO_SAMPLES)/NO_SENSORS
    timeStamp = 0.0

    for i in range(0,len(log_temp)):
        for j in range(0,NO_SENSORS):
            temp[0+(j*4)] = log_temp[i][0+(j*3)]
            temp[1+(j*4)] = log_temp[i][1+(j*3)]
            temp[2+(j*4)] = log_temp[i][2+(j*3)]
            temp[3+(j*4)] = timeStamp
            timeStamp += samplingPeriod
        log.append(temp.copy())

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
    
    # Number of samples must match the Arduino
    NO_SAMPLES = 220
    NO_SENSORS = 5
    # At 250 1 cycle is around 0.78ms
    SAMPLING_CYCLES = 25
    
    # 1 Runs a calibration for a stationary vehicle
    CALIBRATE = 0
    
    NO_INSTANCE_TYPES = 3
    

    data_log = []
    saved_data = []
    training_log = []
    path_names = []
    calibration_array = []
    
    port = '/dev/tty.usbserial-DN018OOF'
    connected = '0'
    sample = '1'
    finish = '0'
    modeSelect = '0'
    
    # Different filenames for the csv file
    timestamp = datetime.datetime.utcnow()
    name = 'NormalOperation-TrainingData'
    
    path = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'
    pathTime = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/Sensor1log-{:%d%b,%H.%M}'.format(timestamp)
    pathName = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'+name
    
    trainingRoot = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Results/'
    training_names = ['Normal-TrainingData.csv','Fault1-TrainingData.csv','Fault2-TrainingData.csv']
    trainingPath = [trainingRoot + training_names[0],trainingRoot + training_names[1],trainingRoot + training_names[2]]
    
    savePath = pathName
    samplePath = trainingPath[0]
    

    modeSelect = input('Please select the mode:\n0:Collect Samples\n1:Manipulate Data\n2:Create Training Data\n3:NN\n')

    # ****************************************************** Collect Samples
    if (modeSelect == '0'):
        while (connected == '0'):
            input('Press a button to attempt connection with Arduino')
            try:
                # Create Serial port object called arduinoSerial with a 5 second timeout
                arduinoSerial = serial.Serial(port,baudrate=115200,timeout=5.0)
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

        # Sampling loop
        count = 1
        while (sample == '1'):
            arduinoSerial.write(b'S')   # Send 'S' to tell the arduino to start taking/sending samples
            collect_samples(arduinoSerial,NO_SENSORS,NO_SAMPLES,data_log)
            if (count >= SAMPLING_CYCLES):
                sample = '0' # Sampling finishes after NO_SAMPLES have been taken
            count += 1

        arduinoSerial.close()

        # Converts the samples to float for conversion
        np_data_ADC = np.array(data_log).astype(np.float64)
        
        # Converts the samples from ADC to g
        np_data_g = ADC_to_g(np_data_ADC,NO_SENSORS)
        
        # Find calibration array
        cal_path = '/Users/Angelo555uk/Desktop/University/Year_4/Project/Project/Calibration/CalArray.csv'
        if (CALIBRATE==1):
            for i in range(0,NO_SENSORS):
                for j in range(0,3):
                    calibration_array.append(np.mean(np_data_g[:,j+(4*i)]))
            with open(cal_path, 'w') as csv_file:
                csv_write = csv.writer(csv_file, dialect='excel')
                csv_write.writerow(calibration_array)
        
        # Re-Zero axes
        calibration_array = read_csv(cal_path)
        np_calibration_array = np.array(calibration_array).astype(np.float64).flatten()
        
        for i in range(0,NO_SENSORS):
            for j in range(0,3):
                np_data_g[:,j+(4*i)] -= np_calibration_array[j+(3*i)]
        
        # Convert the ms to s before saving to the csv
        np_data_g[:,[3,7,11,15,19]] = np_data_g[:,[3,7,11,15,19]]/1000
        np_data_ADC[:,[3,7,11,15,19]] = np_data_ADC[:,[3,7,11,15,19]]/1000

        # Save the given data to Excel CSV
        save_as_csv(samplePath,np_data_g,NO_SENSORS)

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
            selection = input('Which option:\n0:Single figure.\n1:Seperate figures.\n2:Manipulate Data\n3:Create Training Data\n4:NN\n5:Finish\n')
            if (selection == '0'):
                plot_singlefig(data,NO_SENSORS,int(dataSelection)) # Plots all sensor graphs in one figure
            elif (selection == '1'):
                plot_multifig(data,NO_SENSORS,int(dataSelection)) # Plots each sensor graph in a seperate figure one after the other
            elif (selection == '2'):
                modeSelect = '1'
                finish = '1'
            elif (selection == '3'):
                modeSelect = '2'
                finish = '1'
            elif (selection == '4'):
                modeSelect = '3'
                finish = '1'
            elif (selection == '5'):
                finish = '1'

    # **************************************************** Data Manipulation
    if (modeSelect == '1'):
                        
        # Read out the data from scecified file
        saved_data = read_csv(path_names[0])
        
        # Remove the header and cast as numpy float array
        np_saved_data = np.array(saved_data[2:]).astype(np.float64)
        
        # Find the start and end index for each instance and the number fo total instances in the file
        np_instance_start = np.asarray(np.nonzero(np_saved_data[:,3] == 0))
        np_instance_start = np.append(np_instance_start,np_saved_data.shape[0])
        numberInstances = np_instance_start.shape[0]
        
        # Create a copy of the data for FFT
        np_fft_data = np_saved_data.copy()

        # Perform an FFT on the X,Y and Z values for each sensor and save the magnitude
        for i in range(0,NO_SENSORS):
            for j in range(0,3):
                np_fft_data[:,j+(4*i)] = abs(fftpack.fft(np_fft_data[:,j+(4*i)]))
                    
        # Get number of samples
        N = np_fft_data.shape[0]
        # Get the time interval for each sensor
        dt = np_fft_data[[1],[3,7,11,15,19]] - np_fft_data[[0],[3,7,11,15,19]]
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

                    
        # This loop allows the user to look at the data in various formats before exiting the program
        finish = '0'
        while(finish == '0'):
            
            # Allows the choice between different display options
            selection = input('Which option:\n0:Single figure.\n1:Seperate figures.\n2:Create Training Data\n3:NN\n4:Finish\n')
            if (selection == '0'):
                plot_singlefig(np_saved_data,NO_SENSORS,1) # Plots all sensor graphs in one figure
            elif (selection == '1'):
                plot_multifig(np_saved_data,NO_SENSORS,1) # Plots each sensor graph in a seperate figure one after the other
            elif (selection == '2'):
                modeSelect = '2'
                finish = '1'
            elif (selection == '3'):
                modeSelect = '3'
                finish = '1'
            elif (selection == '4'):
                finish = '1'

    # ********************************************* Create Training Data
    if (modeSelect == '2'):
        
        targets = [1,0,0]
        training_header = []
        
        for i in range(0,NO_INSTANCE_TYPES):
            # Read out the data from scecified file
            saved_data = read_csv(trainingPath[i])
            
            # Remove the header and convert the data to a float32 numpy array for manipulation
            np_saved_data = np.array(saved_data[2:]).astype(np.float64)

            # Find start and end index of instances and total number of instances
            np_instance_start = np.asarray(np.nonzero(np_saved_data[:,3] == 0))
            np_instance_start = np.append(np_instance_start,np_saved_data.shape[0])
            numberInstances = np_instance_start.shape[0] - 1
            
            print (np_instance_start)
            print (numberInstances)

            # Perform FFT on each instance and save to one log
            for j in range(0,numberInstances):
                
                # Create a copy of the data for FFT
                np_fft_data = np_saved_data[np_instance_start[j]:np_instance_start[j+1]]

                # Perform an FFT on the X,Y and Z values for each sensor and save the magnitude
                for x in range(0,NO_SENSORS):
                    for y in range(0,3):
                        np_fft_data[:,y+(4*x)] = abs(fftpack.fft(np_fft_data[:,y+(4*x)]))
                
                # Get number of samples
                N = np_fft_data.shape[0]

                # Remove values above the Nyquist Frequency N/2
                np_ffthalf_data = np_fft_data[:int(N/2)]
                
                # Remove time rows
                np.delete(np_ffthalf_data, [3,7,11,15,19], axis=1)

                # Flatten the data into a single row
                np_temp_row = np_ffthalf_data.flatten('F')
                np_temp_row = np.append(np_temp_row,targets[i])
                temp_row = np_temp_row.tolist()

                training_log.append(temp_row)

        # Create header for training data
        for i in range (0,(len(training_log[0]) - 1)):
            training_header.append("x" + str(i))
        training_header.append("y")

        # Save the FFT Instanced values to CSV
        with open(path+'TrainingData.csv', 'w') as csv_file:
            csv_write = csv.writer(csv_file, dialect='excel')
            csv_write.writerow(training_header)
            csv_write.writerows(training_log)
        
        # This loop allows the user to select options
        finish = '0'
        while(finish == '0'):
            # Allows the choice between different display options
            selection = input('Which option:\n0:Neural Net.\n1:Finish\n')
            if (selection == '0'):
                modeSelect = '3'
                finish = '1'
            elif (selection == '1'):
                finish = '1'

    # ******************************************* Neural Net
    if (modeSelect == '3'):

        # Data Processing
        saved_data = read_csv(path+'TrainingData.csv')
        np_saved_data = np.array(saved_data[1:]).astype(np.float64)
        X = np_saved_data[:,0:-1]
        print (X)
        y = np.ravel(np_saved_data[:,[-1]])
        print (y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
        
        # Neural Network Definition
        model = Sequential()

        # Add an input layer
        model.add(Dense(135, activation='relu', input_shape=(X.shape[1],)))

        # Add one hidden layer
        model.add(Dense(27, activation='relu'))

        # Add an output layer
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        model.fit(X_train, y_train,epochs=20, batch_size=1, verbose=1)

        score = model.evaluate(X_test, y_test,verbose=1)

        print(score)
        print(model.get_weights())



main()












