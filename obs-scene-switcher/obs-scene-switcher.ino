#define NUM_BUTTONS 4
#define DELAY 100 // milliseconds

int buttons[] = {2, 3, 4, 5}; // pin numbers
int leds[] = {9, 10, 11, 12};

int reads[NUM_BUTTONS];

unsigned long lastButton = 0;

void setup() {
  DDRD = 0x00; // port D input
  DDRB = 0xFF; // port B output
  Serial.begin(9600);
}

void loop() {
  // read button inputs
  for(int i = 0; i < NUM_BUTTONS; ++i) reads[i] = digitalRead(buttons[i]);

  // if a button is pressed, send data to host
  if (millis() - lastButton > DELAY) {
    for(int i = 0; i < NUM_BUTTONS; ++i) {
      if(reads[i]) {
        Serial.write(i);
        break;
      }
    }
    lastButton = millis(); // debounce button
  }

  // receive scene number from host and light up that LED 
  int scene = Serial.read();
  for(int i = 0; i < NUM_BUTTONS; ++i) {
    if (scene == i) {
      digitalWrite(leds[i], HIGH);
      for(int j = 0; j < NUM_BUTTONS; ++j) {
        if(j != i) digitalWrite(leds[j], LOW);
      }
      break;
    }
  }
}