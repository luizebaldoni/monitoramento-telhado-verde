/*

 * LEITURA DE SENSORES PARA TELHADO VERDE INTELIGENTE

 * Autor: Equipe de Hardware - Grupo 5 Projeto Integrador em Engenharia de Computação
 * Data final: 03/12/2025
 * DESCRIÇÃO:
 * - Código para leitura integrada de múltiplos sensores em um sistema de telhado verde inteligente.
 * - Realiza a leitura de:
 *   - 3 sensores DS18B20 (temperatura do ar) em barramento OneWire.
 *   - 1 sensor DHT11 (temperatura e umidade do ar).
 *   - 1 sensor ultrassônico HC-SR04 (distância/nível).
 *   - 1 sensor de umidade do solo HL-69 (via entrada analógica, com calibração seco/molhado).
 * - Exibe no monitor serial as leituras em formato legível, incluindo checagem de erro e mapeamento em porcentagem para o HL-69.
 *
 * REQUISITOS:
 * - Hardware:
 *   - Placa compatível com Arduino com suporte a GPIO digitais e analógicos (ex.: ESP32, Arduino UNO/Mega com ajustes de pinos).
 *   - 3 sensores DS18B20 ligados em barramento OneWire com resistor de pull-up adequado (geralmente 4k7).
 *   - 1 sensor DHT11 conectado ao pino digital configurado (DHTPIN).
 *   - 1 sensor ultrassônico HC-SR04 (pinos TRIG e ECHO).
 *   - 1 sensor de umidade do solo HL-69 conectado a uma entrada analógica.
 *   - Fonte de alimentação compatível com os sensores e a placa (5 V ou 3,3 V conforme especificação de cada módulo).
 * - Software:
 *   - Arduino IDE ou plataforma compatível para compilação e gravação do código.
 *   - Bibliotecas instaladas:
 *     - OneWire (comunicação 1-Wire com DS18B20). [web:3][web:11][web:14]
 *     - DallasTemperature (leitura de múltiplos DS18B20 por endereço). [web:6][web:9][web:18]
 *     - DHT (leitura de temperatura e umidade do sensor DHT11). [web:4][web:17][web:20]
 *   - Configuração correta da porta serial (115200 baud) para visualização dos dados.
 * - Observações:
 *   - Os valores HL69_DRY_RAW e HL69_WET_RAW devem ser ajustados por calibração prática (solo seco e solo úmido) para cada montagem. [web:7][web:10][web:16]
 *   - O tempo de leitura é controlado por millis(), com intervalo definido em READ_INTERVAL_MS para evitar leituras excessivas e melhorar a estabilidade das medições. [web:1][web:5]

 */


/////// INCLUSÃO DE BIBLIOTECAS //////

#include <OneWire.h>           // Comunicação 1-Wire (DS18B20)
#include <DallasTemperature.h> // Biblioteca de alto nível para DS18B20
#include <DHT.h>               // Biblioteca para sensor DHT (DHT11)
#include <WiFi.h>              // Biblioteca WiFi
#include <NTPClient.h>         // Biblioteca NTP Client
#include <ArduinoJson.h>       // Biblioteca ArduinoJson
#include <HTTPClient.h>        // Biblioteca HTTP Client
#include <ArduinoOTA.h>        // Biblioteca Arduino OTA

////// DEFINIÇÕES DE PINOS //////

#define ONE_WIRE_BUS 18  // Pino de dados do barramento OneWire (DS18B20)
#define DHTPIN 4         // Pino de dados do DHT11
#define DHTTYPE DHT11    // Tipo de sensor DHT utilizado
#define TRIG_PIN 34      // Pino TRIG do HC-SR04
#define ECHO_PIN 26      // Pino ECHO do HC-SR04
#define HL69_PIN 5       // Pino analógico para leitura do HL-69 (umidade do solo)
#define MAX_DS 3        // Número máximo de sensores DS18B20 tratados

////// CRIAÇÃO DE OBJETOS DOS SENSORES //////

