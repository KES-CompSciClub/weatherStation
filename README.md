# School Weather Station

This project implements a real-time weather station using a Raspberry Pi Pico (RP2040) running MicroPython. Data from various environmental sensors are collected, packed into a binary payload, and transmitted over an nRF24L01 wireless link at ~50 ms intervals.

## Sensors & Interfaces

- **Anemometer (Wind Speed)**: Reed switch on GPIO pin counts rotations (GP2).
- **Wind Vane (Direction)**: Analog voltage read via ADC0 (GP26).
- **Tipping-Bucket Rain Gauge**: Reed switch pulses counted on GPIO pin (GP3).
- **BME280**: I²C sensor for temperature, pressure, and humidity (I2C0 SDA=GP0, SCL=GP1).
- **DS18B20**: OneWire temperature probes (air & soil) on GP4; supports multiple devices.
- **BH1750**: I²C ambient lux sensor (I2C0 SDA=GP0, SCL=GP1).
- **VEML6075**: I²C UVA/UVB sensor for UV index (I2C0 SDA=GP0, SCL=GP1).
- **SGP30**: I²C gas sensor for eCO₂ and TVOC (I2C0 SDA=GP0, SCL=GP1).
- **PMS5003**: UART particulate matter sensor for PM1.0, PM2.5, PM10 (UART1 TX=GP8, RX=GP9).
- **Soil Moisture**: Capacitive sensor on ADC2 (GP28) for relative moisture levels.

## Optional Sensor Suggestions

- **SGP30**: Indoor air quality (CO₂ eq, TVOC).
- **Soil Temperature**: Additional DS18B20 in soil.
- **Particulate Matter (PMS5003)**: Already included.
- **Gas Sensors (e.g., SGP30)**: Included.
- **Soil Moisture**: Included.
- **Optional**: Soil pH sensor, barometric wind gust detector, rain pH sensor, microphone for environmental noise level.

## Pinout

| Sensor / Interface         | Function                       | GPIO Pin | Physical Pin |
|----------------------------|--------------------------------|----------|--------------|
| Anemometer (reed)          | Wind speed pulses              | GP2      | 4            |
| Rain gauge (reed)          | Rain tip pulses                | GP3      | 5            |
| DS18B20 OneWire bus        | Air & soil temperature         | GP4      | 6            |
| I²C SDA (BME280, BH1750,
VEML6075, SGP30)             | I²C data                       | GP0      | 1            |
| I²C SCL (BME280, BH1750,
VEML6075, SGP30)             | I²C clock                      | GP1      | 2            |
| Wind Vane (ADC0)           | Analog voltage (0–3.3 V)       | GP26     | 31           |
| Soil Moisture (ADC2)       | Analog voltage (0–3.3 V)       | GP28     | 34           |
| UART1 TX (PMS5003)         | Serial data output             | GP8      | 11           |
| UART1 RX (PMS5003)         | Serial data input              | GP9      | 12           |
| SPI SCK (nRF24L01)         | SPI clock                      | GP18     | 24           |
| SPI MOSI (nRF24L01)        | SPI data out                   | GP19     | 25           |
| SPI MISO (nRF24L01)        | SPI data in                    | GP16     | 21           |
| nRF24L01 CSN               | SPI chip select                | GP17     | 22           |
| nRF24L01 CE                | Radio enable                   | GP20     | 26           |
| 3V3 Power                  | +3.3 V supply                  | —        | 36, 40       |
| GND                        | Ground                         | —        | 38, etc.     |

## Software Requirements

- **MicroPython:** RP2 build for Raspberry Pi Pico.
- **Libraries (copy to `lib/` on the Pico):**
  - `bme280.py`
  - `bh1750.py`
  - `veml6075.py`
  - `adafruit_sgp30.mpy` (and dependencies)
  - `ds18x20.py` + `onewire.py`
  - `pms5003.py`
  - `nrf24l01.py`
  - `pms5003.py`

## Installation

1. Flash MicroPython to the Pico via `picotool` or Thonny.
2. Mount the Pico’s storage and copy the `main.py` script and the `lib/` folder.
3. Wire sensors and radio as per the pinout table.

## Usage

1. Power on the Pico.
2. The script `main.py` runs automatically, collecting sensor data every 50 ms.
3. Data packets are transmitted via nRF24L01; configure the receiver’s pipe to `0xF0F0F0E1`.

## Calibration & Tuning

- **Anemometer factor:** Adjust `wind_speed = count * 2.4` to match your cup size.
- **Rain gauge tip volume:** Update `rain_mm = tips * 0.2794` as per gauge spec.
- **ADC sensors:** Map raw 0–65535 to physical units in your dashboard.

