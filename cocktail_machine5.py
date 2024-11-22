import RPi.GPIO as GPIO
import time

# Configuración de pines para encoder y LCD
CLK = 5
DT = 6
SW = 13

# Configuración de pines para el LCD
RS = 4
E = 18
D4 = 27
D5 = 22
D6 = 23
D7 = 24

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Clase LCD (manteniendo la original)
class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7, pausa=0.02):
        self.RS = rs
        self.E = e
        self.D4 = d4
        self.D5 = d5
        self.D6 = d6
        self.D7 = d7
        self.PAUSA = pausa
        GPIO.setup([rs, e, d4, d5, d6, d7], GPIO.OUT)
        GPIO.output([rs, e, d4, d5, d6, d7], 0)

    def char2bin(self, char):
        bits = bin(ord(char))[2:].zfill(8)
        return tuple(map(int, bits))

    def escriu4bits(self, b1, b2, b3, b4):
        GPIO.output(self.D4, b1)
        GPIO.output(self.D5, b2)
        GPIO.output(self.D6, b3)
        GPIO.output(self.D7, b4)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(self.PAUSA)
        GPIO.output(self.E, GPIO.LOW)

    def esborra_la_pantalla(self):
        GPIO.output(self.RS, GPIO.LOW)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 0, 0, 0)

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

    def escriu_frase(self, frase):
        """
        Escribe una frase completa en el LCD.
        Divide la frase en dos líneas si es más larga que 16 caracteres.
        """
        self.esborra_la_pantalla()

        linea_1 = frase[:16]
        linea_2 = frase[16:32]

        # Escribe la primera línea
        self.escriu_a_fila_u()
        for char in linea_1:
            bits = self.char2bin(char)
            self.escriu4bits(bits[0], bits[1], bits[2], bits[3])  # Primeros 4 bits
            self.escriu4bits(bits[4], bits[5], bits[6], bits[7])  # Últimos 4 bits

        # Escribe la segunda línea, si existe texto adicional
        if linea_2.strip():
            self.escriu_a_fila_dos()
            for char in linea_2:
                bits = self.char2bin(char)
                self.escriu4bits(bits[0], bits[1], bits[2], bits[3])  # Primeros 4 bits
                self.escriu4bits(bits[4], bits[5], bits[6], bits[7])  # Últimos 4 bits

# Clase MotorDC
class MotorDC:
    def __init__(self, ena, in1, in2):
        self.ENA = ena
        self.IN1 = in1
        self.IN2 = in2

        GPIO.setup([self.ENA, self.IN1, self.IN2], GPIO.OUT)
        self.pwm = GPIO.PWM(self.ENA, 100)  # Frecuencia de 100 Hz
        self.pwm.start(0)

    def dispensar(self, tiempo, dutycycle=100):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(dutycycle)
        time.sleep(tiempo)
        self.pwm.ChangeDutyCycle(0)

    def detener(self):
        self.pwm.ChangeDutyCycle(0)

# Configuración de bombas (limitado por pines disponibles)
bombas = {
    "Rum": MotorDC(17, 27, 22),
    "Coke": MotorDC(10, 9, 11),
    "Gin": MotorDC(25, 24, 23)
}

# Configuración de recetas
drink_recipes = [
    {"name": "Rum & Coke", "ingredients": {"Rum": 50, "Coke": 150}},
    {"name": "Gin & Tonic", "ingredients": {"Gin": 50, "Tonic Water": 150}},
]

# Función para calcular tiempo de dispensación
def calcular_tiempo(ml, flujo=100):
    return ml / flujo

# Función para dispensar bebida
def preparar_bebida(lcd, bebida):
    lcd.escriu_frase(f"Preparando {bebida['name']}")
    for ingrediente, cantidad in bebida["ingredients"].items():
        if ingrediente in bombas:
            tiempo = calcular_tiempo(cantidad)
            lcd.escriu_frase(f"{ingrediente}: {cantidad}ml")
            bombas[ingrediente].dispensar(tiempo)
        else:
            lcd.escriu_frase(f"{ingrediente}: No disponible")
        time.sleep(2)  # Pausa entre ingredientes
    lcd.escriu_frase(f"{bebida['name']} lista!")

# Navegación del menú
def navigate_menu():
    clk_last_state = GPIO.input(CLK)
    position = 0

    try:
        while True:
            clk_state = GPIO.input(CLK)
            if clk_state != clk_last_state:
                if GPIO.input(DT) != clk_state:
                    position = (position + 1) % len(drink_recipes)
                else:
                    position = (position - 1) % len(drink_recipes)
                lcd.escriu_frase(drink_recipes[position]["name"])
            clk_last_state = clk_state

            if GPIO.input(SW) == GPIO.LOW:
                bebida = drink_recipes[position]
                preparar_bebida(lcd, bebida)
                break  # Salimos después de preparar
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programa interrumpido.")
    finally:
        GPIO.cleanup()

# Ejecución del programa
if __name__ == "__main__":
    lcd = LCD(RS, E, D4, D5, D6, D7)
    lcd.esborra_la_pantalla()
    lcd.escriu_frase("Elige tu bebida")
    navigate_menu()
