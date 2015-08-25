#!/usr/bin/python
 
import time;
import json;
import os;
import Adafruit_DHT;
import ConfigParser
import MySQLdb

class DataCollector():
    timestamp_fmt = "%Y-%m-%dT%H:%M:%S"
    curl_fmt = 'curl -X POST -d "%s" -H "Content-Type: application/json"' + \
            ' -H "U-ApiKey:%s" http://api.yeelink.net/v1.0/device/%s/' + \
            'sensor/%s/datapoints'

    def __init__(self):
        cf = ConfigParser.ConfigParser()
	print os.path.dirname(__file__) + "/sensorHub.config"
        cf.read(os.path.dirname(__file__) + "/sensorHub.config")
        self.apiKey = cf.get("sensor", "apiKey")
        self.deviceId = cf.get("sensor", "deviceId")
        self.cpuTempSensorId = cf.get("sensor", "cpuTempSensorId")
        self.tempSensorId = cf.get("sensor", "tempSensorId")
        self.humiditySensorId = cf.get("sensor", "humiditySensorId")
        dbUserName = cf.get("db", "user")
        dbPwd = cf.get("db", "pwd")

        try:
            self.conn = MySQLdb.connect(host='localhost',user=dbUserName,passwd=dbPwd,db='sensor',port=3306)
        except MySQLdb.Error, e:
            print "Mysql Error %d:%s" % (e.args[0], e.args[1])

        self.arg = self.apiKey

    def sendSensorData(self, sensorId, value):
        json_data = {"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S"),"value":value}
        json_str = json.dumps(json_data)
        json_str = json_str.replace("\"", "\\\"")
        curl_str = curl_fmt % (json_str, self.apiKey, deviceId, sensorId)
        print curl_str
        result = os.system(curl_str)
        print result

    def saveSensorData(self, sensorId, value):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S");
        isUploaded = 0;
        sql = "INSERT INTO datapionts(sensor_id, value, timestamp, uploaded) value(%s, %f, '%s', %d)" % (sensorId, value, timestamp, isUploaded);
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d:%s" % (e.args[0], e.args[1])

        print sql;

    def getCpuTemp(self,):
        fd = file("/sys/class/thermal/thermal_zone0/temp")
        cpuSensorRawValue = fd.readline()
        cpuTemp = float(cpuSensorRawValue) / 1000
        return cpuTemp;

    def sendUnuploadDatapoints(self, sensorId):
        sql = "select id, timestamp, value from datapionts where sensor_id = %s" % (sensorId)
        print sql
        try:
            cur = self.conn.cursor()
            count = cur.execute(sql)
            
            if count > 0:
                result = cur.fetchall()
                datapoints = []
                ids = []
                for datapoint in result:
                    datapoints.append({"timestamp":datapoint[1].strftime(self.timestamp_fmt),"value":datapoint[2]})
                    ids.append(str(datapoint[0]))
                    print datapoint

                json_str = json.dumps(datapoints)
                json_str = json_str.replace("\"", "\\\"")
                curl_str = self.curl_fmt % (json_str, self.apiKey, self.deviceId, sensorId)
                result = os.system(curl_str)
                if result == 0:
                    print "succ"
                    self.updateDataPointToUploaded(",".join(ids))
                else:
                    print "result unknown" + str(result)

        except MySQLdb.Error, e:
            print "Mysql Error %d:%s" % (e.args[0], e.args[1])

    def updateDataPointToUploaded(self, ids):
        try:
            sql = "update datapionts set uploaded=1 where id in (%s)" % (ids)
            print sql
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            cur.close()
        except MySQLdb.Error, e:
            print "Mysql Error %d:%s" % (e.args[0], e.args[1])

    def __del__(self):
        self.conn.close()


