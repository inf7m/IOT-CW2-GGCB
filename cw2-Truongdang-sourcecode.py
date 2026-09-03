import asyncio
import json
import random
from datetime import datetime, timezone

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message


# ============================================================
# AZURE CONFIGURATION
# ============================================================

HOSTNAME = "iotcw2truongdang.azure-devices.net"
DEVICE_ID = "hospital-room-101"
DEVICE_KEY = "hxE1N904zEeOvprg624Po6zYW80AiM9/+UxeU67CaZo="

# PROJECT DATA RANDOM CONFIGURATION

ROOM_ID = "Room-101"

TOTAL_MESSAGES = 20
SEND_INTERVAL_SECONDS = 3



# GENERATE NORMAL SENSOR DATA

def generate_normal_data():

    return {
        "temperature": round(random.uniform(23.0, 27.0), 1),
        "humidity": round(random.uniform(45.0, 65.0), 1),
        "heartRate": random.randint(65, 95),
        "bedStatus": "occupied"
    }


#  RULE FOR ABNORMAL SENSOR DATA *1 for 5

def generate_abnormal_data():

    scenario = random.choice([
        "high_heart_rate",
        "high_temperature",
        "high_humidity"
    ])

    data = generate_normal_data()

    if scenario == "high_heart_rate":
        data["heartRate"] = random.randint(125, 150)

    elif scenario == "high_temperature":
        data["temperature"] = round(
            random.uniform(29.0, 33.0),
            1
        )

    elif scenario == "high_humidity":
        data["humidity"] = round(
            random.uniform(72.0, 85.0),
            1
        )

    return data



# ANALYSE SENSOR DATA

def analyse_sensor_data(data):

    alerts = []

    # Room temperature rule
    if data["temperature"] > 28:
        alerts.append("HIGH TEMPERATURE")

    # Humidity rule
    if data["humidity"] > 70:
        alerts.append("HIGH HUMIDITY")

    # Heart rate rules
    if data["heartRate"] > 120:
        alerts.append("HIGH HEART RATE")

    elif data["heartRate"] < 50:
        alerts.append("LOW HEART RATE")


    # Determine overall status
    if len(alerts) == 0:

        status = "NORMAL"
        alert_message = "NONE"

    else:

        status = "CRITICAL"
        alert_message = " | ".join(alerts)


    return status, alert_message


# CREATE TELEMETRY RECORD TO PUSH INTO AZURE IOT

def build_telemetry(message_id):

    # Every 5th message will intentionally be abnormal
    # This makes the demonstration predictable.
    if message_id % 5 == 0:

        sensor_data = generate_abnormal_data()

        simulation_type = "ABNORMAL"

    else:

        sensor_data = generate_normal_data()

        simulation_type = "NORMAL"


    status, alert = analyse_sensor_data(sensor_data)


    telemetry = {

        "messageId": message_id,

        "deviceId": DEVICE_ID,

        "roomId": ROOM_ID,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "temperature": sensor_data["temperature"],

        "humidity": sensor_data["humidity"],

        "heartRate": sensor_data["heartRate"],

        "bedStatus": sensor_data["bedStatus"],

        "simulationType": simulation_type,

        "status": status,

        "alert": alert
    }


    return telemetry



# CREATE AZURE MESSAGE

def create_azure_message(telemetry):

    message = Message(
        json.dumps(telemetry)
    )

    message.content_type = "application/json"

    message.content_encoding = "utf-8"

    message.message_id = str(
        telemetry["messageId"]
    )

    return message


# DISPLAY TELEMETRY

def print_telemetry(data):

    print("\n========================================")

    print(
        "MESSAGE ID      :",
        data["messageId"]
    )

    print(
        "ROOM            :",
        data["roomId"]
    )

    print(
        "TIMESTAMP       :",
        data["timestamp"]
    )

    print(
        "TEMPERATURE     :",
        data["temperature"],
        "°C"
    )

    print(
        "HUMIDITY        :",
        data["humidity"],
        "%"
    )

    print(
        "HEART RATE      :",
        data["heartRate"],
        "BPM"
    )

    print(
        "BED STATUS      :",
        data["bedStatus"]
    )

    print(
        "SIMULATION TYPE :",
        data["simulationType"]
    )

    print(
        "SYSTEM STATUS   :",
        data["status"]
    )

    print(
        "ALERT           :",
        data["alert"]
    )


# MAIN APPLICATION

async def main():

    print("========================================")
    print(" SMART HOSPITAL IoT MONITORING SYSTEM")
    print("========================================")

    print("\nConnecting to Azure IoT Hub...")


    # --------------------------------------------------------
    # CREATE DEVICE CLIENT
    # --------------------------------------------------------

    device = IoTHubDeviceClient.create_from_symmetric_key(

        symmetric_key=DEVICE_KEY,

        hostname=HOSTNAME,

        device_id=DEVICE_ID,

        product_info="HospitalRoomMonitoringSystem"
    )


    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    try:

        await device.connect()

        print(
            "Connected:",
            device.connected
        )

        print(
            "Device:",
            DEVICE_ID
        )


        # ----------------------------------------------------
        # SEND TELEMETRY
        # ----------------------------------------------------

        for message_id in range(
            1,
            TOTAL_MESSAGES + 1
        ):

            # Generate telemetry
            telemetry = build_telemetry(
                message_id
            )


            # Display locally
            print_telemetry(
                telemetry
            )


            # Convert to Azure message
            message = create_azure_message(
                telemetry
            )


            # Send to Azure IoT Hub
            await device.send_message(
                message
            )


            print(
                "AZURE           : MESSAGE SENT SUCCESSFULLY"
            )


            # Wait before next sensor reading
            await asyncio.sleep(
                SEND_INTERVAL_SECONDS
            )


        print(
            "\n========================================"
        )

        print(
            "Simulation completed successfully."
        )


    # --------------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------------

    except Exception as error:

        print("\nERROR:")

        print(error)


    # --------------------------------------------------------
    # DISCONNECT
    # --------------------------------------------------------

    finally:

        await device.shutdown()

        print(
            "\nDevice disconnected."
        )


# ============================================================
# RUN PROGRAM
# ============================================================

await main()
