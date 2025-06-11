import subprocess
import time
import sys

if len(sys.argv) < 2:
    print("Uso: python main.py seu@email.com")
    sys.exit(1)

email = sys.argv[1]


p1 = subprocess.Popen(["python3.8", "requisicao.py", email])
print("requisição.py iniciado.")


time.sleep(3)


p2 = subprocess.Popen(["python3.8", "modelo.py", email])
print("modelo.py iniciado.")


p1.wait()
p2.wait()
