// #include <USB.h>

// void setup() {
//     Serial.begin(9600);
// }

// void loop() {
//     Serial.println("Hello, World!");
//     delay(1000);
// }

const int LED { 17 };

// add these
const char S_OK { 0xaa };
const char S_ERR { 0xff };

void on_receive(void* event_handler_arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    // read one byte
    char state { Serial.read() };
    // guard byte is valid LED state
    if (!(state == LOW || state == HIGH)) {
        // invalid byte received
        // report error
        Serial.write(S_ERR);
        return;
    }
    // update LED with valid state
    digitalWrite(LED, state);
    Serial.write(S_OK);
}



void setup() {
    pinMode(LED, OUTPUT);

    // register "on_receive" as callback for RX event
    Serial.onEvent(ARDUINO_HW_CDC_RX_EVENT, on_receive);
    Serial.begin(9600);
}

void loop() {
    // Serial.println("Hello, World!");
    // delay(1000);
}
