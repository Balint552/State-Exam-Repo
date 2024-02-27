#include <Wire.h>
#define R 6378.137
#define RXD2 16
#define TXD2 17

char gpsBuffer[100]; // Buffer a fogadott GPS adatokhoz
int gpsIndex = 0;    // Az aktuális karakter pozíciója a bufferben
bool gpsDataReady = false;

float ReturnGPS(char* s){

    int len = strlen(s);
    float sum = 0, x = 10;
   
    for (int i = 0; i < len-1; ++i) {
        if (s[i] >= '0' && s[i] <= '9') {
            float num = s[i] - '0';
            sum += x * num;
            x /= 10;
        }
    }
    
    return sum;
}
void setup() {
  Serial.begin(9600);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
}

void loop() {
  while (Serial2.available()) {
    char c = Serial2.read();
    if (c == '$') {
      gpsIndex = 0;
    }
    gpsBuffer[gpsIndex++] = c;
    if (c == '\n') {
      gpsBuffer[gpsIndex] = '\0';
      gpsIndex = 0;
      gpsDataReady = true;
    }
  }

  if (gpsDataReady) {
    if (strstr(gpsBuffer, "$GNGLL")) {
      char *token = strtok(gpsBuffer, ",");
      char *szel = strtok(NULL, ",");
      token = strtok(NULL, ",");
      char *hossz = strtok(NULL, ",");
      token = strtok(NULL, ",");
      char *ptr = hossz + 1;

      Serial.print("Szel eredeti: ");
      Serial.print(szel);
      Serial.println();
      Serial.print("Hossz eredeti: ");
      Serial.print(hossz);
      Serial.println();


      float lat2 = 46.5777591;
      float lon2 = 24.3762672;
      float lat1 = ReturnGPS(szel);
      float lon1 = ReturnGPS(ptr);
      Serial.print("Lat1:");
      Serial.print(lat1,7);
      Serial.println();

      Serial.print("Lon1:");
      Serial.print(lon1,7);
      Serial.println();

      float dLat = (lat2*(M_PI / 180.0)) - (lat1*(M_PI / 180.0));
      float dLon = (lon2*(M_PI / 180.0)) - (lon1*(M_PI / 180.0));
      float a = pow(sin(dLat / 2.0), 2) + cos(lat1*(M_PI / 180.0)) * cos(lat2*(M_PI / 180.0)) * pow(sin(dLon / 2.0), 2);
      float c = 2 * atan2(sqrt(a), sqrt(1 - a));
      float d = R * c;

      Serial.print("Distance: ");
      Serial.println(d);
      Serial.println();
    }
    gpsDataReady = false;
  }
}