import socket
import platform
import time

print("[+] Demo malware started")
print("[+] Host:", socket.gethostname())
print("[+] OS:", platform.platform())

for i in range(5):
    print(f"[*] Simulating malicious action {i + 1}/5")
    time.sleep(1)

print("[+] Demo finished")
input("Press Enter to exit...")