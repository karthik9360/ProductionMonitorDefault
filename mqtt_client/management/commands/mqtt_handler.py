from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
import json
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import time
from mqtt_client.models import MqttSettings, LogData, DeviceData, MachineData, ProductionData, DeviceDetails, MachineDetails

class Command(BaseCommand):
    help = 'Starts the MQTT client and handles messages'

    def handle(self, *args, **kwargs):
        global subscribed_topics
        subscribed_topics = set()
        global mqtt_client
        mqtt_client = mqtt.Client()
        global default_data_interval
        default_data_interval = 5

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print('Connected successfully')
                devices = DeviceDetails.objects.all()

                for device in devices:
                    sub_topic = device.sub_topic
                    if sub_topic and sub_topic not in subscribed_topics:
                        mqtt_client.subscribe(sub_topic)
                        subscribed_topics.add(sub_topic)
                        print(f'Subscribed to {sub_topic}')

                print("All topics are successfully subscribed!!")
                threading.Thread(target=publish_default_data_periodically, daemon=True).start()

            else:
                print(f'Bad connection. Code: {rc}')

        @receiver(post_save, sender=DeviceDetails)
        def handle_device_details_save(sender, instance, **kwargs):
            if instance.sub_topic:
                subscribe_to_topic(instance.sub_topic)

        def subscribe_to_topic(sub_topic):
            if sub_topic not in subscribed_topics:
                mqtt_client.subscribe(sub_topic)
                subscribed_topics.add(sub_topic)
                print(f'Subscribed to {sub_topic}')
            else:
                print(f'Topic {sub_topic} is already subscribed.')

        def publish_response(mqtt_client, device_token, response, is_error=False):
            try:
                device = DeviceDetails.objects.get(device_token=device_token)
                publish_topic = device.pub_topic
                result = mqtt_client.publish(publish_topic, json.dumps(response))
                print(f"Response Published to {publish_topic}: {response} with result {result}")
            except DeviceDetails.DoesNotExist:
                print(f"Device with token {device_token} not found. Cannot publish response.")

        def on_message(mqtt_client, userdata, msg):
            print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
            currentMessage = msg.payload.decode()
            currentTopic = msg.topic.split("/")
            print(currentTopic)
            print(currentMessage)

            try:
                message_data = json.loads(currentMessage)
            except json.JSONDecodeError as e:
                print("status: ERROR JSON message: Not a valid JSON received")
                print(f'Error decoding JSON: {e}')
                return

            timestamp = message_data.get('timestamp', int(datetime.datetime.now().timestamp()))
            message_data['timestamp'] = timestamp
            unique_id = str(timestamp)
            current_date = datetime.date.today()
            current_time = datetime.datetime.now().time()

            if not LogData.objects.filter(unique_id=unique_id).exists():
                log_data = LogData(
                    date=current_date,
                    time=current_time,
                    received_data=currentMessage,
                    protocol='MQTT',
                    topic_api=msg.topic,
                    unique_id=unique_id
                )
                log_data.save()
                print(f'Saved log data to database: {log_data}')
            else:
                log_data = LogData.objects.get(unique_id=unique_id)
                print(f'Log data with unique_id {unique_id} already exists: {log_data}')
                device_token = str(message_data.get('device_token', ''))
                response = {
                    "status": "Duplicate Timestamp",
                    "message": "Timestamp already exists",
                    "Device Token": device_token,
                    "timestamp": message_data['timestamp']
                }
                publish_response(mqtt_client, device_token, response, is_error=True)
                return

            device_token = message_data.get('device_token', '')
            if 'cmd' in message_data and message_data['cmd'] == "TIMESTAMP" and device_token:
                current_timestamp = int(datetime.datetime.now().timestamp())
                try:
                    device = DeviceDetails.objects.get(device_token=device_token)
                    device_data = DeviceData(
                        date=current_date,
                        time=current_time,
                        data=message_data,
                        device_id=device,
                        protocol='MQTT',
                        topic_api=msg.topic,
                        log_data_id=log_data
                    )
                    device_data.save()
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
                    print('Device token mismatch')

            elif 'timestamp' in message_data and device_token:
                dt = datetime.datetime.fromtimestamp(timestamp)
                message_date = dt.date()
                message_time = dt.time()

                try:
                    first_log = LogData.objects.first()
                    if first_log:
                        try:
                            first_timestamp = int(first_log.unique_id)
                        except ValueError:
                            first_timestamp = int(datetime.datetime.strptime(first_log.unique_id, "%Y-%m-%d %H:%M:%S").timestamp())

                        if timestamp < first_timestamp:
                            response = {
                                "status": "INVALID TIMESTAMP",
                                "message": "Timestamp is less than first data",
                                "device_token": device_token,
                                "timestamp": timestamp
                            }
                            publish_response(mqtt_client, device_token, response, is_error=True)
                            print(f"Error: Timestamp is less than the first recorded timestamp")
                            return

                    machine_id = message_data.get('machine_id')
                    production_count = message_data.get('production_count')
                    machine = MachineDetails.objects.filter(machine_id=machine_id).first()
                    if machine is None:
                        response = {
                            "status": "INVALID MACHINE ID",
                            "message": "Machine ID not found",
                            "device_token": device_token,
                            "timestamp": timestamp
                        }
                        publish_response(mqtt_client, device_token, response, is_error=True)
                        print(f"Error: Machine ID not found")
                        return

                    if production_count is not None:
                        last_production_data = ProductionData.objects.filter(machine_id=machine.machine_id).last()
                        if last_production_data and production_count < last_production_data.production_count:
                            response = {
                                "status": "PRODUCTION COUNT ERROR",
                                "message": "Production count is less than the last recorded count",
                                "device_token": device_token,
                                "timestamp": timestamp
                            }
                            publish_response(mqtt_client, device_token, response, is_error=True)
                            print(f"Error: Production count is less than the last recorded count")
                            return

                    production_data = ProductionData(
                        machine_id=machine.machine_id,
                        production_count=production_count,
                        date=message_date,
                        time=message_time
                    )
                    production_data.save()
                    print(f'Saved production data to database: {production_data}')
                except Exception as e:
                    response = {
                        "status": "DATA SAVE ERROR",
                        "message": f"Error saving machine data: {e}",
                        "device_token": device_token,
                        "timestamp": timestamp
                    }
                    publish_response(mqtt_client, device_token, response, is_error=True)
                    print(f'Error saving machine data to database: {e}')

        def publish_default_data_periodically():
            while True:
                try:
                    default_data = {
                        "device_token": "default_token",
                        "cmd": "DEFAULT_CMD",
                        "timestamp": int(datetime.datetime.now().timestamp())
                    }
                    publish_topic = "default/topic"
                    mqtt_client.publish(publish_topic, json.dumps(default_data))
                    print(f"Default data published to {publish_topic}: {default_data}")
                except Exception as e:
                    print(f'Error publishing default data: {e}')
                time.sleep(default_data_interval)

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        mqtt_client.connect("mqtt.univa.cloud", 1883, 60)
        mqtt_client.loop_start()

        # Run forever
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
