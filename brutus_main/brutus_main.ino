#include "Arduino.h"

#include <him_log.h>
#include <him_motor.h>

HimMotor2PinPWM motor_l(10,11,false);
HimMotor2PinPWM motor_r(9,8,false);

int speed_l;
int speed_r;

int incomingByte = 0;



void setup() {
  // opens serial port, sets data rate to 57600 baud
  him_log_init(57600);
}

void loop() {
  
  if(Serial.available() > 0) {
    incomingByte = Serial.read();
    switch(incomingByte) {
      case 'w':
        him_logd("Motor forward\n");
        speed_l = motor_l.incrementSpeed(10);
        speed_r = motor_r.incrementSpeed(10);
        break;      
      case 'x':
        him_logd("Motor backward\n");
        speed_l = motor_l.decrementSpeed(10);
        speed_r = motor_r.decrementSpeed(10);
        break;      
      case 'a':
        him_logd("Motor left\n");
        speed_l = motor_l.decrementSpeed(10);
        speed_r = motor_r.incrementSpeed(10);
        break;      
      case 'd':
        him_logd("Motor right\n");
        speed_l = motor_l.incrementSpeed(10);
        speed_r = motor_r.decrementSpeed(10);
        break;      
      case 's':
        him_logd("Motor stop\n");
        speed_l = motor_l.stop();
        speed_r = motor_r.stop();
        break;      
      case 27:
        him_logd("Exit\n");
        motor_l.stop();
        motor_r.stop();
        exit(0);
        break;
      default:;
    }
    switch(incomingByte) {
      case 'w':
      case 'x':
      case 'a':
      case 'd':
      case 's':
        him_logd("Motor Left:  %3d  Motor Right:  %3d\n", speed_l, speed_r);
        break;
      default:;
    }
  }

  delay(10);
}
