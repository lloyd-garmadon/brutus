#include "Arduino.h"

#include <him_log.h>
#include <him_distance.h>
#include <him_servo.h>

HimServo rotor(9);
HimUltrasonicSensor sensor(7,6,200);

unsigned int distance;
int position;
int count;
bool ok;


void setup() {
    // opens serial port, sets data rate to 57600 baud
    him_log_init(57600);
    him_logd(HIM_LOG_ERASE_SCREEN);

    him_logd("setup\n");
    rotor.init();

    count = 0;
}


void loop() {
    him_logd(HIM_LOG_CURSOR_HOME);
    him_logd("loop %d\n", count++);

    for (position = -60; position < 60; position += 5) {
        rotor.setPos(position);
        delay(200);
        ok = sensor.measure(distance);
        him_logd("pos:%3d - %3d - %s", position, distance, ok ? "valid  " : "invalid" );
        for(int i=0; i<200; i+=10) {
            if(i<distance){
                him_logd("-");
            } else {
                him_logd("#");
            }
        }
        him_logd("\n");
    }

    //if(count == 2) while (1);
}
