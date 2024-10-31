import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from serial import Serial, SerialException
from serial.tools.list_ports import comports

from threading import Thread, Lock # we'll use Lock later ;)
def detached_callback(f):
    return lambda *args, **kwargs: Thread(target=f, args=args, kwargs=kwargs).start()


S_OK: int = 0xaa
S_ERR: int = 0xff

class LockedSerial(Serial):
    _lock: Lock = Lock()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def read(self, size=1) -> bytes:
        with self._lock:
            return super().read(size)
    def write(self, b: bytes, /) -> int | None:
        with self._lock:
            super().write(b)
    def close(self):
        with self._lock:
            super().close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("LED Blinker")
        self.led = tk.BooleanVar()
        self.port = tk.StringVar() # add this

        ttk.Checkbutton(self, text='Toggle LED', variable=self.led, command=self.update_led).pack()
        ttk.Button(self, text='Send Invalid', command=self.send_invalid).pack()
        ttk.Button(self, text='Disconnect',command=self.disconnect, default='active').pack()
        SerialPortal(self) # and this
    
    def connect(self):
        self.ser = LockedSerial(self.port.get())

    def disconnect(self):
        self.ser.close()
        SerialPortal(self) # display portal to reconnect

    def write(self, b: bytes):
        try:
            self.ser.write(b)
            if int.from_bytes(self.ser.read(), 'big') == S_ERR:
                showerror('Device Error', 'The device reported an invalid command.')
        except SerialException:
            showerror('Serial Error', 'Write failed.')

    @detached_callback
    def update_led(self):
        self.write(bytes([self.led.get()]))
    def send_invalid(self):
        self.write(bytes([0x10]))

    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.disconnect()





class SerialPortal(tk.Toplevel):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.parent = parent
        self.parent.withdraw() # hide App until connected
        ttk.OptionMenu(self, parent.port, '', *[d.device for d in comports()]).pack()
        ttk.Button(self, text='Connect', command=self.connect, default='active').pack()
    def connect(self):
        self.parent.connect()
        self.destroy()
        self.parent.deiconify() # reveal App


    
if __name__ == '__main__':
    with App() as app:
        app.mainloop()
