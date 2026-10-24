# XIAO ESP32C3 launcher. The ESP32-C3 heap can compile one large script
# per boot, so the chart itself is app.mpy (built from app.py).
import gc
import machine

# A Thonny/Ctrl-D soft reboot leaves this radio unable to accept connections,
# so the phone app cannot find the chart. One hardware reset clears that.
if machine.reset_cause() == machine.SOFT_RESET:
    machine.reset()

gc.collect()
import app
