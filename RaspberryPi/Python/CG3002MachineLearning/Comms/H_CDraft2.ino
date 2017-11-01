
#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050.h"
 
#include <SparkFun_ADXL345.h>

#include <Arduino_FreeRTOS.h>
#include <semphr.h>

#define SEN_BUF_SIZE 50
int16_t ACK = 0, HELLO = 2,TMP = 4;


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

float Ax1, Ay1, Az1;
float Gx1, Gy1, Gz1;

float Ax2, Ay2, Az2;

const int SENSOR_PIN = A0;  // Input pin for measuring Vout
const float RS = 0.00999*10;          // Shunt resistor value (in ohms)*RL
const float VOLTAGE_REF = 5.0;  // Reference voltage for analog read

static SemaphoreHandle_t bufSemaphore;

typedef struct acc {
        float accelx1;
        float accely1;
        float accelz1;
        float gyrox1;
        float gyroy1;
        float gyroz1;
        
        float accelx2;
        float accely2;
        float accelz2;
        /*float sencur;
        float senvol;
        float senpw;*/
      //String d[MAX_STORAGE_SIZE];
        
        
} accStorage;
accStorage value;

static accStorage sensorBuf[SEN_BUF_SIZE];
static int sensorBufEmptyId = 0;
static int sensorBufFilledId = 0;
// Global Variables
int sensorValue;   // Variable to store value from analog read
float current;       // Calculated current value
float v2;

 float vPow = 4.8;
 float r1 = 9848;
 float r2 = 986.3;
 float power;
 float c;
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
  Serial.begin(9600);
  Serial1.begin(9600);
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

  xTaskCreate(generateData, "Task1", 128, NULL,3,NULL);
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

static void generateData(void *pvParameters){
  while(1){
        
//    mpu.setXGyroOffset(35);
//    mpu.setYGyroOffset(-40);
//    mpu.setZGyroOffset(-20);
//    mpu.setXAccelOffset(-3005);
//    mpu.setYAccelOffset(-1990);
//    mpu.setZAccelOffset(1070);
    
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
    
  
//  Serial.print(ax2);
//  Serial.print("\t");
//  Serial.print(ay2);
//  Serial.print("\t");
//  Serial.print(az2);
//  Serial.print("\t");
//  Serial.print(Ax1);
//  Serial.print("\t");
//  Serial.print(Ay1);
//  Serial.print("\t");
//  Serial.print(Az1);
//  Serial.print("\t");
//  Serial.print(Gx1);
//  Serial.print("\t");
//  Serial.print(Gy1);
//  Serial.print("\t");
//  Serial.print(Gz1);
//  Serial.println("\t");
//  

    // display tab-separated accel/gyro x/y/z values

    //voltage
    float v = (analogRead(2) * vPow) / 1023.0;
    float v2 = v / (r2 / (r1 + r2));
   

   
    //Serial.print(v2);
    //Serial.println(" V");
    // Read a value from the INA169 board
    sensorValue = analogRead(4);
    //Serial.print(sensorValue);
    // Remap the ADC value into a voltage number (v2)
    c=(sensorValue * VOLTAGE_REF) / 1024.0;

    // Follow the equation given by the INA169 datasheet to
    // determine the current flowing through RS. Assume RL = 10k
    // Is = (Vout x 1k) / (RS x RL)
    current = c / RS;
    // current = c / RS+v2/(r1+r2);
    //current = sensorValue / (10 * RS);
    //Serial.print(sensorValue, 10);
    //Serial.print(current, 5);
    //Serial.println(" A");

    power=current*v2;
    //Serial.print(power, 5);
    //Serial.println(" W");
    //delay(500);
    xSemaphoreGive(bufSemaphore);
    vTaskDelay(1);
    
  }
}

