import json
from datetime import datetime as dt
class ReadingsToTuples:
    @staticmethod
    def pipeline(payloads):
        payloads_iter = iter(payloads)

        while (readings := next(payloads_iter)):
            yield ReadingsToTuples.split_readings(readings)
    
    @staticmethod
    def split_readings(readings: str, datetime_obj=dt):
        readings = json.loads(readings)
        reading_tuples = []
        now_str = datetime_obj.now().strftime("%Y-%m-%d %H:%M:%S")

        # get tuples for temp, pressure, humidity
        reading_tuples = list(filter(lambda item: item[0] in ("temp", "pressure", "humidity"), readings.items()))
        # get them in order "temp, pressure, humidity"
        reading_tuples.sort(key=lambda t: t[0], reverse=True)
        
        for i, reading_tuple in enumerate(reading_tuples):
            reading_tuples[i] = (
                (now_str, readings["pico_id"], readings["pico_uuid"], readings["sensor"], *reading_tuple)
            )
                
        return tuple(reading_tuples)