import os

certs_dir = "/app/certs"

bind = "0.0.0.0:8000"
workers = 4

# command_no_cert = "gunicorn -w 4 -b 0.0.0.0:8000 server:app"
# command_certs = "gunicorn -w 4 -b 0.0.0.0:8000 --certfile=%s --keyfile=%s server:app"

items = os.listdir(certs_dir)
if "chain1.pem"in items and "privkey1.pem" in items:
    print("using certs")
    certfile = os.path.join(certs_dir, "fullchain1.pem")
    keyfile = os.path.join(certs_dir, "privkey1.pem")


