#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Council";
const char* password = "Rafidona1964";

// MQTT broker settings
const char* mqtt_server = "192.168.0.108"; // Raspberry Pi IP
const int mqtt_port = 1883;
const char* firmware_topic = "lightchain/devices/firmware";
const char* client_id = "esp32-DEVICE-001";

WiFiClient espClient;
PubSubClient client(espClient);

// Device identity
String device_id = "esp32-DEVICE-001";

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("🔌 Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("🔗 Attempting MQTT connection...");
    if (client.connect(client_id)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" 😴 retrying in 3 seconds");
      delay(3000);
    }
  }
}

void sendFirmware() {
  uint32_t sketchSize = ESP.getSketchSize();
  const uint32_t startAddr = 0x0;   // firmware always starts at 0 for ESP8266
  const size_t chunkSize = 512;     // safe chunk size

  Serial.printf("📦 Firmware size: %u bytes\n", sketchSize);

  uint8_t buffer[chunkSize];
  uint32_t offset = 0;
  int chunkIndex = 0;

  while (offset < sketchSize) {
    uint32_t len = min(chunkSize, sketchSize - offset);
    memcpy_P(buffer, (const void*)(startAddr + offset), len);

    // Encode as hex string
    String chunk = "";
    for (uint32_t i = 0; i < len; i++) {
      if (buffer[i] < 16) chunk += "0";
      chunk += String(buffer[i], HEX);
    }

    String payload = "{\"device_id\":\"" + device_id +
                     "\", \"index\":" + String(chunkIndex) +
                     ", \"total\":" + String((sketchSize + chunkSize - 1) / chunkSize) +
                     ", \"data\":\"" + chunk + "\"}";

    if (client.publish("lightchain/devices/firmware", payload.c_str())) {
      Serial.printf("✅ Sent chunk %d/%d\n", chunkIndex + 1,
                    (sketchSize + chunkSize - 1) / chunkSize);
    } else {
      Serial.printf("❌ Failed to send chunk %d\n", chunkIndex);
    }

    offset += len;
    chunkIndex++;
    delay(100); // prevent flooding
  }

  Serial.println("🎉 Firmware transmission complete!");
}


void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  reconnect();

  delay(2000); // wait for MQTT stable
  sendFirmware();
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
}
