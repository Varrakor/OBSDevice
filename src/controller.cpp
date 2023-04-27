#include <Keypad.h>

#define ROWS 4
#define COLS 4

#define LEDS 10

char keys[ROWS][COLS] = {
  { 'a', 'b', 'c', 'd' }, 
  { 'e', 'f', 'g', 'h' }, 
  { 'i', 'j', 'k', 'l' },
  { 'm', 'n', 'o', 'p' } 
};

byte rowPin[COLS] = { 9, 8, 7, 6 };  // connect to L1-L4
byte colPin[ROWS] = { 5, 4, 3, 2 };  // connect to R1-R4

byte ledPin[LEDS] = { 15, 16, 17, 18, 19, 12, 11, 10, 14, 13 };  // connect to D1-D8, and two more leds

Keypad keypad = Keypad(makeKeymap(keys), rowPin, colPin, ROWS, COLS);

void scene_leds_off() {
  for (int i = 0; i <= 7; ++i) digitalWrite(ledPin[i], HIGH);
}

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < LEDS; ++i) {
    pinMode(ledPin[i], OUTPUT);
    digitalWrite(ledPin[i], HIGH);
  }
}

int getKey() {
  return (int) keypad.getKey() - 'a'; // 0-15
}

void loop(){
  int key = getKey();
  if (key >= 0) Serial.write(key);

  if (Serial.available() > 0) {
    int led = Serial.read(); // 0-7
    
    if (led >= 0 && led <= 7) {
      scene_leds_off();
      digitalWrite(ledPin[led], LOW);
    }

    else if (led == 8) digitalWrite(ledPin[8], LOW); // 8 is output_state off
    
    else if (led == 9) digitalWrite(ledPin[8], HIGH); // 9 is output_state on
  }
}

