import random
from apostador_json import apostar_en_json

def apostar_random():
    numero = random.randint(0, 36)
    apostar_en_json(numero)
