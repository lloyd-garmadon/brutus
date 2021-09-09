#include "Arduino.h"

#include <him_log.h>
#include <him_motor.h>
#include <him_speed.h>

#define QuoteIdent(ident) #ident
#define QuoteMacro(macro) QuoteIdent(macro)

#define PROJECT_NAME           brutus_drive
#define PROJECT_VERSION_MAJOR  1
#define PROJECT_VERSION_MINOR  0
#define PROJECT_VERSION_PATCH  0

#define PROJECT_NAME_STRING     QuoteMacro(PROJECT_NAME)
#define PROJECT_VERSION_STRING  QuoteMacro(PROJECT_VERSION_MAJOR) "." QuoteMacro(PROJECT_VERSION_MINOR) "." QuoteMacro(PROJECT_VERSION_PATCH)



HimMotor2PinPWM motor_l( 9,  8, false);
HimMotor2PinPWM motor_r(10, 11, false);

HimSpeedHallSensor motor_sensor_l(3, 5, true);
HimSpeedHallSensor motor_sensor_r(2, 4, false);

int speed_control_l;
int speed_control_r;

int speed_sensor_l;
int speed_sensor_r;



void setup() {
  // opens serial port, sets data rate to 57600 baud
  him_log_init(57600);
}



void loop() {
  int incomingByte = 0;
  
  if(Serial.available() > 0) {
    incomingByte = Serial.read();
    switch(incomingByte) {
      case 'v':
        him_logd("Project: %s\n", PROJECT_NAME_STRING);
        him_logd("Version: %s\n", PROJECT_VERSION_STRING);
        break;      
      case 'w':
        him_logd("Motor forward\n");
        speed_control_l = motor_l.incrementSpeed(10);
        speed_control_r = motor_r.incrementSpeed(10);
        break;      
      case 's':
        him_logd("Motor backward\n");
        speed_control_l = motor_l.decrementSpeed(10);
        speed_control_r = motor_r.decrementSpeed(10);
        break;      
      case 'a':
        him_logd("Motor left\n");
        speed_control_l = motor_l.decrementSpeed(10);
        speed_control_r = motor_r.incrementSpeed(10);
        break;      
      case 'd':
        him_logd("Motor right\n");
        speed_control_l = motor_l.incrementSpeed(10);
        speed_control_r = motor_r.decrementSpeed(10);
        break;      
      case 'q':
        him_logd("Motor stop\n");
        speed_control_l = motor_l.stop();
        speed_control_r = motor_r.stop();
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
        him_logd("Motor Left:  %3d  Motor Right:  %3d\n", speed_control_l, speed_control_r);
        break;
      default:;
    }
  }

  motor_sensor_l.getIncrement(speed_sensor_l, true);
  motor_sensor_r.getIncrement(speed_sensor_r, true);
  him_logd("Encoder Left:%3d  Encoder Right:%3d\n", speed_sensor_l, speed_sensor_r);

  delay(10);
}
