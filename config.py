random_seed = 29
decimal_places = 4

def decimal_float(num):
    return round(num, decimal_places)

def decimal_float_str(num):
    return "{:.4f}".format(num)

def generate_decimal():
    if decimal_places < 0:
        return None
    return 10 ** -decimal_places