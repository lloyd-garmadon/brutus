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
bool cmd_version(void * p_data)
{
    him_logd("%s %s\n", PROJECT_NAME_STRING, PROJECT_VERSION_STRING);
    return true;
}

bool cmd_start(void * p_data)
{
    p_brutus->state = BRUTUS_RADAR_STATE_MEASURE;
    return true;
}

bool cmd_stop(void * p_data)
{
    p_brutus->state = BRUTUS_RADAR_STATE_STOP;
    return true;
}

bool cmd_range(void * p_data)
{
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

    return true;
}

bool cmd_pos(void * p_data)
{
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

    return true;
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
        delay(200);
    }
}

void brutus_measure()
{
    if ( p_brutus->state == BRUTUS_RADAR_STATE_MEASURE ) {
        unsigned int distance;
        bool ok = p_brutus->sensor.measure(distance);

        //him_logd_pos( (1 + (p_brutus->position_end_r + p_brutus->position) / p_brutus->increment), 1);
        him_logd("pos:%3d - %3d - %s", p_brutus->position, distance, ok ? "valid  " : "invalid" );
        for(int i=0; i<200; i+=10) {
            if(i<distance){
                him_logd("-");
            } else {
                him_logd("#");
            }
        }
        him_logd("\r");
    }
}



//
// setup function
//
void setup() {
    him_serial_init(57600);

    p_brutus->rotor.init();
    p_brutus->rotor.setPos(0);

    him_cmd_set_echo(true);
    him_cmd_register("version", cmd_version, NULL);
    him_cmd_register("stop",    cmd_stop,    NULL);
    him_cmd_register("start",   cmd_start,   NULL);
    him_cmd_register("range",   cmd_range,   NULL);
    him_cmd_register("pos",     cmd_pos,     NULL);
}



//
// main loop function
//
void loop() {

    him_cmd_update();

    brutus_update();

    brutus_measure();
}
