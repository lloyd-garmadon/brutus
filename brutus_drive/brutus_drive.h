#include "Arduino.h"

#include <him_utilities.h>
#include <him_log.h>
#include <him_cmd.h>
#include <him_motor.h>
#include <him_speed.h>


struct brutus_handle_ {
    HimMotor2PinPWM motor_l;
    HimMotor2PinPWM motor_r;

    HimSpeedHallSensor motor_sensor_l;
    HimSpeedHallSensor motor_sensor_r;

    int speed_control_l;
    int speed_control_r;

    int speed_sensor_l;
    int speed_sensor_r;
};

