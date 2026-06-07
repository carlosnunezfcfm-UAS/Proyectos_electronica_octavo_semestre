void setup() {
  Serial.begin(250000);
}

void loop() {
  byte ch1 = analogRead(A0) >> 2; // 0-255
  byte ch2 = analogRead(A1) >> 2; // 0-255

  Serial.write(ch1);
  Serial.write(ch2);  
}
