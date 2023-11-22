#include <Ticker.h>
#include <Wire.h>
#include <LSM6.h>
#include <LIS3MDL.h>


/*****************************************************************
  Defines
******************************************************************/
#define START_EVENT_BIT (1 << 0)
#define STOP_EVENT_BIT (1 << 1)

//GPS
#define RXD2 16
#define TXD2 17

//GPS GNGLL szukseges adatok kivagasa
char gpsBuffer[100]; // Buffer a fogadott GPS adatokhoz
int gpsIndex = 0;    //Az aktualis karakter pozicioja
bool gpsDataReady = false;

//IMU
LSM6 lsm6;
LIS3MDL lis3mdl;

/*****************************************************************
  Global variables and types
******************************************************************/
union ble_data {
  struct __attribute__((packed)) {
    uint32_t time_stamp;
    int32_t accel_x;
    int32_t accel_y;
    int32_t gyro_z;
    int32_t mag_x;
    int32_t mag_y;
    float GPS_x;
    float GPS_y;
  };
  uint8_t bytes[32];
};

Ticker millisecondTicker;
volatile uint32_t milliseconds = 0;

EventGroupHandle_t xACQEventGroup;

void IRAM_ATTR incrementMilliseconds() {
  milliseconds++;
}

float szel_float = 0.0; 
float hossz_float = 0.0;

void data_acquisition_task(void* parameter) {
  union ble_data packet;
  bool is_measurement_on = true;
  EventBits_t uxBits;

  while (1) {
    uxBits = xEventGroupGetBits(xACQEventGroup);

    if (is_measurement_on) {
      /*****************************************************************
       IMU
       *****************************************************************/
      lsm6.read();
      lis3mdl.read();
      /*****************************************************************
        GPS
       *****************************************************************/
       // Olvassuk a GPS adatokat a bufferbe
  while (Serial2.available()) {          //Olvasok folyamatosan a soros porton
    char c = Serial2.read();             //Atadom a beolvasott karaktert a c valtozonak
    if (c == '$') {                      //Ellenorzom hogy ha egy dollarjel 
                                         //Mivel mindegyik GPS adat $ jellel kezdodik igy mikor ujj csomag erkezik akkor lennulaza a gpsIndex -et
      gpsIndex = 0; //Hogy ujj adatot tudjon tarolni a bufferben 
    }
    gpsBuffer[gpsIndex++] = c;           //Atadodid a buffernek a c be beolvasott ertek

    if (c == '\n') {                     //Ellenorzi hogy veget ert-e a sor vagyis hogy ujj sor kezdodik 
                                         //GPS adatok \n  sortoressel vegzodnek
                                         //Ha van ilyen karakter akkor lezarjuk az olvasast
      gpsBuffer[gpsIndex] = '\0'; 
      gpsIndex = 0;                      //Nullara allitjuk az Indexet hogy egy ujj sor olvasas legyen meg

      gpsDataReady = true;               //True -ra allitjuk a DataReadyt hogy  varjuk az uj adatokat
    }
  }

  if (gpsDataReady) //Ellenozrizzuk hogy vannak-e adatok
  {
    
    if (strstr(gpsBuffer, "$GNGLL"))     //Ellenozrizzuk hogy a karaktertomb tartalmazza-e GNGLL sort
    {
      char *token = strtok(gpsBuffer, ",");// tokenekre bontas a veszo karakter alapjan

      char *szel = strtok(NULL, ",");    //Kovetkezo veszo karakter ellotti reszre mutat 
      token = strtok(NULL, ",");         // Ugrik egyet
      char *hossz = strtok(NULL, ",");
      token = strtok(NULL, ",");         // Ugrik egyet
                                         //Kiiratas
     szel_float = atof(szel);
     hossz_float = atof(hossz);
      //Serial.print(szel);
      // Serial.print(" ");
      //Serial.println(hossz);
      
      //Serial.print(gpsBuffer);
    }
    gpsDataReady = false;                //False -ra allitas hogy sikerult feldolgozni az adatot
  }
      /*****************************************************************/

      packet.time_stamp = milliseconds/1000;
      packet.accel_x = (int32_t)(lsm6.a.x);
      packet.accel_y = (int32_t)(lsm6.a.y);
      packet.gyro_z = (int32_t)(lsm6.g.z);
      packet.mag_x = (int32_t)(lis3mdl.m.x);
      packet.mag_y = (int32_t)(lis3mdl.m.y);
      packet.GPS_x = (float)(szel_float);
      packet.GPS_y = (float)(hossz_float);

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
      Serial.print(packet.GPS_x);
      Serial.print(",");
      Serial.print(packet.GPS_y);
      Serial.print("\n");
    }

    vTaskDelay(30 / portTICK_PERIOD_MS);
  }
}

void setup() {
  setCpuFrequencyMhz(240);
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);//GPS soros porti beolvasas
  Wire.begin(); //I2C olvasas
  if (!lsm6.init() || !lis3mdl.init()) {
    Serial.println("Failed to communicate with LSM6 or LIS3MDL!");
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

}

