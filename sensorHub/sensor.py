#!/usr/bin/python

import Adafruit_DHT;
import time;
from dataCollector import DataCollector

dataCollector = DataCollector()

dataCollector.saveSensorData(dataCollector.cpuTempSensorId, dataCollector.getCpuTemp());
# sendSensorData(cpuTempSensorId, cpuTemp)
# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO23.
pin = 25

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)


# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).  
# If this happens try again!
if humidity is not None and temperature is not None:
    print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
    dataCollector.saveSensorData(dataCollector.tempSensorId, temperature)
    dataCollector.saveSensorData(dataCollector.humiditySensorId, humidity)
else:
    print "time not match"

minute = int(time.strftime("%M")) % 10
print minute
if minute in [1, 3, 5, 7, 9]:
    dataCollector.sendUnuploadDatapoints(dataCollector.cpuTempSensorId);
elif minute in [2,6]:
    dataCollector.sendUnuploadDatapoints(dataCollector.tempSensorId);
elif minute in [4,8]:
    dataCollector.sendUnuploadDatapoints(dataCollector.humiditySensorId);
