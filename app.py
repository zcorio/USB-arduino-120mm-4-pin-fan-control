from flask import Flask, render_template, request
import serial
import logging
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD = 9600
LAST_SPEED_FILE = "last_speed.txt"

logging.basicConfig(level=logging.INFO)

class SerialManager:
    def __init__(self, port, baud, timeout=1, retries=3, retry_delay=0.5):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.ser = None

    def connect(self):
        if self.ser and getattr(self.ser, 'is_open', False):
            return
        try:
            logging.info('Opening serial port %s @ %d', self.port, self.baud)
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
            # Give Arduino time to reset and boot after the serial port opens.
            # Many Arduino boards toggle DTR on open which resets the MCU; wait
            # a short time and clear any startup noise so commands aren't lost.
            time.sleep(2)
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception:
                pass
        except Exception:
            logging.exception('Failed to open serial port %s', self.port)
            self.ser = None

    def write(self, data):
        for attempt in range(1, self.retries + 1):
            try:
                if not self.ser or not getattr(self.ser, 'is_open', False):
                    self.connect()
                if not self.ser:
                    raise serial.SerialException('serial not available')
                self.ser.write(data)
                try:
                    self.ser.flush()
                except Exception:
                    pass
                return True
            except Exception:
                logging.exception('Serial write failed (attempt %d/%d)', attempt, self.retries)
                try:
                    if self.ser:
                        self.ser.close()
                except Exception:
                    pass
                self.ser = None
                if attempt < self.retries:
                    time.sleep(self.retry_delay)
        return False

    def close(self):
        try:
            if self.ser and getattr(self.ser, 'is_open', False):
                self.ser.close()
        except Exception:
            logging.exception('Error closing serial')
        finally:
            self.ser = None


serial_mgr = SerialManager(SERIAL_PORT, BAUD)

app = Flask(__name__)

def set_fan(percent):
    percent = max(0, min(100, int(percent)))
    data = f"fan {percent}\n".encode()
    ok = serial_mgr.write(data)
    if not ok:
        logging.error('Failed to send fan command after retries: %s', data)
    else:
        try:
            with open(LAST_SPEED_FILE, 'w') as f:
                f.write(str(percent))
        except Exception:
            logging.exception('Failed to persist last speed')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        speed = request.form.get("speed")
        set_fan(speed)
    # Read persisted last speed (if any) and pass to the template.
    last = None
    try:
        with open(LAST_SPEED_FILE, 'r') as f:
            v = f.read().strip()
            if v:
                last = int(v)
    except FileNotFoundError:
        last = None
    except Exception:
        logging.exception('Failed to read last speed')
    return render_template("index.html", last_speed=last)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
