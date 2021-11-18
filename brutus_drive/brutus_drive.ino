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
bool cmd_forward(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->speed_control_l = p_brutus->motor_l.incrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.incrementSpeed(10);

    him_cmd_response_cmd(cookie, res, "cmd_forward %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

bool cmd_backward(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->speed_control_l = p_brutus->motor_l.decrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.decrementSpeed(10);

    him_cmd_response_cmd(cookie, res, "cmd_backward %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

bool cmd_left(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->speed_control_l = p_brutus->motor_l.decrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.incrementSpeed(10);

    him_cmd_response_cmd(cookie, res, "cmd_left %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

bool cmd_right(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->speed_control_l = p_brutus->motor_l.incrementSpeed(10);
    p_brutus->speed_control_r = p_brutus->motor_r.decrementSpeed(10);

    him_cmd_response_cmd(cookie, res, "cmd_right %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

bool cmd_stop(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->speed_control_l = p_brutus->motor_l.stop();
    p_brutus->speed_control_r = p_brutus->motor_r.stop();

    him_cmd_response_cmd(cookie, res, "cmd_stop %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

bool cmd_center(int cookie, void * p_data)
{
    int res = 0;

    int speed = (p_brutus->speed_control_l + p_brutus->speed_control_r) / 2;

    p_brutus->speed_control_l = p_brutus->motor_l.setSpeed(speed);
    p_brutus->speed_control_r = p_brutus->motor_r.setSpeed(speed);

    him_cmd_response_cmd(cookie, res, "cmd_center %d %d", p_brutus->speed_control_l, p_brutus->speed_control_r);
    return !res;
}

void msg_speed(int res, int speed_l, int speed_r )
{
    him_cmd_response_msg("speed", res, true, "%3d %3d", speed_l, speed_r );
}


//
// setup function
//
void setup() {
    him_serial_init(57600);

    him_cmd_set_name(PROJECT_NAME_STRING, PROJECT_VERSION_STRING);
    him_cmd_set_echo(false);
    him_cmd_assign_cmd("w", cmd_forward,  NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Increments left and right motor speed by 10");
    him_cmd_assign_cmd("s", cmd_backward, NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Decrements left and right motor speed by 10");
    him_cmd_assign_cmd("a", cmd_left,     NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Increments/decrements left and right motor  by 10 to turn left");
    him_cmd_assign_cmd("d", cmd_right,    NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Increments/decrements left and right motor  by 10 to turn right");
    him_cmd_assign_cmd("q", cmd_stop,     NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Stops motors");
    him_cmd_assign_cmd("e", cmd_center,   NULL,
                        "<speed_ctrl_l> <speed_ctrl_r>",
                        "",
                        "Centers left and right motor speed to driver straight forward");

    him_cmd_assign_msg( "speed",
                        "<speed_l> <speed_r>",
                        "returns the current speed");

}



//
// main loop function
//
void loop() {

    him_cmd_update();

    p_brutus->motor_sensor_l.getIncrement(p_brutus->speed_sensor_l, true);
    p_brutus->motor_sensor_r.getIncrement(p_brutus->speed_sensor_r, true);

    msg_speed(0, p_brutus->speed_sensor_l, p_brutus->speed_sensor_r );

    delay(70);
}

