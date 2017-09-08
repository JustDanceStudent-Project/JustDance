################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Source/portable/MemMang/heap_2.c 

C_DEPS += \
./Source/portable/MemMang/heap_2.d 

OBJS += \
./Source/portable/MemMang/heap_2.o 


# Each subdirectory must supply rules for building sources it contributes
Source/portable/MemMang/%.o: ../Source/portable/MemMang/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: AVR Compiler'
	avr-gcc -I"C:\Users\avidr\Google Drive\Workspace\Git Repository\JustDanceStudent-Project\JustDance\ArduinoMEGA\eclipse\ArduinoMEGA_OS_Setup.zip_expanded\freeRTOS\Source\include" -Wall -Os -fpack-struct -fshort-enums -ffunction-sections -fdata-sections -std=gnu99 -funsigned-char -funsigned-bitfields -mmcu=atmega328p -DF_CPU=16000000UL -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


