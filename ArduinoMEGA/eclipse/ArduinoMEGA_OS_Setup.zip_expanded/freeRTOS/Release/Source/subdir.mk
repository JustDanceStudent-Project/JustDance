################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Source/croutine.c \
../Source/event_groups.c \
../Source/list.c \
../Source/queue.c \
../Source/tasks.c \
../Source/timers.c 

C_DEPS += \
./Source/croutine.d \
./Source/event_groups.d \
./Source/list.d \
./Source/queue.d \
./Source/tasks.d \
./Source/timers.d 

OBJS += \
./Source/croutine.o \
./Source/event_groups.o \
./Source/list.o \
./Source/queue.o \
./Source/tasks.o \
./Source/timers.o 


# Each subdirectory must supply rules for building sources it contributes
Source/%.o: ../Source/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: AVR Compiler'
	avr-gcc -I"C:\Users\avidr\Google Drive\Workspace\Git Repository\JustDanceStudent-Project\JustDance\ArduinoMEGA\eclipse\ArduinoMEGA_OS_Setup.zip_expanded\freeRTOS\Source\include" -Wall -Os -fpack-struct -fshort-enums -ffunction-sections -fdata-sections -std=gnu99 -funsigned-char -funsigned-bitfields -mmcu=atmega328p -DF_CPU=16000000UL -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


