from machine import Pin, ADC, I2C, SPI, UART
import onewire, ds18x20, time, struct
from nrf24l01 import NRF24L01
import bh1750, veml6075, bme280
import adafruit_sgp30
import pms5003

# --- Pins ---
wind_pin = Pin(2, Pin.IN)        # Anemometer
rain_pin = Pin(3, Pin.IN)        # Tipping bucket
vane_adc  = ADC(Pin(26))         # Wind vane
soil_adc  = ADC(Pin(28))         # Soil moisture

# OneWire bus for DS18B20 probes
ow = onewire.OneWire(Pin(4))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()

# I2C: BME280, BH1750, VEML6075, SGP30
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
bme = bme280.BME280(i2c=i2c)
lux = bh1750.BH1750(i2c)
uv  = veml6075.VEML6075(i2c)
sgp = adafruit_sgp30.Adafruit_SGP30(i2c)
sgp.iaq_init()

# UART: PMS5003
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
pm   = pms5003.PMS5003(uart)

# SPI: nRF24L01
spi  = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn  = Pin(17, Pin.OUT)
ce   = Pin(20, Pin.OUT)
radio = NRF24L01(spi, csn, ce)
radio.set_payload_size(64)
radio.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')
radio.set_power_speed(NRF24L01.POWER_3, NRF24L01.SPEED_1M)

# Counters
wind_count = rain_count = 0
wind_pin.irq(trigger=Pin.IRQ_RISING, handler=lambda p: globals().__setitem__('wind_count', wind_count+1))
rain_pin.irq(trigger=Pin.IRQ_RISING, handler=lambda p: globals().__setitem__('rain_count', rain_count+1))

INTERVAL = 0.05  # 50 ms

while True:
    # Wind
    wc, wind_count = wind_count, 0
    wind_speed = wc * 2.4
    wind_dir   = vane_adc.read_u16() * (360/65535)

    # Rain
    rc, rain_count = rain_count, 0
    rain_mm = rc * 0.2794

    # BME280
    temp_bme, pressure, humidity = bme.read_compensated_data()

    # DS18B20
    ds.convert_temp(); time.sleep_ms(750)
    temps = [ds.read_temp(r) for r in roms]

    # Soil moisture
    soil_raw = soil_adc.read_u16()

    # Light & UV
    lux_val  = lux.luminance(bh1750.CONT_HIRES_1)
    uv_index = uv.read_index()

    # Air quality (SGP30)
    co2eq = sgp.eCO2
    tvoc  = sgp.TVOC

    # Particulates (PMS5003)
    pm_data = pm.read()

    # Pack data
    payload = struct.pack(
        '<H H f f f f f f f f f f f H',
        wc, rc,
        wind_speed, wind_dir, rain_mm,
        temp_bme, pressure, humidity,
        temps[0] if temps else 0, temps[1] if len(temps)>1 else 0,
        soil_raw,
        co2eq, tvoc,
        pm_data.pm25
    )
    radio.send(payload)
    time.sleep(INTERVAL)
