#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050.h"
 
#include <SparkFun_ADXL345.h>

#include <Arduino_FreeRTOS.h>
#include <semphr.h>

#define BUF_SIZE 70
int16_t ACK = 0, HELLO = 2,TMP = 4;

#define NUM_SAMPLES 10

int sum = 0;                    // sum of samples takens
unsigned char sample_count = 0; // current sample number
//float voltage = 0.0;            // calculated voltage
const int VOLTAGE_SENSOR = A1;

// Constants
const int CURRENT_SENSOR = A0;  // Input pin for measuring Vout
const int RS = 9.1;          // Shunt resistor value (in ohms)
const int VOLTAGE_REF = 5;  // Reference voltage for analog read

// Global Variables
float sensorValue;   // Variable to store value from analog read


// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69

//MPU6050 accelgyro;
MPU6050 mpu(0x68);

//ADXL HandAcc
ADXL345 adxl = ADXL345(); 

int16_t ax1, ay1, az1;
int16_t gx1, gy1, gz1;

int16_t ax2, ay2, az2;

long Ax1, Ay1, Az1;
long Gx1, Gy1, Gz1;

float Ax2, Ay2, Az2;

long voltage, power, energy, current;

long checksum = 0;

static SemaphoreHandle_t bufSemaphore;

typedef struct acc {
        long accelx1;
        long accely1;
        long accelz1;
        long gyrox1;
        long gyroy1;
        long gyroz1;
        
        long accelx2;
        long accely2;
        long accelz2;
        
        long cur;
        long vol;
        long pw;
        long energy;
        
} accValue;
accValue value;

static accValue sensorBuf[BUF_SIZE];
static int sensorBufEmptyId = 0;
static int sensorBufFilledId = 0;


  //String str_mpugyrox = String(Ay1, 4);
 

void setup() {
  bufSemaphore = xSemaphoreCreateMutex();
  if(bufSemaphore == NULL){
    Serial.println("Error");
  }
  xSemaphoreGive(bufSemaphore);
  // join I2C bus (I2Cdev library doesn't do this automatically)
  Wire.begin();

  // initialize serial communication
  // (38400 chosen because it works as well at 8MHz as it does at 16MHz,
  //but it's really up to you depending on your project)
  Serial.begin(115200);
  Serial1.begin(115200);
  // initialize device
  Serial.println("Initializing I2C devices...");
  //accelgyro.initialize();
  mpu.initialize();

  adxl.powerOn();                     
  adxl.setRangeSetting(16);
  adxl.setSpiBit(0);
  adxl.setActivityXYZ(1, 0, 0); 
  adxl.setActivityThreshold(75);
  adxl.setInactivityXYZ(1, 0, 0); 
  adxl.setInactivityThreshold(75);  
  adxl.setTimeInactivity(10);         
  adxl.setTapDetectionOnXYZ(0, 0, 1);
  adxl.setTapThreshold(50);
  adxl.setTapDuration(15);
  adxl.setDoubleTapLatency(80);     
  adxl.setDoubleTapWindow(200);     
  adxl.setFreeFallThreshold(7);  
  adxl.setFreeFallDuration(30);

  // verify connection
  Serial.println("Testing device connections...");
  Serial.println(mpu.testConnection() ? "MPU6050 #1 connection successful" : "MPU6050 connection failed");

  Serial.println("handshake begin");
  handshake();
  Serial.println("handshake finished");
  Serial1.flush();

  xTaskCreate(getData, "Task1", 128, NULL,3,NULL);
  xTaskCreate(sendData, "Task2", 128, NULL, 2, NULL);
  xTaskCreate(transmitData, "IdleTask", 256, NULL, 1, NULL);

}

void handshake(){
  bool initFlag = true;
  int reply;
  
  while(initFlag){
    if (Serial1.available()) {
      reply = Serial1.read();
      //Serial.println(reply);
    }
    if (reply == HELLO) {
      Serial1.println(ACK);
    }
    if (reply == ACK) {
      initFlag = false;
    }
  }
}

static void getData(void *pvParameters){
  while(1){
        
    // Body Accelerometer and Gyro Readings 
    mpu.getMotion6(&ax1, &ay1, &az1, &gx1, &gy1, &gz1);  

    // Hand Accelerometer Readings  
    adxl.readAccel(&ax2, &ay2, &az2);


    Ax1 = (ax1 - (-3005));
    Ay1 = (ay1 - (-1990));
    Az1 = (az1 - (1070));

    Gx1 = (gx1 - (-35));
    Gy1 = (gy1 - (-40));
    Gz1 = (gz1 - (-20));
  
  
    Ax1=ax1/16384.0;
    Ay1=ay1/16384.0;
    Az1=az1/16384.0;
    Gx1=gx1/16384.0;
    Gy1=gy1/16384.0;
    Gz1=gz1/16384.0;
    
    Ax2=ax2;
    Ay2=ay2;
    Az2=az2;
   
    float voltage1, voltage2;
    // calculate the voltage
    // use 5.0 for a 5.0V ADC reference voltage
    // 5.015V is the calibrated reference voltage
    voltage1 = (analogRead(VOLTAGE_SENSOR)* 5.0) / 1024.0;
    voltage2 = (analogRead(VOLTAGE_SENSOR)* 5.0) / 1024.0;
    voltage1 *= 12.0;
    voltage2 *= 12.0;
    voltage = (voltage1 + voltage2)/2;


    float sensorValue1, sensorValue2, sensorValue3;
  // Read a value from the INA169 board
  sensorValue1 = analogRead(CURRENT_SENSOR);
  sensorValue2 = analogRead(CURRENT_SENSOR); 
  sensorValue3 = analogRead(CURRENT_SENSOR); 
  // Remap the ADC value into a voltage number (5V reference)
  sensorValue = (sensorValue1 + sensorValue2 + sensorValue3) / 3;
  sensorValue = (((sensorValue * voltage)/12.5) + ((sensorValue * voltage)/13))/ 2;
  
  
  // Follow the equation given by the INA169 datasheet to
  // determine the current flowing through RS. Assume RL = 10k
  // Is = (Vout x 1k) / (RS x RL)
  current = (sensorValue) / (10 * RS); 
  power = current * voltage;
  energy += power * (millis()/60000.0);
    
    xSemaphoreGive(bufSemaphore);
    vTaskDelay(1);
    
  }
}