OneWire oneWire(ONE_WIRE_BUS);          // Instância do barramento OneWire
DallasTemperature sensors(&oneWire);    // Gerenciador dos sensores DS18B20
DHT dht(DHTPIN, DHTTYPE);               // Objeto para o sensor DHT11
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "br.pool.ntp.org", -3 * 3600);  // UTC-3 (Brasília)

////// VARIAVEIS GLOBAIS //////
//& Variáveis para controle de intervalo entre leituras
unsigned long lastRead = 0;                 // Armazena o instante da última leitura
const unsigned long READ_INTERVAL_MS = 2000; // Intervalo entre leituras em ms (2 s)

//& Valores de calibração do sensor HL-69 (ajustar conforme necessário)
int HL69_DRY_RAW = 3000;  // Valor analógico aproximado para solo seco (ajustar via calibração)
int HL69_WET_RAW = 1200;  // Valor analógico aproximado para solo úmido (ajustar via calibração)

///& Armazenamento dos endereços dos sensores DS18B20
DeviceAddress dsAddr[MAX_DS];         // Vetor para armazenar os endereços dos sensores
uint8_t dsCount = 0;                  // Quantidade efetiva de sensores detectados

//& Credenciais Wi-Fi
const char* ssid = "SEU_SSID";        // SSID da rede Wi-Fi à qual o ESP8266 se conectará
const char* password = "SUA_SENHA";           // Senha da rede Wi-Fi

//& URL do servidor API (substitua pelo IP ou domínio do seu Ubuntu Server)
const char* SERVER_URL = "http://192.168.1.100:8000/sensor-data"; // <-- ajuste aqui
const char* DEVICE_ID = "ESP32_TELHADO_VERDE";

////// FUNÇÕES AUXILIARES //////

//& Imprime no monitor serial o endereço 1-Wire (8 bytes em HEX) de um DS18B20
void printAddress(const DeviceAddress addr) {
  for (uint8_t i = 0; i < 8; i++) {
    if (addr[i] < 16) Serial.print("0");
    Serial.print(addr[i], HEX);
  }
}

//& Compara se dois endereços 1-Wire são idênticos
bool sameAddr(const DeviceAddress a, const DeviceAddress b) {
  for (int i = 0; i < 8; i++) if (a[i] != b[i]) return false;
  return true;
}

//& Converte leitura bruta do HL-69 para porcentagem de umidade (0–100 %)
static float mapPercent(int raw, int rawDry, int rawWet) {
  if (rawDry == rawWet) return 0;
  float pct = (float)(raw - rawDry) / (float)(rawWet - rawDry) * 100.0f;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return pct;
}

//& Retorna um nome padrão para cada DS18B20, com base no índice
const char* defaultName(uint8_t i) {
  static const char* N[MAX_DS] = {"DS_A", "DS_B", "DS_C"};
  return (i < MAX_DS) ? N[i] : "DS_X";
}

// NEW: helper to format ISO8601 timestamp from NTPClient epoch
String formatIsoTimestamp(unsigned long epoch) {
  // epoch from NTPClient already has timezone offset applied if configured
  time_t t = (time_t)epoch;
  struct tm tminfo;
  gmtime_r(&t, &tminfo); // safe on ESP32
  char buf[32];
  snprintf(buf, sizeof(buf), "%04d-%02d-%02dT%02d:%02d:%02d",
           tminfo.tm_year + 1900,
           tminfo.tm_mon + 1,
           tminfo.tm_mday,
           tminfo.tm_hour,
           tminfo.tm_min,
           tminfo.tm_sec);
  return String(buf);
}

