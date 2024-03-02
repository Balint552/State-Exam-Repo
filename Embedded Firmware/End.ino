/*
#include <Wire.h>
#define RXD2 16
#define TXD2 17

String Latitude;
String Longitude;

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
}

void loop() {
    if (Serial2.available() > 0) { // Ellenorzi, hogy van-e adat a soros porton
    String receivedData = Serial2.readStringUntil('\n'); // Beolvassa az adatot, amig el nemeri a sortorest

    if (receivedData.startsWith("$GNGLL")) {
  

      int lat1commandIndex = receivedData.indexOf(',') + 1; // A vesszo utani elso karakter
      int lat2commandIndex = receivedData.indexOf(',', lat1commandIndex); // A kovetkezo vesszo

      int lon1commandIndex = receivedData.indexOf(',', lat2commandIndex) + 3; //Az azutani karkter 
      int lon2commandIndex = receivedData.indexOf(',', lon1commandIndex); // A következo vesszo

      if (lat1commandIndex != -1 && lat2commandIndex != -1 && lon1commandIndex != -1 && lon2commandIndex != -1) {
        Latitude = receivedData.substring(lat1commandIndex, lat2commandIndex);
        Longitude = receivedData.substring(lon1commandIndex, lon2commandIndex);
        
        Serial.print(Latitude);
        Serial.print(" ");
        Serial.print(Longitude);
        Serial.println();
      }
    }
  }
}
*/

#include <Ticker.h>
#include <Wire.h>
#include <LSM6.h>
#include <LIS3MDL.h>
#include <cmath>
#include <stdio.h>
#include <math.h>

// Konstansok
#define RXD2 16
#define TXD2 17

float g = 9.81;
LSM6 lsm6;
LIS3MDL lis3mdl;
String Latitude;
String Longitude;

union ble_data {
  struct __attribute__((packed)) {
    uint32_t time_stamp;
    int32_t accel_x;
    int32_t accel_y;
    int32_t gyro_z;
    int32_t mag_x;
    int32_t mag_y;
    int32_t mag_z;
    char GPS_x[11];
    char GPS_y[11];
    float ACCEL_X_CALLC;
    float ACCEL_Y_CALLC;
    float GYRO_Z_CALLC;
    float MAG_XY_CALLC;
  };
  uint8_t bytes[52];
};

// Idozito valtozok
Ticker millisecondTicker;
volatile uint32_t milliseconds = 0;

// Esemenycsoport kezelo
EventGroupHandle_t xACQEventGroup;

// Idozito megszakitas kezelo
void IRAM_ATTR incrementMilliseconds() {
  milliseconds++;
}
// Adatgyujtes fuggveny
void data_acquisition_task(void* parameter) {
  union ble_data packet;
  bool is_measurement_on = true;
  EventBits_t uxBits;

  while (1) {
    uxBits = xEventGroupGetBits(xACQEventGroup);

    if (is_measurement_on) {
      // IMU adatok olvasasa
      lsm6.read();
      lis3mdl.read();

      // GPS adatok olvasasa
          if (Serial2.available() > 0) { // Ellenorzi, hogy van-e adat a soros porton
          String receivedData = Serial2.readStringUntil('\n'); // Beolvassa az adatot, amig el nemeri a sortorest

          if (receivedData.startsWith("$GNGLL")) {
        

            int lat1commandIndex = receivedData.indexOf(',') + 1; // A vesszo utani elso karakter
            int lat2commandIndex = receivedData.indexOf(',', lat1commandIndex); // A kovetkezo vesszo

            int lon1commandIndex = receivedData.indexOf(',', lat2commandIndex) + 3; //Az azutani karkter 
            int lon2commandIndex = receivedData.indexOf(',', lon1commandIndex); // A következo vesszo

            if (lat1commandIndex != -1 && lat2commandIndex != -1 && lon1commandIndex != -1 && lon2commandIndex != -1) {
              Latitude = receivedData.substring(lat1commandIndex, lat2commandIndex);
              Longitude = receivedData.substring(lon1commandIndex, lon2commandIndex);
            }
          }
        }
      
      }

      // Adatcsomag osszeallitasa
      packet.time_stamp = milliseconds;
      packet.accel_x = (int32_t)(lsm6.a.x);
      packet.accel_y = (int32_t)(lsm6.a.y);
      packet.gyro_z = (int32_t)(lsm6.g.z);
      packet.mag_x = (int32_t)(lis3mdl.m.x);
      packet.mag_y = (int32_t)(lis3mdl.m.y);
      packet.mag_z = (int32_t)(lis3mdl.m.z);
      strcpy(packet.GPS_x, Latitude.c_str()); // Konvertaljuk a Stringet const char*-ra es masoljuk a tombbe
      strcpy(packet.GPS_y, Longitude.c_str()); // Konvertáljuk a Stringet const char*-ra es masoljuk a tombbe
      packet.ACCEL_X_CALLC = (float)((lsm6.a.x*g)/pow(2, 15));
      packet.ACCEL_Y_CALLC = (float)((lsm6.a.y*g)/pow(2, 15));
      packet.GYRO_Z_CALLC = (float)((lsm6.g.z*250)/pow(2, 15));
      packet.MAG_XY_CALLC = (float)(atan2(lis3mdl.m.x,lis3mdl.m.y));

      // Adatcsomag kuldese soros porton
      Serial.print(packet.time_stamp);
      Serial.print(",");
      Serial.print(packet.accel_x);
      Serial.print(",");
      Serial.print(packet.accel_y);
      Serial.print(",");
      Serial.print(packet.gyro_z);
      Serial.print(",");
      Serial.print(packet.mag_x);
      Serial.print(",");
      Serial.print(packet.mag_y);
      Serial.print(",");
      Serial.print(packet.mag_z);
      Serial.print(",");
      Serial.print(packet.GPS_x);
      Serial.print(",");
      Serial.print(packet.GPS_y);
      Serial.print(",");
      Serial.print(packet.ACCEL_X_CALLC);
      Serial.print(",");
      Serial.print(packet.ACCEL_Y_CALLC);
      Serial.print(",");
      Serial.print(packet.GYRO_Z_CALLC);
      Serial.print(",");
      Serial.print(packet.MAG_XY_CALLC);
      Serial.print("\n");
    }
    vTaskDelay(30 / portTICK_PERIOD_MS);
  }


void setup() {
  setCpuFrequencyMhz(240);
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Wire.begin();
  if (!lsm6.init() || !lis3mdl.init()) {
    Serial.println("LSM6 vagy LIS3MDL inicializálása sikertelen!");
    while (1);
  }
  lsm6.enableDefault();
  lis3mdl.enableDefault();

  millisecondTicker.attach_ms(1, incrementMilliseconds);

  xACQEventGroup = xEventGroupCreate();
  if (xACQEventGroup == NULL) {
    Serial.println("Hiba az eseménycsoport létrehozásakor!");
  }
 
  xTaskCreatePinnedToCore(data_acquisition_task, "Task1", 10000, NULL, 1, NULL, 0);
}

void loop() {
  // A loop fuggvény ures, mivel a muveleteket a data_acquisition_task vegzi
}



