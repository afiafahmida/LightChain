from Crypto.PublicKey import ECC

# Generate ECC key pair
key = ECC.generate(curve='P-256')

# Save private key (for ESP32 firmware)
with open("esp32_priv.pem", "wt") as f:
    f.write(key.export_key(format='PEM'))

# Save public key (for Raspberry Pi to verify)
with open("esp32_pub.pem", "wt") as f:
    f.write(key.public_key().export_key(format='PEM'))
