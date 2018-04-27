

const int sensor4x = A0;
const int sensor4y = A1;
const int sensor4z = A2;
const int sensor1x = A3;
const int sensor1y = A4;
const int sensor1z = A5;
const int sensor3x = A7;
const int sensor3y = A8;
const int sensor3z = A9;
const int sensor5x = A10;
const int sensor5y = A11;
const int sensor5z = A12;
const int sensor2x = A13;
const int sensor2y = A14;
const int sensor2z = A15;

// Variables
const int NO_OF_SENSORS = 5;
const int NO_OF_SAMPLES = 250;
const int sensorInfo[5][3] = { {sensor1x,sensor1y,sensor1z},
                               {sensor2x,sensor2y,sensor2z},
                               {sensor3x,sensor3y,sensor3z},
                               {sensor4x,sensor4y,sensor4z},
                               {sensor5x,sensor5y,sensor5z} };


bool start = false;
int serialRX;
unsigned long timeStart,timeEnd;
int sensorVals[NO_OF_SAMPLES][15];

void setup() {
  
  Serial.begin(115200);
  analogReference(EXTERNAL);
  
}

void loop() {
  while(!start){
     if (Serial.available() > 0){
        serialRX = Serial.read();
        if (serialRX == 'S'){
          start = true;
        }
     }
  }

  
  while(start){
    
    timeStart = millis();

    for(int i=0; i<NO_OF_SAMPLES; i++){
      for(int j=0; j<NO_OF_SENSORS; j++){
        
        // Takes 100 microseconds per analogue read plus added delay
        sensorVals[i][0+(j*3)] = analogRead(sensorInfo[j][0]);
        delayMicroseconds(100);
        sensorVals[i][1+(j*3)] = analogRead(sensorInfo[j][1]);
        delayMicroseconds(100);
        sensorVals[i][2+(j*3)] = analogRead(sensorInfo[j][2]);
        delayMicroseconds(100);
      }
    }
 
    timeEnd = millis()-timeStart;

    for(int i=0; i<NO_OF_SAMPLES; i++){
      for(int j=0; j<NO_OF_SENSORS; j++){
        Serial.print(sensorVals[i][0+(j*3)]);
        Serial.print(" ");
        Serial.print(sensorVals[i][1+(j*3)]);
        Serial.print(" ");
        Serial.print(sensorVals[i][2+(j*3)]);
        Serial.print(" ");
        delay(10);
      }
      Serial.println();
    }
    Serial.print("T");
    Serial.print(" ");
    Serial.print(timeEnd);
    Serial.print(" ");
    Serial.println();
    delay(5);
    
    start = false;
    
  } 
}
