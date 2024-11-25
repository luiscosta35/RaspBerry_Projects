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

# Clase LCD
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
        time.sleep(self.PAUSA)

    def esborra_la_pantalla(self):
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 0, 0, 0)

    def envia_dades_al_display(self, dada):
        self.escriu4bits(dada[0], dada[1], dada[2], dada[3])
        self.escriu4bits(dada[4], dada[5], dada[6], dada[7])

    def escriu_frase(self, frase):
        self.esborra_la_pantalla()
        linea_1 = frase[:16]
        linea_2 = frase[16:32]
        for char in linea_1:
            self.envia_dades_al_display(self.char2bin(char))
        if linea_2.strip():
            for char in linea_2:
                self.envia_dades_al_display(self.char2bin(char))

    def inicia_pantalla(self):
        for _ in range(3):
            self.escriu4bits(1, 1, 0, 0)
        time.sleep(0.05)  # Pausa para estabilizar
        self.escriu4bits(0, 1, 0, 0)
        self.escriu4bits(1, 0, 1, 1)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 1, 1, 1)
        time.sleep(0.1)  # Pausa adicional para evitar caracteres erráticos
        self.esborra_la_pantalla()

    def cleanup(self):
        GPIO.cleanup()

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
        self.pwm.stop()

# Configuración de bombas
bombas = {
    "Rum": MotorDC(16, 20, 21),
    "Coke": MotorDC(12, 19, 26),
}

# Configuración de recetas
drink_recipes = [
    {"name": "Rum & Coke", "ingredients": {"Rum": 50, "Coke": 150}},
    {"name": "Gin & Tonic", "ingredients": {"Rum": 50}},  # Simplificado
]

# Función para calcular tiempo de dispensación
def calcular_tiempo(ml, flujo=100):
    return ml / flujo

# Función para activar las bombas
def preparar_bebida(lcd, bebida):
    lcd.escriu_frase(f"Preparando {bebida['name']}")
    for ingrediente, cantidad in bebida["ingredients"].items():
        if ingrediente in bombas:
            tiempo = calcular_tiempo(cantidad)
            lcd.escriu_frase(f"{ingrediente}: {cantidad}ml")
            bombas[ingrediente].dispensar(tiempo)
        else:
            lcd.escriu_frase(f"{ingrediente}: No disponible")
        time.sleep(2)
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
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Programa interrumpido.")
    finally:
        for bomba in bombas.values():
            bomba.detener()
        GPIO.cleanup()

# Ejecución principal
if __name__ == "__main__":
    try:
        lcd = LCD(RS, E, D4, D5, D6, D7)
        lcd.inicia_pantalla()
        lcd.escriu_frase("Elige tu bebida")
        navigate_menu()
    except KeyboardInterrupt:
        print("Programa detenido por el usuario.")
    finally:
        GPIO.cleanup()
