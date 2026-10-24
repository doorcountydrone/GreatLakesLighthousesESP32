# Great Lakes Lighthouses

**13 lighthouses** from Kewaunee through Rock Island on a **Seeed Studio XIAO ESP32C3** NeoPixel strip, with an SSD1306 OLED and an 8×32 LED matrix. Each strip LED uses that light’s **real color and flash characteristic** (USCG Light List / historic pattern), not weather colors.

The Android app has a **Great Lakes catalog** (named lighthouses, pier lights, and US/Canadian lighted buoys on all five lakes, with color and flash already filled in). Search or tap the Chart to add the ones on *your* strip, then **Save to chart**. Restore defaults still loads the Kewaunee → Rock Island pack. The app and the map’s web page both have a **Help** tab. The Chart tab can show Google Maps or a NOAA ENC (not for navigation).

## Light characteristics

Wired **south to north**. Timing is the official (or last historic) rhythm:

| LED | Lighthouse | Characteristic | Meaning |
|-----|------------|----------------|---------|
| 0 | Kewaunee Pierhead | **F W** | Steady white |
| 1 | Algoma Pierhead | **Iso R 6s** | Red 3s on, 3s off |
| 2 | Sturgeon Bay Ship Canal Light | **Fl R 10s** | Red flash 1s, dark 9s |
| 3 | Sturgeon Bay North Pierhead | **Fl R 2.5s** | Red flash 0.5s, dark 2s |
| 4 | Sherwood Point | **Iso W 6s** | White 3s on, 3s off |
| 5 | Eagle Bluff | **Fl W 6s** | White flash 1s, dark 5s |
| 6 | Chambers Island | **Fl W 6s** | Current skeletal ATON (brick tower dark since 1961) |
| 7 | Baileys Harbor Range | **F R** | Fixed red front light (rear is fixed white) |
| 8 | Old Baileys Harbor (Birdcage) | **F W** | Historic fixed white; inactive since 1869 |
| 9 | Cana Island | **F W** | Fixed white |
| 10 | Plum Island Range | **F R** | Fixed red (front and rear) |
| 11 | Pilot Island | **Fl(2) W 6s** | White: on 1, off 1, on 1, off 3 |
| 12 | Pottawatomie (Rock Island) | **Fl W 4s** | White flash 0.5s, dark 3.5s (current ATON) |

Edit `pico/lighthouses.json` (`light.on_s` / `light.off_s`) if you want a different published timing.

## Hardware

See `pico/WIRING.txt`.

- Seeed Studio XIAO ESP32C3
- WS2812 / NeoPixel strip (13 LEDs or longer) on **D8 / GPIO 8**, common **GND**, 5 V sized for the strip
- SSD1306 OLED on **D4 / GPIO 6** (SDA) and **D5 / GPIO 7** (SCL), powered from the board **3.3 V** pin
- 8×32 WS2812 matrix data on **D3 / GPIO 5**, 5 V and common GND
- Optional: hold **D1 / GPIO 3** to GND for 3 seconds at boot to force setup Wi-Fi
- Light sensor: **D6 / GPIO 21** held at 3.3 V, LDR to **D2 / GPIO 4**, then 10k to GND

Do not use D9, or any GPIO from 12 through 19. Those are strap, flash, or USB pins. D8 is the strip data line; leave it low while the board resets.

## Flash the XIAO ESP32C3

1. Install [MicroPython for ESP32-C3](https://micropython.org/download/ESP32_GENERIC_C3/) (4 MB flash). Hold **BOOT**, tap **RESET**, release **BOOT**, then install with Thonny or esptool.
2. Copy these files to the board root with Thonny or mpremote. The large modules are precompiled (`.mpy`) because the ESP32-C3 cannot compile `app.py` and `wifi_manager.py` in the same boot. `main.py` only imports `app`:
   - `pico/boot.py`
   - `pico/main.py`
   - `pico/app.mpy`
   - `pico/wifi_manager.mpy`
   - `pico/netreq.mpy`
   - `pico/updater.mpy`
   - `pico/led_matrix.mpy`
   - `pico/ssd1306.mpy`
   - `pico/sans18.mpy`
   - `pico/sans20.mpy`
   - `pico/writer.mpy`
   - `pico/lighthouses.json`
   - `pico/lighthouses_defaults.json`
   - `pico/catalog.json`
   - `pico/help.html`
   Rebuild the `.mpy` files from the matching `.py` sources with `mpy-cross -march=rv32imc -msmall-int-bits=31` after editing them. Do not also copy those `.py` files onto the board.
3. Power the board. On first boot it opens **GreatLakes-Setup** (password `door1234`). The OLED shows the firmware version while setup is running.
4. Join that network on your phone and open **http://192.168.4.1**.
5. Enter home Wi-Fi, LED count, brightness, time zone (Central or Eastern; daylight saving is automatic), then **Save & Reboot**. Leave **Extra display** on **OLED and LED matrix**.
6. After reboot the strip chases south→north in each light’s color, then runs the real flash patterns. The matrix and OLED scroll the same light and weather text.

On the home LAN (and in setup AP mode) the chart serves:

- `http://<board-ip>/status`
- `GET/POST http://<board-ip>/lighthouses` — app fetch/save of the editable list

In the app: set **Chart address** to `192.168.4.1` on GreatLakes-Setup, or the chart’s LAN IP on home Wi-Fi. **Restore defaults** reloads the bundled Kewaunee → Rock Island set.

Firmware updates come from [GreatLakesLighthousesESP32](https://github.com/doorcountydrone/GreatLakesLighthousesESP32). Pico boards stay on GreatLakesLighthouses. This board ignores a manifest that is not tagged `xiao-esp32c3`.

If you add more lights than the strip has chips, extra LEDs will not show until you wire them and set LED count.
