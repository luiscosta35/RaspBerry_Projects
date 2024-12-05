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

# Clase MotorDC para controlar las bombas
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
 
    def cleanup(self):
        """Detura el PWM i neteja la configuració GPIO del motor."""
        self.pwm.stop()
        del self.pwm  # Elimina l'objecte PWM per evitar errors en el destructor
        GPIO.output([self.ENA, self.IN1, self.IN2], GPIO.LOW)

# Configuración de bombas 
bombas = {
    "Rum": MotorDC(16, 20, 21),  # Pines GPIO para la bomba de "Rum"
    "Coke": MotorDC(12, 19, 26),  # Pines GPIO para la bomba de "Coke"
    "Orange Juice": MotorDC(25, 17, 21),  # Pines GPIO para la bomba de "Orange Juice"
    
}

# Configuración de recetas
drink_recipes = [
    {"name": "Rum & Coke", "ingredients": {"Rum": 50, "Coke": 150}},
    {"name": "Gin & Tonic", "ingredients": {"Gin": 50, "Tonic": 150}},  # Ejemplo simplificado para usar "Rum"
    {"name": "Screwdriver", "ingredients": {"Vodka": 50, "Orange Juice": 150}},
    {"name": "Long Island", "ingredients": {"Gin": 15, "Rum": 15, "Vodka": 15, "Tequila": 15, "Coke": 100, "Orange Juice": 15}},
    {"name": "Margarita", "ingredients": {"Tequila": 50, "mmix": 150}},
    {"name": "Gin & Juice", "ingredients": {"Gin": 50, "Orange Juice": 150}},
    {"name": "Tequila Sunrise", "ingredients": {"Tequila": 50, "Orange Juice": 150}},
]


            
# Función para calcular tiempo de dispensación
def calcular_tiempo(ml, flujo=20):
    return ml / flujo
    

# Función para activar las bombas y preparar la bebida
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


def cleanup_tot():
    """Atura motors, neteja LCD i GPIO."""
    for motor in bombas.values():
        motor.detener()
        motor.cleanup()  # Atura i neteja cada motor
    lcd.esborra_la_pantalla()
    lcd.detencio_pantalla()
    time.sleep(1)  # Esperar un poco para asegurarnos de que el LCD se limpia correctamente
    #lcd.cleanup()  # Neteja el LCD
    #GPIO.cleanup()  # Neteja els GPIO
    
    

def iniciar_lcd():
    """Inicialitza el LCD de manera segura per evitar errors de display."""
    lcd = LCD(RS, E, D4, D5, D6, D7)
    lcd.inicia_pantalla()  # Inicialitza el display a un estat net i configurat
    return lcd

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
        cleanup_tot()  # Llamamos a la función de limpieza para detener todo y limpiar el LCD

# Ejecución del programa
if __name__ == "__main__":
    lcd = iniciar_lcd()  # Usamos la función de inicialización limpia
    lcd.escriu_frase("Elige tu bebida")
    navigate_menu()


