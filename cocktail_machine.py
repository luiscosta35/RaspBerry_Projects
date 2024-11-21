import RPi.GPIO as GPIO
import time

# Configuració dels pins GPIO
CLK = 5  # Pin de l'entrada del Clock
DT = 6   # Pin de l'entrada de la Data
SW = 13   # Pin per al botó

# ENA = 22  # Pin Motor
# IN1 = 17  # Pin Motor
# IN2 = 27  # Pin Motor

# Configurar els pins GPIO
GPIO.setmode(GPIO.BCM)  # Utilitza la numeració BCM
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pin CLK com a entrada amb pull-up
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Pin DT com a entrada amb pull-up
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Pin SW per al botó

# GPIO.setup([ENA, IN1, IN2], GPIO.OUT)

# motor_pin = 22 # <<--  cuidado con esta mierda!! 
                 # posible conflito con la linea 9: ENA = 22   
# pwm = GPIO.PWM(motor_pin, 1000)  # 1000 Hz de freqüència
# pwm.start(0)  # Iniciem amb un duty cycle de 0% (motor apagat)

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
                    display.esborra_la_pantalla()
                    #display.envia_dades_al_display(display.char2bin('D'))
                    # if counter > 0: motor1.giro_derecha(0.001) 
                    display.escriu_frase("Hola, Raspberry Pi! Aquest és un exemple.")                    
                else:
                    counter -= 1  # Rotació a l'esquerra
                    display.envia_dades_al_display(display.char2bin('E'))
                    # if counter < 0: motor1.giro_izquierda(0.001)                   
                    
                if counter > 100:
                    print("                             No te pases, cabrón!")
                    counter = 100
                if counter < -100:
                    print("                             No te pases, cabrón!")
                    counter = -100
                    
                # if counter > 0: motor1.giro_der_pwm(0.0001, counter)
                # if counter < 0: motor1.giro_izq_pwm(0.0001, -1*counter)
                # if counter == 0: motor1.parate(0.0001)
                
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

class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7, pausa=0.02):
        # Configura els pins i pausa
        self.RS = rs
        self.E = e
        self.D4 = d4
        self.D5 = d5
        self.D6 = d6
        self.D7 = d7
        self.PAUSA = pausa
        
        # Configura els pins GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.RS, self.E, self.D4, self.D5, self.D6, self.D7], GPIO.OUT)
        GPIO.output([self.RS, self.E, self.D4, self.D5, self.D6, self.D7], 0)

    def char2bin(self, char):
        """Converteix un caràcter en una representació binària de 8 bits i la retorna com una tupla d'enters."""
        strink = bin(ord(char))[2:]
        strink = '0' * (8 - len(strink)) + strink  
        resultat = ''
        for bit in strink:
            resultat = bit + resultat  
        res = resultat[4:] + resultat[:4]
        tupla = tuple([int(element) for element in res])
        return tupla

    def modecomandament(self, valor):
        """Configura el mode de comandament del display, ajustant el pin RS segons si és instrucció o dada."""
        GPIO.output(self.RS, GPIO.HIGH if not valor else GPIO.LOW)
        GPIO.output(self.E, GPIO.LOW)

    def escriu_a_fila_u(self):
        """Mou el cursor a l'inici de la primera fila del display."""
        self.modecomandament(True)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(0, 0, 0, 0)

    def escriu_a_fila_dos(self):
        """Mou el cursor a l'inici de la segona fila del display."""
        self.modecomandament(True)
        self.escriu4bits(0, 0, 1, 1)
        self.escriu4bits(0, 0, 0, 0)

    def escriu4bits(self, b1, b2, b3, b4):
        """Envia 4 bits al display a través dels pins D4-D7."""
        GPIO.output(self.D4, b1)
        GPIO.output(self.D5, b2)
        GPIO.output(self.D6, b3)
        GPIO.output(self.D7, b4)
        time.sleep(self.PAUSA)
        GPIO.output(self.E, GPIO.HIGH)
        GPIO.output(self.E, GPIO.LOW)
        time.sleep(self.PAUSA)

    def esborra_la_pantalla(self):
        """Envia la instrucció per esborrar tot el display."""
        self.modecomandament(True)
        time.sleep(self.PAUSA)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 0, 0, 0)

    def envia_dades_al_display(self, dada):
        """Envia un caràcter (en forma de tupla de 8 bits) al display per a ser mostrat."""
        self.modecomandament(False)
        self.escriu4bits(dada[0], dada[1], dada[2], dada[3])
        self.escriu4bits(dada[4], dada[5], dada[6], dada[7])

    def detencio_pantalla(self):
        """Posa el display en mode de detenció o pausa."""
        self.modecomandament(True)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(0, 0, 1, 1)

    def inicia_pantalla(self):
        """Configura el display per iniciar-lo, establint-lo amb dues files i esborrant-lo."""
        self.modecomandament(True)
        for _ in range(3):
            self.escriu4bits(1, 1, 0, 0)
        for _ in range(2):
            self.escriu4bits(0, 1, 0, 0)
        self.escriu4bits(1, 0, 1, 1)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 1, 1, 1)
        self.esborra_la_pantalla()

    def cleanup(self):
        """Neteja la configuració de GPIO."""
        GPIO.cleanup()
        
    def escriu_frase(self, frase):
        """
        Escriu una frase completa al LCD.
        Divideix la frase en dues línies si és més llarga que l'amplada del LCD (16 caràcters).
        """
        self.esborra_la_pantalla()

        linea_1 = frase[:16]
        linea_2 = frase[16:32]

        self.escriu_a_fila_u()
        for char in linea_1:
            self.envia_dades_al_display(self.char2bin(char))

        if linea_2.strip():
            self.escriu_a_fila_dos()
            for char in linea_2:
                self.envia_dades_al_display(self.char2bin(char))
        
# motor1 = MotorDC(ENA,IN1,IN2)
display = LCD(rs=4, e=18, d4=27, d5=22, d6=23, d7=24, pausa=0.02)

display.inicia_pantalla()
display.escriu_a_fila_u()
                    
                    
# Executa la funció
if __name__ == "__main__":
    display.escriu_frase("Elige tu bebida")
    read_encoder()
 
