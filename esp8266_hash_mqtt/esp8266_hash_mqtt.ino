#include <WiFi.h>
#include <PubSubClient.h>
#include "mbedtls/sha256.h"

// WiFi credentials
const char* ssid = "Council";
const char* password = "Rafidona1964";

// MQTT broker settings
const char* mqtt_server = "192.168.0.108";
const int mqtt_port = 1883;
const char* join_topic = "lightchain/devices/join";
const char* client_id = "esp32-DEVICE-001"; // MQTT client ID

WiFiClient espClient;
PubSubClient client(espClient);

// Device identity
String device_id = "esp32-DEVICE-001";

// Function to calculate SHA256 firmware hash using mbedTLS
String getFirmwareHash() {
  uint32_t sketchSize = ESP.getSketchSize();
  uint8_t buffer[512];
  mbedtls_sha256_context ctx;
  uint8_t hash[32];

  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts_ret(&ctx, 0); // 0 for SHA-256

  for (uint32_t offset = 0; offset < sketchSize; offset += sizeof(buffer)) {
    uint32_t len = min(sizeof(buffer), sketchSize - offset);
    memcpy_P(buffer, (const void*)(ESP.getSketchStart() + offset), len);
    mbedtls_sha256_update_ret(&ctx, buffer, len);
  }

  mbedtls_sha256_finish_ret(&ctx, hash);
  mbedtls_sha256_free(&ctx);

  String hashStr = "";
  for (int i = 0; i < 32; ++i) {
    if (hash[i] < 0x10) hashStr += "0";
    hashStr += String(hash[i], HEX);
  }
  return hashStr;
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("🔌 Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi");
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("🔗 Attempting MQTT connection...");
    // Attempt to connect
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

void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);

  reconnect();

  String firmware_hash = getFirmwareHash();
  Serial.println("🔍 Firmware SHA256 Hash: " + firmware_hash);

  // Prepare JSON payload
  String json = "{\"device_id\": \"" + device_id + "\", \"firmware_hash\": \"" + firmware_hash + "\"}";
  Serial.println("📤 Publishing: " + json);

  // Publish to MQTT join topic
  if (client.publish(join_topic, json.c_str())) {
    Serial.println("✅ Registration message published to MQTT.");
  } else {
    Serial.println("❌ Failed to publish registration message.");
  }
}

void loop() {
  // Keep MQTT connection alive
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  // No repeated registration; you can modify to periodically check or listen for approval if desired
}
