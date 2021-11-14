//
// header includes and necessary defines
//
#include "brutus_radar.h"

#define PROJECT_NAME           brutus_radar
#define PROJECT_VERSION_MAJOR  1
#define PROJECT_VERSION_MINOR  0
#define PROJECT_VERSION_PATCH  0


//
// initalize the program handle
//
struct brutus_handle_ brutus = {
    HimServo(9),                    // HimServo rotor
    HimUltrasonicSensor(7,6,200),   // HimUltrasonicSensor sensor

    0,                              //  int position
    BRUTUS_RADAR_POS_MAX_L,         //  int position_end_r
    BRUTUS_RADAR_POS_MAX_R,         //  int position_end_l
    BRUTUS_RADAR_INCREMENT,         //  int increment
    BRUTUS_RADAR_DIR_R,             //  int direction

    BRUTUS_RADAR_STATE_STOP,        // int measure
    BRUTUS_RADAR_MODE_STATIC        // int mode
} ;
struct brutus_handle_ * p_brutus = &brutus;



//
// command function
//
bool cmd_start(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->state = BRUTUS_RADAR_STATE_MEASURE;

    him_cmd_response_cmd(cookie, res, "cmd_start\n");
    return !res;
}

bool cmd_stop(int cookie, void * p_data)
{
    int res = 0;

    p_brutus->state = BRUTUS_RADAR_STATE_STOP;

    him_cmd_response_cmd(cookie, res, "cmd_stop\n");

    return !res;
}

bool cmd_range(int cookie, void * p_data)
{
    int res = 0;
    int l,r;
    if ( him_cmd_getarg_count() != 3 ) {
        return false;
    } else if ( !him_cmd_getarg_int(1, l) ) {
        return false;
    } else if ( !him_cmd_getarg_int(2, r) ) {
        return false;
    } else if ( l < BRUTUS_RADAR_POS_MAX_L ) {
        return false;
    } else if ( l > BRUTUS_RADAR_POS_MAX_R ) {
        return false;
    } else if ( l > r ) {
        return false;
    }
    p_brutus->position_end_l = l;
    p_brutus->position_end_l = (p_brutus->position_end_l / p_brutus->increment) * p_brutus->increment;
    p_brutus->position_end_r = r;
    p_brutus->position_end_r = (p_brutus->position_end_r / p_brutus->increment) * p_brutus->increment;
    p_brutus->position = (r - l) / 2 + l;
    p_brutus->position = (p_brutus->position / p_brutus->increment) * p_brutus->increment;
    p_brutus->rotor.setPos(p_brutus->position);
    p_brutus->mode = BRUTUS_RADAR_MODE_SCAN;

    him_cmd_response_cmd(cookie, res, "cmd_range %3d %3d", p_brutus->position_end_l, p_brutus->position_end_r );
    return !res;
}

bool cmd_pos(int cookie, void * p_data)
{
    int res = 0;
    int p;
    if ( him_cmd_getarg_count() != 2 ) {
        return false;
    } else if ( !him_cmd_getarg_int(1, p) ) {
        return false;
    } else if ( p < BRUTUS_RADAR_POS_MAX_L ) {
        return false;
    } else if ( p > BRUTUS_RADAR_POS_MAX_R ) {
        return false;
    }
    p_brutus->position = p;
    p_brutus->position = (p_brutus->position / p_brutus->increment) * p_brutus->increment;
    p_brutus->rotor.setPos(p_brutus->position);
    p_brutus->mode = BRUTUS_RADAR_MODE_STATIC;

    him_cmd_response_cmd(cookie, res, "cmd_pos %3d", p_brutus->position);
    return !res;
}

void msg_pos(int res, int position, int distance )
{
    him_cmd_response_msg("pos", res, true, "%3d %3d", position, distance );
}



//
// function
//
void brutus_update()
{
    if ( (p_brutus->mode == BRUTUS_RADAR_MODE_SCAN)  &&  (p_brutus->state == BRUTUS_RADAR_STATE_MEASURE) ) {
        p_brutus->position += p_brutus->direction * p_brutus->increment;
        if(p_brutus->position >= p_brutus->position_end_r) {
            p_brutus->position  = p_brutus->position_end_r;
            p_brutus->direction = -p_brutus->direction;
        } else if(p_brutus->position <= p_brutus->position_end_l) {
            p_brutus->position  = p_brutus->position_end_l;
            p_brutus->direction = -p_brutus->direction;
        }
        p_brutus->rotor.setPos(p_brutus->position);
    }
}

void brutus_measure()
{
    if ( p_brutus->state == BRUTUS_RADAR_STATE_MEASURE ) {
        unsigned int distance;
        int res = p_brutus->sensor.measure(distance) ? 0 : 1;

        delay(200);

        msg_pos(res, p_brutus->position, distance );
    }
}



//
// setup function
//
void setup() {
    him_serial_init(57600);

    p_brutus->rotor.init();
    p_brutus->rotor.setPos(0);

    him_cmd_set_name(PROJECT_NAME_STRING, PROJECT_VERSION_STRING);
    him_cmd_set_echo(false);
    him_cmd_assign_cmd( "stop",    cmd_stop,    NULL,
                        "",
                        "",
                        "stops distance measuring");
    him_cmd_assign_cmd( "start",   cmd_start,   NULL,
                        "",
                        "",
                        "starts distance measuring");
    him_cmd_assign_cmd( "range",   cmd_range,   NULL,
                        "<max_scan_angle_left> <max_scan_angle_right>",
                        "",
                        "Sets max scan angels and activates scan mode");
    him_cmd_assign_cmd( "pos",     cmd_pos,     NULL,
                        "<position>",
                        "",
                        "Sets position and activates static position mode");

    him_cmd_assign_msg( "pos",
                        "<position> <distance>",
                        "returns postion and measured distance");
    }



//
// main loop function
//
void loop() {

    him_cmd_update();

    brutus_update();

    brutus_measure();
}
