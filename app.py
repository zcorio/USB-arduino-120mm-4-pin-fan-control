from flask import Flask, render_template, request
import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUD = 9600

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

app = Flask(__name__)

def set_fan(percent):
    percent = max(0, min(100, int(percent)))
    ser.write(f"fan {percent}\n".encode())

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        speed = request.form.get("speed")
        set_fan(speed)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
