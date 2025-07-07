import string
import random
import hashlib

# Constants
ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
ALPHABET_LENGTH = len(ALPHABET)

def split_password(password, parts=4):
    k, m = divmod(len(password), parts)
    return [password[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(parts)]

def string_to_seed(s):
    hashed = hashlib.sha256(s.encode()).hexdigest()
    return int(hashed[:16], 16)

def generate_rotor_from_seed(seed):
    chars = list(ALPHABET)
    random.seed(seed)
    random.shuffle(chars)
    return ''.join(chars)

def generate_reflector_from_seed(seed):
    chars = list(ALPHABET)
    random.seed(seed)
    random.shuffle(chars)
    reflector = [''] * ALPHABET_LENGTH
    for i in range(0, ALPHABET_LENGTH, 2):
        a = chars[i]
        b = chars[i + 1]
        idx_a = ALPHABET.index(a)
        idx_b = ALPHABET.index(b)
        reflector[idx_a] = b
        reflector[idx_b] = a
    return ''.join(reflector)

def letter_to_index(letter):
    return ALPHABET.index(letter)

def rotor_forward(letter, rotor, position):
    shifted_index = (letter_to_index(letter) + position) % ALPHABET_LENGTH
    return rotor[shifted_index]

def rotor_backward(letter, rotor, position):
    index_in_rotor = (rotor.index(letter) - position) % ALPHABET_LENGTH
    return ALPHABET[index_in_rotor]

def enigma(text, rotor_a, rotor_b, rotor_c, reflector, pos_a=0, pos_b=0, pos_c=0):
    output = ""
    for char in text:
        if char not in ALPHABET:
            output += char
            continue

        pos_a = (pos_a + 1) % ALPHABET_LENGTH
        if pos_a == 0:
            pos_b = (pos_b + 1) % ALPHABET_LENGTH
        if pos_b == 0 and pos_a == 0:
            pos_c = (pos_c + 1) % ALPHABET_LENGTH

        step1 = rotor_forward(char, rotor_a, pos_a)
        step2 = rotor_forward(step1, rotor_b, pos_b)
        step3 = rotor_forward(step2, rotor_c, pos_c)

        reflected = reflector[letter_to_index(step3)]

        step4 = rotor_backward(reflected, rotor_c, pos_c)
        step5 = rotor_backward(step4, rotor_b, pos_b)
        step6 = rotor_backward(step5, rotor_a, pos_a)

        output += step6
    return output

def initialize_machine_from_password(password):
    parts = split_password(password, 4)
    seeds = [string_to_seed(part) for part in parts]
    rotor_a = generate_rotor_from_seed(seeds[0])
    rotor_b = generate_rotor_from_seed(seeds[1])
    rotor_c = generate_rotor_from_seed(seeds[2])
    reflector = generate_reflector_from_seed(seeds[3])
    return rotor_a, rotor_b, rotor_c, reflector
