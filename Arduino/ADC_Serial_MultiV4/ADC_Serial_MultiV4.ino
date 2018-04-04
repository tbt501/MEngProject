

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
const int sensorInfo[5][3] = { {sensor1x,sensor1y,sensor1z},
                               {sensor2x,sensor2y,sensor2z},
                               {sensor3x,sensor3y,sensor3z},
                               {sensor4x,sensor4y,sensor4z},
                               {sensor5x,sensor5y,sensor5z}};

bool start = false;
int serialRX;
unsigned long timeStart,timeSample;

void setup() {
  
  Serial.begin(9600);
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
  
  timeStart = millis();
  while(start){
    for(int i=0; i<NO_OF_SENSORS; i++){
      timeSample = millis()-timeStart;
      delay(1);
      Serial.print(i+1);
      delay(1);
      Serial.print(" ");
      delay(1);
      Serial.print(analogRead(sensorInfo[i][0]));
      delay(1);
      Serial.print(" ");
      delay(1);
      Serial.print(analogRead(sensorInfo[i][1]));
      delay(1);
      Serial.print(" ");
      delay(1);
      Serial.print(analogRead(sensorInfo[i][2]));
      delay(1);
      Serial.print(" ");
      delay(1);
      Serial.print(timeSample);
      delay(20);
      Serial.print(" ");
      delay(1);
      Serial.println();
           
      if (Serial.available() > 0){
          serialRX = Serial.read();
          if (serialRX == 'S'){
            start = false;
          }
      }
    }
  } 
}
