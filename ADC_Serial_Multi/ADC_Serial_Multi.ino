
const int groundpin1 = 2;
const int powerpin1 = 3;
const int groundpin2 = 4;
const int powerpin2 = 5;
const int groundpin3 = 6;
const int powerpin3 = 7;

const int sensor1x = A0;
const int sensor1y = A1;
const int sensor1z = A2;
const int sensor2x = A3;
const int sensor2y = A4;
const int sensor2z = A5;
const int sensor3x = A7;
const int sensor3y = A8;
const int sensor3z = A9;

// Variables
const int NO_OF_SENSORS = 3;
const int sensorInfo[NO_OF_SENSORS][3] = { {sensor1x,sensor1y,sensor1z},
                                           {sensor2x,sensor2y,sensor2z},
                                           {sensor3x,sensor3y,sensor3z} };

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
}

void loop() {

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
   } 
}
