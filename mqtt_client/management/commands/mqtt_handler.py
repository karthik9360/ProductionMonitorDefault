import paho.mqtt.client as mqtt
import json
import time
from django.core.management.base import BaseCommand
from mqtt_client.models import MqttSettings, Setting, DeviceDetails, DeviceData, LogData, ProductionData, MachineDetails
import datetime

class Command(BaseCommand):
    help = 'Starts the MQTT client and handles messages.'

    def handle(self, *args, **options):
        mqtt_broker = "mqtt.univa.cloud"
        mqtt_port = 1883
        subscribe_topic = "server_subscribe_topic"
        publish_topic = "server_subscribe_topic"
        mqtt_client_id = "mqtt_91bb53a0"
        mqtt_username = "admin"
        mqtt_password = "admin"

        global virtual_device_counts
        virtual_device_counts = {
            'virtual_device-1': 0,
            'virtual_device-2': 0,
            'virtual_device-3': 0,
            'virtual_device-4': 0,
            'virtual_device-5': 0,
            'virtual_device-6': 0,
            'virtual_device-7': 0,
            'virtual_device-8': 0,
            'virtual_device-9': 0,
            'virtual_device-0': 0,
        }

        mqtt_client = mqtt.Client(client_id=mqtt_client_id)
        default_data_interval = 1

        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                if enable_printing:
                    print('Connected successfully')

                client.subscribe(subscribe_topic)
                if enable_printing:
                    print(f'Subscribed to {subscribe_topic}')
            else:
                if enable_printing:
                    print(f'Bad connection. Code: {rc}')

        def on_message(client, userdata, msg):
            if enable_printing:
                print(f"Received message on topic {msg.topic}")
            message_data, log_data = log_message(msg, msg.topic)
            if message_data:
                if 'device_token' in message_data:
                    handle_command_message(client, msg, message_data, log_data)
                elif 'machine_id' in message_data:
                    handle_machine_data(client, msg, message_data, log_data)
                else:
                    if enable_printing:
                        print(f"Unhandled message data: {message_data}")

        def publish_message():
            global virtual_device_counts

            for key in virtual_device_counts.keys():
                virtual_device_counts[key] += 1

            message = {
                "device_token": "virtual-token-1",
                **virtual_device_counts,
                "shift_no": 1,
                "timestamp": int(time.time())
            }
            message_json = json.dumps(message)

            result = mqtt_client.publish(publish_topic, message_json)
            if enable_printing:
                print(f"Sent data: {message_json}")
                print(f"Publish result: {result.rc}")

        def publish_response(mqtt_client, device_token, response, is_error=False):
            try:
                mqtt_settings = MqttSettings.objects.first()
                if not mqtt_settings:
                    if enable_printing:
                        print("MqttSettings instance does not exist. Cannot publish response.")
                    return

                publish_topic = mqtt_settings.pub_topic
                result = mqtt_client.publish(publish_topic, json.dumps(response))
                if enable_printing:
                    print(f"Response Published to {publish_topic}: {response} with result {result.rc}")

            except Exception as e:
                if enable_printing:
                    print(f"An error occurred: {e}")

        def generate_unique_id():
            unique_id = int(time.time())
            return unique_id

        def log_message(message, topic):
            try:
                message_data = json.loads(message.payload.decode())
                
                date = message_data.get('date', datetime.date.today())
                time = message_data.get('time', datetime.datetime.now().time())
                
                unique_id = generate_unique_id()

                log_data, created = LogData.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'date': date,
                        'time': time,
                        'received_data': message_data,
                        'protocol': 'MQTT',
                        'topic_api': topic,
                    }
                )
                if enable_printing:
                    print(f"Logged message data: {message_data}")
                    print(f"LogData entry: {log_data}")
                return message_data, log_data

            except json.JSONDecodeError:
                if enable_printing:
                    print("Failed to decode JSON message")
                return None, None
            except Exception as e:
                if enable_printing:
                    print(f"An error occurred: {e}")
                return None, None

        def handle_command_message(mqtt_client, msg, message_data, log_data):
            current_timestamp = int(datetime.datetime.now().timestamp())
            device_token = message_data['device_token']

            try:
                device = DeviceDetails.objects.get(device_token=device_token)
                if enable_printing:
                    print("device", device)
                device_data = DeviceData(
                    date=datetime.date.today(),
                    time=datetime.datetime.now().time(),
                    data=message_data,
                    device_id=device,
                    protocol='MQTT',
                    topic_api=msg.topic,
                    log_data_id=log_data,
                )
                device_data.save()
                if enable_printing:
                    print(f'Saved device data to database: {device_data}')

                response = {
                    "status": "OK",
                    "device_token": device_token,
                    "cmd_response": current_timestamp,
                }
                publish_response(mqtt_client, device_token, response)

            except DeviceDetails.DoesNotExist:
                response = {
                    "status": "DEVICE NOT FOUND",
                    "message": "Device not found with given token"
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                if enable_printing:
                    print('Device token mismatch')

        def handle_machine_data(mqtt_client, msg, message_data, log_data):
            timestamp = message_data['timestamp']
            dt = datetime.datetime.fromtimestamp(timestamp)
            message_date = dt.date()
            message_time = dt.time()

            device_token = message_data.get('device_token', '')
            errors = []

            try:
                device = DeviceDetails.objects.get(device_token=device_token)
                if enable_printing:
                    print("device", device)
            except DeviceDetails.DoesNotExist:
                errors.append({
                    "status": "DEVICE NOT FOUND",
                    "message": "Device not found with given token",
                    "device_token": device_token,
                    "timestamp": timestamp
                })
                if enable_printing:
                    print('Device token mismatch')
                publish_response(mqtt_client, device_token, errors, is_error=True)
                return False

            device_first_data = DeviceData.objects.filter(device_id=device, protocol='MQTT').order_by('time').first()
            if device_first_data and "timestamp" in device_first_data.data:
                old_timestamp = device_first_data.data["timestamp"]
                if old_timestamp > timestamp:
                    errors.append({
                        "status": "INVALID TIMESTAMP",
                        "message": "Received timestamp is less than first data timestamp",
                        "device_token": device_token,
                        "timestamp": timestamp
                    })
                    if enable_printing:
                        print(f"Error: Received timestamp {timestamp} is less than first recorded timestamp {old_timestamp}")
                    publish_response(mqtt_client, device_token, errors, is_error=True)
                    return False

            current_timestamp = time.time()
            if current_timestamp < timestamp:
                errors.append({
                    "status": "INVALID TIMESTAMP",
                    "message": "Received timestamp is greater than current timestamp",
                    "device_token": device_token,
                    "timestamp": timestamp
                })
                if enable_printing:
                    print('Received timestamp is greater than current timestamp current =', current_timestamp, '- Received', timestamp)
                publish_response(mqtt_client, device_token, errors, is_error=True)
                return False

            machine_id = message_data.get('machine_id')
            if MachineDetails.objects.filter(machine_id=machine_id).exists():
                production_count = message_data.get('production_count')
                if production_count is not None:
                    last_production_data = ProductionData.objects.filter(machine_id=machine_id).last()
                    if last_production_data and production_count < last_production_data.production_count:
                        errors.append({
                            "status": "INVALID DATA",
                            "message": "Production count is less than last recorded value",
                            "device_token": device_token,
                            "timestamp": timestamp
                        })
                        if enable_printing:
                            print(f"Error: Production count {production_count} is less than last recorded {last_production_data.production_count}")
                        publish_response(mqtt_client, device_token, errors, is_error=True)
                        return False

                    production_data = ProductionData(
                        machine_id=machine_id,
                        production_count=production_count,
                        timestamp=timestamp,
                    )
                    production_data.save()
                    if enable_printing:
                        print(f'Saved production data to database: {production_data}')

                    response = {
                        "status": "OK",
                        "device_token": device_token,
                        "cmd_response": timestamp,
                    }
                    publish_response(mqtt_client, device_token, response)

                    return True
                else:
                    errors.append({
                        "status": "INVALID DATA",
                        "message": "Production count is missing in the data",
                        "device_token": device_token,
                        "timestamp": timestamp
                    })
                    if enable_printing:
                        print("Production count is missing")
                    publish_response(mqtt_client, device_token, errors, is_error=True)
                    return False
            else:
                errors.append({
                    "status": "MACHINE NOT FOUND",
                    "message": "Machine not found with given ID",
                    "machine_id": machine_id,
                    "timestamp": timestamp
                })
                if enable_printing:
                    print(f"Error: Machine not found with ID {machine_id}")
                publish_response(mqtt_client, device_token, errors, is_error=True)
                return False

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)

        mqtt_client.connect(mqtt_broker, mqtt_port, 60)

        mqtt_client.loop_start()

        while True:
            publish_message()
            time.sleep(default_data_interval)
