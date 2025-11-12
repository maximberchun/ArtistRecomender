import bcrypt
pw = "contraseña".encode()
print(bcrypt.hashpw(pw, bcrypt.gensalt()).decode())
