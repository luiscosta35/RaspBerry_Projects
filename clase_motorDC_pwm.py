import RPi.GPIO as GPIO
import time

class MotorDC:
    def __init__(self, ena, in1, in2):
        self.ENA = ena
        self.IN1 = in1
        self.IN2 = in2

        # Configuració GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.ENA, self.IN1, self.IN2], GPIO.OUT)

    def giro_derecha(self, t):
        GPIO.output(self.ENA, GPIO.HIGH)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        time.sleep(t)

    def parate(self, t):
        GPIO.output(self.ENA, GPIO.LOW)
        time.sleep(t)

    def giro_izquierda(self, t):
        GPIO.output(self.ENA, GPIO.HIGH)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        time.sleep(t)
        
    def giro_der_pwm(self, t, dutycycle):
        GPIO.output(self.ENA, GPIO.HIGH)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        pwm.ChangeDutyCycle(dutycycle)
        time.sleep(t)
        
    def giro_izq_pwm(self, t, dutycycle):
        GPIO.output(self.ENA, GPIO.HIGH)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(dutycycle)        
        time.sleep(t)