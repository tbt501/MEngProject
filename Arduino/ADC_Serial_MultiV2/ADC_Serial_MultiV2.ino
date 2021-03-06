
const int groundpin1 = 2;
const int powerpin1 = 3;
const int groundpin2 = 4;
const int powerpin2 = 5;
const int groundpin3 = 6;
const int powerpin3 = 7;
const int groundpin4 = 8;
const int powerpin4 = 9;
const int groundpin5 = 10;
const int powerpin5 = 11;

const int sensor1x = A0;
const int sensor1y = A1;
const int sensor1z = A2;
const int sensor2x = A3;
const int sensor2y = A4;
const int sensor2z = A5;
const int sensor3x = A7;
const int sensor3y = A8;
const int sensor3z = A9;
const int sensor4x = A10;
const int sensor4y = A11;
const int sensor4z = A12;
const int sensor5x = A13;
const int sensor5y = A14;
const int sensor5z = A15;

// Variables
const int NO_OF_SENSORS = 5;
const int sensorInfo[NO_OF_SENSORS][3] = { {sensor1x,sensor1y,sensor1z},
                                           {sensor2x,sensor2y,sensor2z},
                                           {sensor3x,sensor3y,sensor3z},
                                           {sensor4x,sensor4y,sensor4z},
                                           {sensor5x,sensor5y,sensor5z}};

bool start = false;
int serialRX;

void setup() {
  Serial.begin(9600);

  pinMode(groundpin1, OUTPUT);
  pinMode(powerpin1, OUTPUT);
  digitalWrite(groundpin1, LOW);
  digitalWrite(powerpin1, HIGH);
  pinMode(groundpin2, OUTPUT);
  pinMode(powerpin2, OUTPUT);
  digitalWrite(groundpin2, LOW);
  digitalWrite(powerpin2, HIGH);
  pinMode(groundpin3, OUTPUT);
  pinMode(powerpin3, OUTPUT);
  digitalWrite(groundpin3, LOW);
  digitalWrite(powerpin3, HIGH);
  pinMode(groundpin4, OUTPUT);
  pinMode(powerpin4, OUTPUT);
  digitalWrite(groundpin4, LOW);
  digitalWrite(powerpin4, HIGH);
  pinMode(groundpin5, OUTPUT);
  pinMode(powerpin5, OUTPUT);
  digitalWrite(groundpin5, LOW);
  digitalWrite(powerpin5, HIGH);
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
    for(int i=0; i<NO_OF_SENSORS; i++){
      Serial.print(i+1);
      Serial.print(" ");
      Serial.print(analogRead(sensorInfo[i][0]));
      Serial.print(" ");
      Serial.print(analogRead(sensorInfo[i][1]));
      Serial.print(" ");
      Serial.print(analogRead(sensorInfo[i][2]));
      Serial.print(" ");
      Serial.println();
      delay(20);
      if (Serial.available() > 0){
          serialRX = Serial.read();
          if (serialRX == 'S'){
            start = false;
          }
      }
    }
  } 
}
