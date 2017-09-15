#include <Arduino.h>
#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>

#define STACK_SIZE   200
#define LED_PIN      6

void task1(void *p)
{
	for (;;) {
	  digitalWrite(LED_PIN, HIGH);
	  delay(1000);
	  digitalWrite(LED_PIN, LOW);
	  delay(1000);
	}
}

void setup()
{
	pinMode(LED_PIN, OUTPUT);
}

void loop() {
	xTaskCreate(task1,           // Pointer to the task entry function
		     "Task1",         // Task name
		     STACK_SIZE,      // Stack size
		     NULL,            // Pointer that will be used as parameter
		     1,               // Task priority
		    NULL);           // Used to pass back a handle by which the created task can be referenced.
	vTaskStartScheduler();
}

