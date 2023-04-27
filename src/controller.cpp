#include <Keypad.h>

#define ROWS 4
#define COLS 4

#define LEDS 8

char keys[ROWS][COLS] = {
  { 'a', 'b', 'c', 'd' }, 
  { 'e', 'f', 'g', 'h' }, 
  { 'i', 'j', 'k', 'l' },
  { 'm', 'n', 'o', 'p' } 
};

byte rowPin[COLS] = { 9, 8, 7, 6 };  // connect to L1-L4
byte colPin[ROWS] = { 5, 4, 3, 2 };  // connect to R1-R4

byte ledPin[LEDS] = { 15, 16, 17, 18, 19, 12, 11, 10 };  // connect to D1-D8

Keypad keypad = Keypad(makeKeymap(keys), rowPin, colPin, ROWS, COLS);

void leds_off() {
  for (int i = 0; i < LEDS; ++i) digitalWrite(ledPin[i], HIGH);
}

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < LEDS; ++i) pinMode(ledPin[i], OUTPUT);
  leds_off();
}

int getKey() {
  return (int) keypad.getKey() - 'a'; // 0-15
}

void loop(){
  int key = getKey();
  if (key >= 0) Serial.write(key);

  if (Serial.available() > 0) {
    int led = Serial.read(); // 0-7
    
    if (led >= 0 && led < LEDS) {
      leds_off();
      digitalWrite(ledPin[led], LOW);
    }
  }
}