// NEW: Send JSON payload to FastAPI endpoint
bool sendSensorData(const char* url, const char* device_id, const String &timestamp_iso,
                    float ds_temp, float dht_temp, float dht_hum, float hcsr_dist,
                    int hl_raw, float hl_pct) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi não conectado. Tentando reconectar...");
    WiFi.begin(ssid, password);
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
      delay(200);
    }
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Falha ao conectar WiFi para envio.");
      return false;
    }
  }

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Prepare JSON using ArduinoJson
  StaticJsonDocument<1024> doc;
  doc["device_id"] = device_id;
  doc["timestamp"] = timestamp_iso;
  JsonObject sensors = doc.createNestedObject("sensors");

  JsonObject ds = sensors.createNestedObject("ds18b20");
  ds["temperature"] = ds_temp;
  ds["unit"] = "celsius";
  ds["status"] = (ds_temp == DEVICE_DISCONNECTED_C) ? "error" : "ok";

  JsonObject dht = sensors.createNestedObject("dht11");
  dht["temperature"] = dht_temp;
  dht["humidity"] = dht_hum;
  dht["unit_temp"] = "celsius";
  dht["unit_humidity"] = "percent";
  dht["status"] = (isnan(dht_temp) || isnan(dht_hum)) ? "error" : "ok";

  JsonObject hcsr = sensors.createNestedObject("hcsr04");
  hcsr["distance"] = hcsr_dist;
  hcsr["unit"] = "cm";
  hcsr["status"] = (hcsr_dist <= 0) ? "error" : "ok";

  JsonObject hl = sensors.createNestedObject("hl69");
  hl["soil_moisture"] = hl_pct;
  hl["raw_value"] = hl_raw;
  hl["unit"] = "percent";
  hl["status"] = "ok";

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.print("HTTP POST code: "); Serial.println(httpCode);
    String resp = http.getString();
    Serial.print("Resposta: "); Serial.println(resp);
    http.end();
    return (httpCode >= 200 && httpCode < 300);
  } else {
    Serial.print("Falha POST: "); Serial.println(http.errorToString(httpCode));
    http.end();
    return false;
  }
}


////// FUNÇÃO DE CONFIGURAÇÃO //////

void setup() {
  Serial.begin(115200);  // Inicializa comunicação serial
  delay(200);

  // NEW: Conecta Wi-Fi
  Serial.print("Conectando em WiFi: "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    delay(250);
    Serial.print('.');
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi conectado. IP: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Aviso: não foi possível conectar ao WiFi no setup.");
  }

  // NEW: Inicializa NTP client
  timeClient.begin();
  timeClient.update();

  //& Inicialização dos sensores DS18B20 no barramento OneWire
  sensors.begin();
  dsCount = sensors.getDeviceCount();     // Lê quantidade de dispositivos 1-Wire detectados
  if (dsCount > MAX_DS) dsCount = MAX_DS; // Limita ao máximo definido

  Serial.print("DS18B20 encontrados no barramento: ");
  Serial.println(sensors.getDeviceCount());
  if (dsCount == 0) {
    Serial.println("ATENCAO: nenhum DS18B20 detectado!");
  } else {
    //& Obtém e armazena os primeiros endereços válidos detectados
    uint8_t filled = 0;
    DeviceAddress tmp;
    for (uint8_t idx = 0; filled < dsCount && sensors.getAddress(tmp, filled); filled++) {
      memcpy(dsAddr[filled], tmp, 8);
    }
    dsCount = filled;

    //& Mostra os endereços dos sensores DS18B20 encontrados
    for (uint8_t i = 0; i < dsCount; i++) {
      Serial.print("Sensor "); Serial.print(defaultName(i)); Serial.print(" -> 0x");
      printAddress(dsAddr[i]); Serial.println();
    }

    //& Ajusta opcionalmente a resolução dos DS18B20 para 12 bits (maior precisão, conversão mais lenta)
    if (sensors.getResolution() != 12) sensors.setResolution(12);
  }

  //& Inicialização do sensor DHT11 (temperatura e umidade do ar)
  dht.begin();
  Serial.println("DHT11 inicializado no GPIO4.");

  //& Configuração dos pinos do sensor ultrassônico HC-SR04
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("HC-SR04 inicializado.");

  //& Configuração do sensor de umidade do solo HL-69
  pinMode(HL69_PIN, INPUT);
#ifdef ARDUINO_ARCH_ESP32
  analogSetPinAttenuation(HL69_PIN, ADC_11db);  // Ajusta a atenuação do ADC no ESP32 para melhor faixa de leitura
#endif
  Serial.println("HL-69 inicializado (GPIO5).");
}


