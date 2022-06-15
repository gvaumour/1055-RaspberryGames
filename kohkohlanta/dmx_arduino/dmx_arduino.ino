/*
 * This sketch is meant to be played with 1055 Koh Koh Lanta
 * room, it handles the DMX connection with the stromboscope 
 * and the fan inside the room 
 * It communicates through a Serial connection with the raspberry
 * pi  
 *
 * Library Dependency: (install from the IDE) 
 *  - DmxSimple
 * Used with Groove DMX 512 and Arduino Nano
*/ 

#include <DmxSimple.h>


int STROMBO_ADDR = 10;
int FAN_ADDR = 50;

void setup() {

  // Setting the GND/VCC of the DMX controller
  pinMode(A3,OUTPUT); 
  pinMode(A2,OUTPUT); 
  digitalWrite(A2, HIGH);
  digitalWrite(A3, LOW);
  DmxSimple.usePin(A0);
  DmxSimple.maxChannel(7);

  Serial.begin(9600);

  // Init strombo
  for(int i = STROMBO_ADDR; i < STROMBO_ADDR+7; i++)
    DmxSimple.write(i,255);

}

void strombo_switch_on() {
  DmxSimple.write(STROMBO_ADDR+1,255);
}

void strombo_switch_off() {
  DmxSimple.write(STROMBO_ADDR+1,0);
}

void fan_switch_on() {
  DmxSimple.write(FAN_ADDR, 255);
}

void fan_switch_off() {
  DmxSimple.write(FAN_ADDR, 0);
}

void loop() {

  if(Serial.available()) {
    String request = Serial.readString();
    char val = 'a';
    if (strncmp(request.c_str(), "strombo_on" , strlen("strombo_on")) == 0)
      strombo_switch_on();
    else if (strncmp(request.c_str(), "strombo_off" , strlen("strombo_off")) == 0)
      strombo_switch_off();
    else if (strncmp(request.c_str(), "fan_on" , strlen("fan_on")) == 0)
      fan_switch_on();
    else if (strncmp(request.c_str(), "fan_off" , strlen("fan_off")) == 0)
      fan_switch_off();
     else 
      val = 'b';

     Serial.write(val);
  }
}
