#include "Arduino.h"

#include <him_utilities.h>
#include <him_log.h>
#include <him_cmd.h>
#include <him_distance.h>
#include <him_servo.h>

struct brutus_handle_ {
    HimServo rotor;
    HimUltrasonicSensor sensor;

    int position;
    int position_end_l;
    int position_end_r;
    int increment;
    int direction;

    int state;
    int mode;
};

#define BRUTUS_RADAR_POS_MAX_L        -60
#define BRUTUS_RADAR_POS_MAX_R         60
#define BRUTUS_RADAR_DIR_L             -1
#define BRUTUS_RADAR_DIR_R              1
#define BRUTUS_RADAR_INCREMENT          5

#define BRUTUS_RADAR_STATE_STOP         0
#define BRUTUS_RADAR_STATE_MEASURE      1

#define BRUTUS_RADAR_MODE_STATIC        0
#define BRUTUS_RADAR_MODE_SCAN          1