////// FUNÇÃO PRINCIPAL //////

void loop() {
  unsigned long now = millis();
  if (now - lastRead < READ_INTERVAL_MS) return; //& Garante intervalo mínimo entre leituras
  lastRead = now;

  //& Limpa visualmente o monitor serial com linhas em branco
  for (int i = 0; i < 10; i++) Serial.println();

///// LEITURA DOS SENSORES DS18B20 (POR ENDEREÇO) /////
  sensors.requestTemperatures(); // Solicita conversão de temperatura a todos os DS18B20
  float last_ds_temp = DEVICE_DISCONNECTED_C;
  for (uint8_t i = 0; i < dsCount; i++) {
    float t = sensors.getTempC(dsAddr[i]);              // Lê temperatura em °C do endereço correspondente
    bool ok = (t != DEVICE_DISCONNECTED_C);             // Verifica se o sensor respondeu corretamente

    const char* nome = nullptr;
    if (!nome) nome = defaultName(i);                   // Nome padrão para identificação do sensor

    if (ok) {
      Serial.print(nome); Serial.print("  Temp: ");
      Serial.print(t, 2); Serial.println(" °C");
      last_ds_temp = t;
    } else {
      Serial.print(nome); Serial.println("  ERRO (-127 °C) — confira fiação/pull-up.");
      Serial.print("Endereço 0x"); printAddress(dsAddr[i]); Serial.println();
    }
  }

 ///// LEITURA DO SENSOR DHT11 /////
  float hum  = dht.readHumidity();       // Umidade relativa do ar em %
  float tDHT = dht.readTemperature();    // Temperatura do ar em °C
  bool dht_ok = !(isnan(hum) || isnan(tDHT));
  if (dht_ok) {
    Serial.print("DHT11    Temp: "); Serial.print(tDHT, 2);
    Serial.print(" °C  |  Umid: "); Serial.print(hum, 1); Serial.println(" %");
  } else {
    Serial.println("DHT11    Falha de leitura.");
  }

 /////LEITURA DO SENSOR ULTRASSÔNICO HC-SR04 /////
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // Tempo do eco em microssegundos (timeout 30 ms)
  float distance = -1;
  if (duration == 0) {
    Serial.println("HC-SR04  Falha de leitura (sem eco).");
  } else {
    distance = duration * 0.0343f / 2.0f;   // Conversão tempo->distância em cm (velocidade do som aproximada)
    Serial.print("HC-SR04  Dist: "); Serial.print(distance, 1); Serial.println(" cm");
  }

  ///// LEITURA DO SENSOR DE UMIDADE DO SOLO HL-69 /////
  int hl_raw = analogRead(HL69_PIN);                         // Valor analógico bruto do HL-69
  float soil_pct = mapPercent(hl_raw, HL69_DRY_RAW, HL69_WET_RAW); // Converte para porcentagem (0–100 %)
  Serial.print("HL-69    Bruto: "); Serial.print(hl_raw);
  Serial.print("  |  Solo: "); Serial.print(soil_pct, 1); Serial.println(" %");

  // NEW: Atualiza NTP e monta timestamp ISO
  timeClient.update();
  String ts = formatIsoTimestamp(timeClient.getEpochTime());
  Serial.print("Timestamp ISO: "); Serial.println(ts);

  // NEW: Envia dados para API
  bool sent = sendSensorData(SERVER_URL, DEVICE_ID, ts,
                             last_ds_temp, tDHT, hum, distance,
                             hl_raw, soil_pct);
  if (sent) {
    Serial.println("Dados enviados com sucesso para a API.");
  } else {
    Serial.println("Falha ao enviar dados para a API.");
  }
}