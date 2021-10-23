//
// header includes and necessary defines
//
#include "brutus_drive.h"

#define PROJECT_NAME           brutus_drive
#define PROJECT_VERSION_MAJOR  1
#define PROJECT_VERSION_MINOR  0
#define PROJECT_VERSION_PATCH  0



//
// initalize the program handle
//
struct brutus_handle_ brutus = {
    HimMotor2PinPWM( 9,  8, false),         // HimMotor2PinPWM motor_l
    HimMotor2PinPWM(10, 11, false),         // HimMotor2PinPWM motor_r
    HimSpeedHallSensor(3, 5, true),         // HimSpeedHallSensor motor_sensor_l
    HimSpeedHallSensor(2, 4, false),        // HimSpeedHallSensor motor_sensor_r
    0,                                      // int speed_control_l
    0,                                      // int speed_control_r
    0,                                      // int speed_sensor_l
    0,                                      // int speed_sensor_r
} ;
struct brutus_handle_ * p_brutus = &brutus;



//
// command function
//
bool cmd_version(void * p_data)
{
    him_logd("%s %s\n", PROJECT_NAME_STRING, PROJECT_VERSION_STRING);
    return true;
}

bool cmd_forward(void * p_data)
{
    him_logd("cmd_forward\n");
    p_brutus->speed_control_l = p_brutus->motor_l.incrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.incrementSpeed(10);
    return true;
}

bool cmd_backward(void * p_data)
{
    him_logd("cmd_backward\n");
    p_brutus->speed_control_l = p_brutus->motor_l.decrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.decrementSpeed(10);
    return true;
}

bool cmd_left(void * p_data)
{
    him_logd("cmd_left\n");
    p_brutus->speed_control_l = p_brutus->motor_l.decrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.incrementSpeed(10);
    return true;
}

bool cmd_right(void * p_data)
{
    him_logd("cmd_right\n");
    p_brutus->speed_control_l = p_brutus->motor_l.incrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.decrementSpeed(10);
    return true;
}

bool cmd_stop(void * p_data)
{
    him_logd("cmd_stop\n");
    p_brutus->speed_control_l = p_brutus->motor_l.stop();
    p_brutus->speed_control_r = p_brutus->motor_r.stop();
    return true;
}



//
// setup function
//
void setup() {
    him_serial_init(57600);

    him_cmd_set_echo(true);
    him_cmd_assign_cmd("version", cmd_version, NULL);
    him_cmd_assign_cmd("w", cmd_forward,  NULL);
    him_cmd_assign_cmd("s", cmd_backward, NULL);
    him_cmd_assign_cmd("a", cmd_left,     NULL);
    him_cmd_assign_cmd("d", cmd_right,    NULL);
    him_cmd_assign_cmd("q", cmd_stop,     NULL);
}



//
// main loop function
//
void loop() {

    him_cmd_update();

    p_brutus->motor_sensor_l.getIncrement(p_brutus->speed_sensor_l, true);
    p_brutus->motor_sensor_r.getIncrement(p_brutus->speed_sensor_r, true);
    him_logd("Motor %3d/%3d  Sensor%3d/%3d\n", p_brutus->speed_control_l, p_brutus->speed_control_r, p_brutus->speed_sensor_l, p_brutus->speed_sensor_r);

    delay(10);
}

