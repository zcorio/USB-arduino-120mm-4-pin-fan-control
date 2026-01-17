const int FAN_PWM_PIN = 9;

void setup() {
  pinMode(FAN_PWM_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("fan ")) {
      int percent = cmd.substring(4).toInt();
      percent = constrain(percent, 0, 100);

      int pwm = map(percent, 0, 100, 0, 255);
      analogWrite(FAN_PWM_PIN, pwm);

      Serial.println("OK");
    }
  }
}
