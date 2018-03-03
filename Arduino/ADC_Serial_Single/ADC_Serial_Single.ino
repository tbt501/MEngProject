
const int groundpin1 = 2;
const int powerpin1 = 3;

const int sensor1x = A0;
const int sensor1y = A1;
const int sensor1z = A2;

void setup() {
Serial.begin(9600);

pinMode(groundpin1, OUTPUT);
pinMode(powerpin1, OUTPUT);
digitalWrite(groundpin1, LOW);
digitalWrite(powerpin1, HIGH);
}

void loop() {

  Serial.print("1");
  Serial.print(" ");
  Serial.print(analogRead(sensor1x));
  Serial.print(" ");
  Serial.print(analogRead(sensor1y));
  Serial.print(" ");
  Serial.print(analogRead(sensor1z));
  Serial.print(" ");
  Serial.println();
  delay(100);

}
