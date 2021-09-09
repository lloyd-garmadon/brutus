#include "Arduino.h"

#include <him_log.h>
#include <him_distance.h>
#include <him_servo.h>

#define QuoteIdent(ident) #ident
#define QuoteMacro(macro) QuoteIdent(macro)

#define PROJECT_NAME           brutus_radar
#define PROJECT_VERSION_MAJOR  1
#define PROJECT_VERSION_MINOR  0
#define PROJECT_VERSION_PATCH  0

#define PROJECT_NAME_STRING     QuoteMacro(PROJECT_NAME)
#define PROJECT_VERSION_STRING  QuoteMacro(PROJECT_VERSION_MAJOR) "." QuoteMacro(PROJECT_VERSION_MINOR) "." QuoteMacro(PROJECT_VERSION_PATCH)



HimServo rotor(9);
HimUltrasonicSensor sensor(7,6,200);

int position = 0;
int position_end_r = 60;
int position_end_l = -60;
int increment = 5;
int direction = 1;

bool running = false;



void setup() {
    // opens serial port, sets data rate to 57600 baud
    him_log_init(57600);

    rotor.init();
}



void loop() {

    int incomingByte = 0;
    bool cmd_start   = false;
    bool cmd_stop    = false;

    if(Serial.available() > 0) {
        incomingByte = Serial.read();
        switch(incomingByte) {
        case 'v':
            him_logd("Project: %s\n", PROJECT_NAME_STRING);
            him_logd("Version: %s\n", PROJECT_VERSION_STRING);
            break;
        case 'w':
            cmd_start = true;
            break;      
        case 'q':
            cmd_stop = true;
            break;      
        case 27:
            him_logd("Exit\n");
            exit(0);
            break;
        default:;
        }
    }

    if(cmd_start) {
        if(!running) {
            position = 0;
            running = true;
            rotor.setPos(position);
            him_logd(HIM_LOG_ERASE_SCREEN);
        }
    } else if(cmd_stop) {
        if(running) {
            position = 0;
            running = false;
            rotor.setPos(position);
        }
    } 

    if ( running ) {
        position += direction * increment;
        if(position >= position_end_r) {
            position = position_end_r;
            direction = -direction;
        } else if(position <= position_end_l) {
            position = position_end_l;
            direction = -direction;
        }
        rotor.setPos(position);
        delay(200);
        
        unsigned int distance;
        bool ok = sensor.measure(distance);
        
        him_logd_pos( (1 + (position_end_r + position) / increment), 1);
        him_logd("pos:%3d - %3d - %s", position, distance, ok ? "valid  " : "invalid" );
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
