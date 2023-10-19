# script packaged into a single setup.exe file
import os

def install(package):
	os.system(f"python -m pip install {package}")

if __name__ == "__main__":
	install("gorilla-cli")