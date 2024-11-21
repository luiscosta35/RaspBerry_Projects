import RPi.GPIO as GPIO
import time

# Configuració dels pins GPIO
CLK = 18  # Pin de l'entrada del Clock
DT = 23   # Pin de l'entrada de la Data
SW = 24   # Pin per al botó

ENA = 22  # Pin Motor
IN1 = 17  # Pin Motor
IN2 = 27  # Pin Motor

# Configurar els pins GPIO
GPIO.setmode(GPIO.BCM)  # Utilitza la numeració BCM
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pin CLK com a entrada amb pull-up
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Pin DT com a entrada amb pull-up
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Pin SW per al botó

GPIO.setup([ENA, IN1, IN2], GPIO.OUT)

motor_pin = 22 # <<--  cuidado con esta mierda!! 
               # posible conflito con la linea 9: ENA = 22   
pwm = GPIO.PWM(motor_pin, 1000)  # 1000 Hz de freqüència
pwm.start(0)  # Iniciem amb un duty cycle de 0% (motor apagat)

# Funció per llegir el valor de rotació
def read_encoder():
    clkLastState = GPIO.input(CLK)  # Llegim l'estat inicial del CLK
    counter = 0  # Comptador de la rotació

    try:
        while True:
            clkState = GPIO.input(CLK)  # Llegim l'estat actual del CLK

            # Si l'estat del CLK ha canviat (rotació)
            if clkState != clkLastState:
                # Comprovem la direcció de rotació
                if GPIO.input(DT) != clkState:
                    counter += 1  # Rotació a la dreta
                    # if counter > 0: motor1.giro_derecha(0.001)                     
                else:
                    counter -= 1  # Rotació a l'esquerra
                    # if counter < 0: motor1.giro_izquierda(0.001)                   
                    
                if counter > 100:
                    print("                             No te pases, cabrón!")
                    counter = 100
                if counter < -100:
                    print("                             No te pases, cabrón!")
                    counter = -100
                    
                if counter > 0 : motor1.giro_der_pwm(0.0001, counter)
                if counter < 0 : motor1.giro_izq_pwm(0.0001, -1*counter)
                if counter == 0: motor1.parate(0.0001)
                
                print("Valor del DutyCycle:", counter, "%")
            
            clkLastState = clkState  # Actualitzem l'estat del CLK
            time.sleep(0.0001)  # Petita pausa per evitar la sobrecàrrega del processador

    except KeyboardInterrupt:
        print("Programa aturat pel teclat")
        GPIO.cleanup()

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

motor1 = MotorDC(ENA,IN1,IN2)

# Executa la funció
if __name__ == "__main__":
    read_encoder()
