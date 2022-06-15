

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

#include <Wire.h>
#include <DmxSimple.h>
#include <TFLI2C.h>

TFLI2C tflI2C;
int lidar_distance = 0; // Lidar distance 
int lidar_i2c_addr= TFL_DEF_ADR;  // Default I2C address for the Lidar

int MIN = 100 , MAX = 160;
/*
 * First channel :
 * 0 to 128 : dimmer 
 * 128 to 255: blink frequency 
 * Then RGBW channels 
 * Last channel make the light blink more or less, 0 -> Full black , 255 -> Zero blink 
 */

int PROJ_ADDR = 10;

void setup() {

  Serial.begin(9600);
  Wire.begin();
  
  DmxSimple.usePin(5);
  DmxSimple.maxChannel(7);
  for (int i = 0 ; i< 9; i++)
    DmxSimple.write(PROJ_ADDR+i, 0); // Dimmer
  
  // Init strombo
  DmxSimple.write(PROJ_ADDR, 255); // Dimmer
  set_projo_red();
  DmxSimple.write(PROJ_ADDR+4, 0); // White
  DmxSimple.write(PROJ_ADDR+5, 0); // Zero blink
  DmxSimple.write(PROJ_ADDR+6, 0); // Zero blink
  DmxSimple.write(PROJ_ADDR+7, 0); // Zero blink
  DmxSimple.write(PROJ_ADDR+8, 0); // Zero blink
}

void set_projo_red() {
  DmxSimple.write(PROJ_ADDR+1, 255);
  DmxSimple.write(PROJ_ADDR+2, 0);
  DmxSimple.write(PROJ_ADDR+3, 0);  
}
void set_projo_green() {
  DmxSimple.write(PROJ_ADDR+1, 0); 
  DmxSimple.write(PROJ_ADDR+2, 255);
  DmxSimple.write(PROJ_ADDR+3, 0);  
}
void set_projo_blue() {
  DmxSimple.write(PROJ_ADDR+1, 0); 
  DmxSimple.write(PROJ_ADDR+2, 0);
  DmxSimple.write(PROJ_ADDR+3, 255);  
}



int read_sensor_value() {
  if (!tflI2C.getData( lidar_distance, lidar_i2c_addr)) {
       tflI2C.printStatus();
   }
}

char* is_sensor_activated() {
    if (lidar_distance > MIN && lidar_distance < MAX)
      return "yes";
    else 
      return "no";
}

void loop() {
/*
  for (int i = 0 ; i < 255 ; i++) {
    DmxSimple.write(PROJ_ADDR, i);
     delay(200);
  }
  */
  read_sensor_value();
  if(Serial.available()) {
    String request = Serial.readString();
    if (strncmp(request.c_str(), "is_activated" , strlen("read_sensor")) == 0)
      Serial.println(is_sensor_activated());
  }


    if (lidar_distance > MIN && lidar_distance < MAX) {
      set_projo_green();
    }
    else {
      set_projo_red();      
    }

  delay(500);
}
