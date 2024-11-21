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

# Configuración de menú de bebidas con recetas
drink_recipes = [
    {"name": "Rum & Coke", "ingredients": {"Rum": 50, "Coke": 150}},
    {"name": "Gin & Tonic", "ingredients": {"Gin": 50, "Tonic Water": 150}},
    {"name": "Long Island", "ingredients": {"Gin": 15, "Rum": 15, "Vodka": 15, "Tequila": 15, "Coke": 100, "Orange Juice": 30}},
    {"name": "Screwdriver", "ingredients": {"Vodka": 50, "Orange Juice": 150}},
    {"name": "Margarita", "ingredients": {"Tequila": 50, "Margarita Mix": 150}},
    {"name": "Gin & Juice", "ingredients": {"Gin": 50, "Orange Juice": 150}},
    {"name": "Tequila Sunrise", "ingredients": {"Tequila": 50, "Orange Juice": 150}}
]

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Clase LCD (similar a tu original)
class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7, pausa=0.02):
        self.RS = rs
        self.E = e
        self.D4 = d4
        self.D5 = d5
        self.D6 = d6
        self.D7 = d7
        self.PAUSA = pausa
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([rs, e, d4, d5, d6, d7], GPIO.OUT)
        GPIO.output([rs, e, d4, d5, d6, d7], 0)
    
    def char2bin(self, char):
        bits = bin(ord(char))[2:].zfill(8)
        return tuple(map(int, bits))
        
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
        GPIO.output(self.D4, b1)
        GPIO.output(self.D5, b2)
        GPIO.output(self.D6, b3)
        GPIO.output(self.D7, b4)
        GPIO.output(self.E, GPIO.HIGH)
        time.sleep(self.PAUSA)
        GPIO.output(self.E, GPIO.LOW)
    
    def envia_dades_al_display(self, dada):
        self.escriu4bits(dada[0], dada[1], dada[2], dada[3])
        self.escriu4bits(dada[4], dada[5], dada[6], dada[7])

    def escriu_frase(self, frase):
        self.esborra_la_pantalla()
        for i, char in enumerate(frase[:16]):
            self.envia_dades_al_display(self.char2bin(char))
        if len(frase) > 16:
            self.escriu_a_fila_dos()
            for char in frase[16:32]:
                self.envia_dades_al_display(self.char2bin(char))
    
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
        
    def esborra_la_pantalla(self):
        GPIO.output(self.RS, GPIO.LOW)
        self.escriu4bits(0, 0, 0, 0)
        self.escriu4bits(1, 0, 0, 0)



# Función para mostrar receta en el LCD
def mostrar_receta(lcd, receta):
    lcd.esborra_la_pantalla()
    for ingrediente, cantidad in receta.items():
        mensaje = f"{ingrediente}: {cantidad}ml"
        lcd.escriu_frase(mensaje)
        time.sleep(2)  # Mostrar cada ingrediente durante 2 segundos

# Función de navegación por menú
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
                print(f"Bebida seleccionada: {bebida['name']}")
                lcd.escriu_frase(f"Preparando {bebida['name']}")
                time.sleep(1)
                mostrar_receta(lcd, bebida["ingredients"])
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
    lcd.escriu_frase("Elige tu bebida")
    navigate_menu()
