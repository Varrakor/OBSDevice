const int BUTTON1 = 8;
const int BUTTON2 = 7;

const int GREEN = 11;
const int RED = 12;

void setup() {
  pinMode(BUTTON1, INPUT);
  pinMode(BUTTON2, INPUT);

  pinMode(GREEN, OUTPUT); 
  pinMode(RED, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  if (digitalRead(BUTTON2)) {
    digitalWrite(RED, HIGH);
    digitalWrite(GREEN, LOW);
    Serial.write(1);
  }

  else if (digitalRead(BUTTON1)) {
    digitalWrite(GREEN, HIGH);
    digitalWrite(RED, LOW);
    Serial.write(0);
  }
}