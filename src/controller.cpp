#include <Arduino.h>
#include <Keypad.h>

// ----- leds -----

#define NUM_SCENES 8

#define OUTPUT_PIN 13
#define MUTE_PIN 14

#define S0 17
#define S1 18
#define S2 19

int binary[NUM_SCENES][3] = { {0, 0, 0}, {0, 0, 1}, {0, 1, 0}, {0, 1, 1}, {1, 0, 0}, {1, 0, 1}, {1, 1, 0}, {1, 1, 1} };

// ----- keypad -----

#define ROWS 4
#define COLS 4

char keys[ROWS][COLS] = { { 'a', 'b', 'c', 'd' }, { 'e', 'f', 'g', 'h' }, { 'i', 'j', 'k', 'l' }, { 'm', 'n', 'o', 'p' } };

byte rowPin[COLS] = { 9, 8, 7, 6 };  // connect to L1-L4
byte colPin[ROWS] = { 5, 4, 3, 2 };  // connect to R1-R4

Keypad keypad = Keypad(makeKeymap(keys), rowPin, colPin, ROWS, COLS);

// ----- rotor -----

#define ROTOR_CLK 15
#define ROTOR_DT 16

#define FIDELITY 2

int counter = 0; 
int lastState = 0;

int aState;
int aLastState; 

void setupRotor() {
  aLastState = digitalRead(ROTOR_CLK);   
}

/**
 * @return int -1 if rotor state has decremented, 1 if state has incremented, 0 if unchanged.
 */
int getRotor() {
  int val = 0;
  aState = digitalRead(ROTOR_CLK);

  if (aState != aLastState) {
    if (digitalRead(ROTOR_DT) != aState) ++counter; 
    else --counter; 

    if (abs(counter - lastState) >= FIDELITY) {
      val = counter > lastState ? 1 : -1;
      lastState = counter;
    }
  } 
  aLastState = aState;
  return val;
}

// -----------------

void setup() {
  Serial.begin(9600);
  
  // leds
  int leds[5] = { S0, S1, S2, OUTPUT_PIN, MUTE_PIN };
  for (int i = 0; i < 5; ++i) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }
  
  // rotor
  setupRotor();
  pinMode(ROTOR_CLK, INPUT);
  pinMode(ROTOR_DT, INPUT);
}

void writeLed(int led) {
  digitalWrite(S2, binary[led][0]);
  digitalWrite(S1, binary[led][1]);
  digitalWrite(S0, binary[led][2]);
}

void loop() {
  // leds
  if (Serial.available() > 0) {
    int led = Serial.read();
    if (led >= 0 && led <= 7) writeLed(led); // 0-7 is scene LED
    else if (led == 8) digitalWrite(OUTPUT_PIN, HIGH); // 8 is output_state off
    else if (led == 9) digitalWrite(OUTPUT_PIN, LOW); // 9 is output_state on
    // 10 is mute off
    // 11 is mute on
  }

  // keypad
  int key = (int) keypad.getKey() - 'a';
  if (key >= 0) Serial.write(key); // 0-15 from keypad

  // rotor
  int rotor = getRotor();
  if (rotor < 0) Serial.write(16); // 16 is rotor decrement
  else if (rotor > 0) Serial.write(17); // 17 is rotor increment
}

