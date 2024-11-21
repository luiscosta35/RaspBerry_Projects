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

# Configuración de menú de bebidas
drink_list = [
    "Rum & Coke",
    "Gin & Tonic",
    "Long Island",
    "Screwdriver",
    "Margarita",
    "Gin & Juice",
    "Tequila Sunrise"
]

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Clase LCD 
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

# Función de navegación por menú
def navigate_menu():
    clk_last_state = GPIO.input(CLK)
    position = 0

    try:
        while True:
            clk_state = GPIO.input(CLK)
            if clk_state != clk_last_state:
                if GPIO.input(DT) != clk_state:
                    position = (position + 1) % len(drink_list)
                else:
                    position = (position - 1) % len(drink_list)
                lcd.escriu_frase(drink_list[position])
            
            clk_last_state = clk_state

            if GPIO.input(SW) == GPIO.LOW:
                print(f"Bebida seleccionada: {drink_list[position]}")
                lcd.escriu_frase(f"Seleccion: {drink_list[position]}")
                time.sleep(1)
                break  # Salimos del menú tras seleccionar
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programa interrumpido.")
    finally:
        GPIO.cleanup()

# Ejecución del programa
if __name__ == "__main__":
    # Inicialización del LCD
    lcd = LCD(RS, E, D4, D5, D6, D7)
    lcd.inicia_pantalla()
    #lcd.esborra_la_pantalla()

    lcd.escriu_frase("Elige tu bebida")
    navigate_menu()
