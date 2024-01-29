import os

certs_dir = "/app/certs"

bind = "0.0.0.0:8000"
workers = 4

items = os.listdir(certs_dir)
if "chain1.pem"in items and "privkey1.pem" in items:
    print("using certs")
    certfile = os.path.join(certs_dir, "fullchain1.pem")
    keyfile = os.path.join(certs_dir, "privkey1.pem")