static void sendData(void *pvParameters){
  while(1)
  {  
    
     //char buffer[2560];
     //char temp[2560];
     //char type = 'A';
    //Serial.println(F("Task2"));
    //Serial.println("Add Sensor Data");
    value.accelx1 = Ax1;
    value.accely1 = Ay1;
    value.accelz1 = Az1;
    value.gyrox1 = Gx1;
    value.gyroy1 = Gy1;
    value.gyroz1 = Gz1;
    value.accelx2 = Ax2;
    value.accely2 = Ay2;
    value.accelz2 = Az2;

    /*value.sencur = current;
    value.senvol = v2;
    value.senpw = power;*/

    sensorBuf[sensorBufEmptyId] = value;
    sensorBufEmptyId = (sensorBufEmptyId+1) % SEN_BUF_SIZE;
    //value.sencur = current;
    //value.senvol = v2;
    //value.senpw = power;
    //value.d[sen_size] = "*";
    //Serial.println(value.accelx1[sen_size]);
    //Serial.println(value.gyrox1[sen_size]);
    //sen_size = (sen_size+1)%MAX_STORAGE_SIZE;
//    Serial.println(value.gyrox1,7);
//    Serial.println(value.accely2,7);
//    Serial.println("gyrox1");
//    int len = serialize(buffer,&value,sizeof(value));
//    Serial.println(len);
//    send(buffer,len);

    xSemaphoreGive(bufSemaphore);    
    vTaskDelay(1);
  }
  
}

static void transmitData(void* pvParameters)
{ 
  int i =0;
  //accStorage send_value;
  
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
    accStorage send_value;
    //accStorage a;
    send_value = sensorBuf[i];
    i = (i+1)%SEN_BUF_SIZE;
   
    Serial.print("MPU:\t");
    Serial1.println("MPU:");
    Serial.print(send_value.accelx1,4); 
    Serial.print("\t");
    Serial1.println(send_value.accelx1,4);
    Serial.print(send_value.accely1,4); 
    Serial.print("\t");
    Serial1.println(send_value.accely1,4);
    Serial.print(send_value.accelz1,4); 
    Serial.print("\t");
    Serial1.println(send_value.accelz1,4);
    Serial.print(send_value.gyrox1,4); 
    Serial.print("\t");
    Serial1.println(send_value.gyrox1,4);
    Serial.print(send_value.gyroy1,4); 
    Serial.print("\t");
    Serial1.println(send_value.gyroy1,4);
    Serial.print(send_value.gyroz1,4); 
    Serial.print("\t");
    Serial1.println(send_value.gyroz1,4);

    Serial.print("\t");
    Serial.print("ADXL:\t");
    Serial1.println("ADXL:");
    Serial.print(send_value.accelx2,4); 
    Serial.print(" ");
    Serial1.println(send_value.accelx2,4);
    Serial.print(send_value.accely2,4); 
    Serial.print(" ");
    Serial1.println(send_value.accely2,4);
    Serial.print(send_value.accelz2,4); 
    Serial.println(" ");
    Serial1.println(send_value.accelz2,4);
    
//    Serial.print(send_value.gyrox2,4); Serial.print("\t");
//    Serial1.println(send_value.gyrox2,4);
//    Serial.print(send_value.gyroy2,4); Serial.print("\t");
//    Serial1.println(send_value.gyroy2,4);
//    Serial.println(send_value.gyroz2,4);
//    Serial1.println(send_value.gyroz2,4);
    /*Serial.print("Voltage:\t");
    Serial.print(send_value.sencur,4); Serial.print("\t");
    Serial1.println(send_value.sencur,4);
    Serial.print(send_value.senvol,4); Serial.print("\t");
    Serial1.println(send_value.senvol,4);
    Serial.print(send_value.senpw,4); Serial.print("\t");
    Serial1.println(send_value.senpw,4);*/

    
    //Serial1.println(send_value.gyrox2,4);
    int len = serialize(buffer,&send_value,sizeof(send_value));
    
    //send(buffer,len);
    //Serial1.write(buffer[5]);
    //Serial.write(buffer,len);
    //Serial.println("send data successful");
//    xSemaphoreGive(bufSemaphore);  
//    vTaskDelay(1);
      
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

void send(char *buf, int len){
  Serial.write(buf,len);
  Serial1.flush();
  Serial1.write("\n");
  delayMicroseconds(10);
}

void loop() {
  //do nothing
}



