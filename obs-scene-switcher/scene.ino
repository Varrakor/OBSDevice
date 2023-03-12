const int BUTTON1 = 8;
const int BUTTON2 = 7;

const int GREEN = 11;
const int RED = 12;

unsigned long DELAY = 100;

unsigned long lastButton = 0;

void setup() {
  pinMode(BUTTON1, INPUT);
  pinMode(BUTTON2, INPUT);

  pinMode(GREEN, OUTPUT); 
  pinMode(RED, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  int b1 = digitalRead(BUTTON1);
  int b2 = digitalRead(BUTTON2);

  if (millis() - lastButton > DELAY) {
    if (b1) Serial.write(0);
    else if (b2) Serial.write(1);
    lastButton = millis();
  }

  int scene = Serial.read();

  if (scene == 0) {
    digitalWrite(GREEN, HIGH);
    digitalWrite(RED, LOW);
  }

  else if (scene == 1) {
    digitalWrite(RED, HIGH);
    digitalWrite(GREEN, LOW);
  }
}