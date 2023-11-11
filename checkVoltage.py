import asyncio
import json
import struct
from bleak import BleakScanner
from TheengsDecoder import decodeBLE as dble
from TheengsDecoder import getProperties, getAttribute

target_device_address = "50:54:7B:22:5F:86"

def detection_callback(device, advertisement_data):
    if device.address == target_device_address:
        print(f"{device.address}:{advertisement_data}")
        data_json = {}

        if advertisement_data.service_data:
            dstr = list(advertisement_data.service_data.keys())[0]
            data_json['servicedatauuid'] = dstr[4:8]
            dstr = str(list(advertisement_data.service_data.values())[0].hex())
            data_json['servicedata'] = dstr

        if advertisement_data.manufacturer_data:
            dstr = str(struct.pack('<H', list(advertisement_data.manufacturer_data.keys())[0]).hex())
            dstr += str(list(advertisement_data.manufacturer_data.values())[0].hex())
            data_json['manufacturerdata'] = dstr

        if advertisement_data.local_name:
            data_json['name'] = advertisement_data.local_name

        if data_json:
            data_json["id"] = device.address
            data_json["rssi"] = advertisement_data.rssi
            print("data sent to decoder: ", json.dumps(data_json))
            data_json = dble(json.dumps(data_json))
            print("TheengsDecoder found device:", data_json)

            if data_json:
                dev = json.loads(data_json)
                print(getProperties(dev['model_id']))
                brand = getAttribute(dev['model_id'], 'brand')
                model = getAttribute(dev['model_id'], 'model')
                print("brand:", brand, ", model:", model)


async def main():
    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    await asyncio.sleep(15.0)
    await scanner.stop()

    for d in scanner.discovered_devices:
        print(d)

asyncio.run(main())