static void sendData(void *pvParameters){ 
  while(1)
  {  
    
    value.accelx1 = Ax1;
    value.accely1 = Ay1;
    value.accelz1 = Az1;
    value.gyrox1 = Gx1;
    value.gyroy1 = Gy1;
    value.gyroz1 = Gz1;
    value.accelx2 = Ax2;
    value.accely2 = Ay2;
    value.accelz2 = Az2;
    value.cur = current;
    value.vol = voltage;
    value.pw = power;
    value.energy = energy;

    /*value.cur = current;
    value.vol = v2;
    value.pw = power;*/

    sensorBuf[sensorBufEmptyId] = value;
    sensorBufEmptyId = (sensorBufEmptyId+1) % BUF_SIZE;

    xSemaphoreGive(bufSemaphore);    
    vTaskDelay(1);
  }
  
}

static void transmitData(void* pvParameters)
{ 
  int i = 0;
  
  while(1)
  {
    int reply;
    if (Serial1.available()) {
      reply = Serial1.read();
      //Serial.println(reply);
    }
    if (reply == HELLO) {
      //Serial.println("send sensor data");
      char buffer[300];
      accValue strt;
      //accValue a;
      strt = sensorBuf[i];
      i = (i+1)%BUF_SIZE;

      checksum = strt.gyrox1 ^ strt.gyroy1 ^ strt.gyroz1 ^ strt.accelx1 ^ strt.accely1 ^ strt.accelz1 ^
                 strt.accelx2 ^ strt.accely2 ^ strt.accelz2 ^ strt.vol ^ strt.cur ^ strt.pw ^ strt.energy;
     
      Serial.print("MPU:\t");
      Serial1.println("MPU:");
      Serial.print(strt.gyrox1,4); 
      Serial.print("\t");
      Serial1.print(strt.gyrox1,4);
      Serial1.print(",");
      Serial.print(strt.gyroy1,4); 
      Serial.print("\t");
      Serial1.print(strt.gyroy1,4);
      Serial1.print(",");
      Serial.print(strt.gyroz1,4); 
      Serial.print("\t");
      Serial1.print(strt.gyroz1,4);
      Serial1.print(",");
      Serial.print(strt.accelx1,4); 
      Serial.print("\t");
      Serial1.print(strt.accelx1,4);
      Serial1.print(",");
      Serial.print(strt.accely1,4); 
      Serial.print("\t");
      Serial1.print(strt.accely1,4);
      Serial1.print(",");
      Serial.print(strt.accelz1,4); 
      Serial.print("\t");
      Serial1.print(strt.accelz1,4);
      Serial1.print(",");
//  
      Serial.print("ADXL:\t");
//      Serial1.println("ADXL:");
      Serial.print(strt.accelx2,4); 
      Serial.print(" ");
      Serial1.print(strt.accelx2,4);
      Serial1.print(",");
      Serial.print(strt.accely2,4); 
      Serial.print(" ");
      Serial1.print(strt.accely2,4);
      Serial1.print(",");
      Serial.print(strt.accelz2,4); 
      Serial.println(" ");
      Serial1.print(strt.accelz2,4);
      Serial1.print(",");

      Serial.println("PowerM:\t");
      Serial.print(strt.vol,4); Serial.print("\t");
      Serial1.print(strt.vol,4);
      Serial1.print(",");
      Serial.print(strt.cur,4); Serial.print("\t");
      Serial1.print(strt.cur,4);
      Serial1.print(",");
      Serial.print(strt.pw,4); Serial.print("\t");
      Serial1.print(strt.pw,4);
      Serial1.print(",");
      Serial.print(strt.energy,4); Serial.print("\t");
      Serial1.print(strt.energy,4);
      Serial1.println();
      
      //Serial1.println(strt.gyrox2,4);
      int len = serialize(buffer,&strt,sizeof(strt));
      
      //delayMicroseconds(10);
      delay(1);
      //send(buffer,len);
      //vTaskDelay(1);
      //Serial1.write(buffer[5]);
      //Serial.write(buffer,len);
      //Serial.println("send data successful");
  //    xSemaphoreGive(bufSemaphore);  

      
    }    
  }
  
}

unsigned int serialize(char *buf,void *data,size_t len){
 // delay(5);
  char checksum = 0;
  buf[0] = len;
  memcpy(buf+1,data,len);
  //Serial.println(buf[3]);
  for(int i = 1; i<=len;i++){
    checksum ^= buf[i];
  }
  buf[len+1] = checksum;
  return len+2;
}

void loop() {
  //do nothing
}
