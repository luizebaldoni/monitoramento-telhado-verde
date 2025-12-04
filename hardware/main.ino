/*

 * ENVIO DE DADOS DE SENSORES DO TELHADO VERDE PARA API FASTAPI (ESP32)

 * Autor: equipe de hardware Grupo 5 Projeto Integrador em Engenharia de Computação
*  Engenharia de Computação – UFSM
* Contato: grupo5.projeto.telhado.verde@gmail.com
 * Data de conclusao: 03/12/2025
 *
 * DESCRIÇÃO:
 * - Código para leitura de múltiplos sensores conectados a um ESP32 em um sistema de telhado verde inteligente.
 * - Coleta dados de:
 *   - DS18B20: temperatura do solo via barramento OneWire.
 *   - DHT11: temperatura e umidade do ar.
 *   - HC-SR04: distância (ex.: nível de reservatório ou altura da lâmina d’água).
 *   - HL-69: umidade do solo em forma de porcentagem a partir de leitura analógica.
 * - Obtém o horário atual via NTP (servidor pool.ntp.org) para gerar timestamp no formato ISO 8601.
 * - Monta um JSON com os dados dos sensores e metadados do dispositivo e envia via HTTP POST
 *   para uma API FastAPI exposta por Nginx na rota /api-fast/sensor-data.
 *
 * REQUISITOS:
 * - Hardware:
 *   - Placa ESP32 com Wi-Fi integrado.
 *   - Sensor DS18B20 (temperatura do solo) com resistor de pull-up adequado no barramento OneWire. [web:21][web:22]
 *   - Sensor DHT11 (temperatura/umidade do ar).
 *   - Sensor ultrassônico HC-SR04 (pinos TRIG/ECHO compatíveis com ESP32).
 *   - Sensor de umidade do solo HL-69 conectado a entrada analógica (HL69_PIN).
 *   - Fonte de alimentação estável compatível com o ESP32 e todos os sensores.
 * - Software:
 *   - Arduino IDE (ou plataforma compatível) com suporte para ESP32 configurado.
 *   - Bibliotecas instaladas:
 *     - WiFi.h e HTTPClient.h para conexão de rede e requisições HTTP. [web:22][web:27][web:38]
 *     - ArduinoJson para montagem e serialização do objeto JSON enviado na requisição POST. [web:21][web:23][web:32]
 *     - OneWire e DallasTemperature para comunicação e leitura do sensor DS18B20. [web:21]
 *     - DHT (Adafruit DHT) para leitura de temperatura e umidade do DHT11.
 *     - NTPClient e WiFiUdp para sincronização de horário com servidor NTP e obtenção de epoch time. [web:26][web:28][web:30]
 *   - Servidor de backend com FastAPI publicado atrás de Nginx, aceitando requisições HTTP POST em:
 *     - URL base configurada em SERVER_URL (ex.: http://10.5.1.100/api-fast/sensor-data), com corpo JSON compatível com o esperado pela API.
 * - Observações:
 *   - As credenciais de Wi-Fi (ssid e password) devem ser configuradas antes da gravação no dispositivo.
 *   - Os valores HL69_DRY_RAW e HL69_WET_RAW precisam ser ajustados por calibração prática em solo seco e úmido
 *     para que o cálculo de porcentagem de umidade represente corretamente a condição real. [web:10][web:13][web:31]
 *   - O intervalo de envio de dados é definido em READ_INTERVAL_MS (30 segundos), evitando requisições excessivas
 *     e reduzindo consumo de energia e carga no servidor.

 */


/////// INCLUSÃO DE BIBLIOTECAS //////

#include <WiFi.h>          // Gerenciamento de conexão Wi-Fi no ESP32
#include <HTTPClient.h>    // Cliente HTTP para requisições GET/POST
#include <ArduinoJson.h>   // Montagem e serialização de JSON
#include <OneWire.h>       // Protocolo OneWire (DS18B20)
#include <DallasTemperature.h> // Leitura de sensores DS18B20
#include "DHT.h"           // Biblioteca para sensor DHT (DHT11)
#include <NTPClient.h>     // Cliente NTP para horário de rede
#include <WiFiUdp.h>       // UDP para comunicação com servidor NTP


/////// CONFIGURAÇÕES DE REDE //////

//& SSID e senha da rede Wi-Fi à qual o ESP32 deve se conectar
const char* ssid     = "SSID";        // <-- TROCAR: nome da rede Wi-Fi
const char* password = "PASSWORD";   // <-- TROCAR: senha da rede Wi-Fi

//& URL da API FastAPI acessada via Nginx (rota /api-fast/sensor-data)
const char* SERVER_URL = "http://10.5.1.100/api-fast/sensor-data";

//& Identificador lógico deste dispositivo (usado no JSON enviado)
const char* DEVICE_ID = "ESP32_TELHADO_VERDE";


/////// CONFIGURAÇÃO NTP (DATA/HORA) //////

//& Cliente UDP e cliente NTP para obter horário atual (UTC-3) de pool.ntp.org
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -3 * 3600, 60 * 1000); // Fuso UTC-3, atualiza a cada 60 s

//& Converte epoch time (segundos desde 1970) em string no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
String formatIsoTimestamp(unsigned long epoch) {
  struct tm timeinfo;
  gmtime_r((time_t*)&epoch, &timeinfo);
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
}


/////// CONFIGURAÇÃO DOS SENSORES //////

//& DS18B20 – sensor de temperatura do solo via OneWire
#define ONE_WIRE_BUS  2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);
DeviceAddress dsAddr;         // Endereço do primeiro sensor DS18B20
float last_ds_temp = NAN;     // Armazena última leitura válida (opcional)

//& DHT11 – sensor de temperatura e umidade do ar
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//& HC-SR04 – sensor ultrassônico de distância
#define TRIG_PIN 12
#define ECHO_PIN 14

//& HL-69 – sensor resistivo de umidade do solo (saída analógica)
#define HL69_PIN  34
// Valores de calibração (ajustar conforme medições em solo seco e solo úmido)
#define HL69_DRY_RAW  3500   // valor analógico aproximado solo seco
#define HL69_WET_RAW  1200   // valor analógico aproximado solo molhado


//& Converte leitura analógica bruta do HL-69 em porcentagem de umidade (0–100 %)
float mapPercent(int raw, int dryRaw, int wetRaw) {
  float pct = (float)(dryRaw - raw) * 100.0 / (float)(dryRaw - wetRaw);
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return pct;
}


/////// FUNÇÃO DE ENVIO DE DADOS PARA API //////

//& Monta o JSON com leituras de sensores e envia via HTTP POST para a API configurada
bool sendSensorData(
  const char* serverUrl,
  const char* deviceId,
  const String& timestamp,
  float ds_temp,
  float dht_temp,
  float dht_hum,
  float hcsr_dist,
  int hl_raw,
  float hl_pct
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi não conectado, não foi possível enviar.");
    return false;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json"); // cabeçalho para JSON

  //& Documento JSON no formato esperado pela API (ex.: modelo DadosSensor)
  StaticJsonDocument<1024> doc;

  doc["device_id"] = deviceId;
  doc["timestamp"] = timestamp;

  JsonObject sensors = doc.createNestedObject("sensors");

  //& Bloco de dados do sensor DS18B20
  JsonObject ds18 = sensors.createNestedObject("ds18b20");
  ds18["temperature"] = isnan(ds_temp) ? 0.0 : ds_temp;   // não envia null
  ds18["unit"] = "celsius";
  ds18["status"] = isnan(ds_temp) ? "error" : "ok";

  //& Bloco de dados do sensor DHT11
  JsonObject dht = sensors.createNestedObject("dht11");
  dht["temperature"] = isnan(dht_temp) ? 0.0 : dht_temp;  // não envia null
  dht["humidity"]   = isnan(dht_hum)  ? 0.0 : dht_hum;    // não envia null
  dht["unit_temp"] = "celsius";
  dht["unit_humidity"] = "percent";
  dht["status"] = (isnan(dht_temp) || isnan(dht_hum)) ? "error" : "ok";

  //& Bloco de dados do sensor HC-SR04
  JsonObject hcsr = sensors.createNestedObject("hcsr04");
  hcsr["distance"] = hcsr_dist;
  hcsr["unit"] = "cm";
  hcsr["status"] = (hcsr_dist <= 0) ? "error" : "ok";

  //& Bloco de dados do sensor HL-69
  JsonObject hl = sensors.createNestedObject("hl69");
  hl["soil_moisture"] = hl_pct;
  hl["raw_value"] = hl_raw;
  hl["unit"] = "percent";
  hl["status"] = "ok";

  //& Serializa o documento JSON para string a ser enviada no corpo da requisição
  String payload;
  serializeJson(doc, payload);

  Serial.println("Enviando para API:");
  Serial.println(payload);

  int httpCode = http.POST(payload); // envia POST com corpo JSON

  if (httpCode > 0) {
    Serial.print("HTTP POST code: ");
    Serial.println(httpCode);
    String resp = http.getString();
    Serial.print("Resposta: ");
    Serial.println(resp);
    http.end();
    return (httpCode >= 200 && httpCode < 300); // considera sucesso códigos 2xx
  } else {
    Serial.print("Falha POST: ");
    Serial.println(http.errorToString(httpCode));
    http.end();
    return false;
  }
}


/////// CONFIGURAÇÕES INICIAIS //////

unsigned long lastRead = 0;                         // último instante de leitura
const unsigned long READ_INTERVAL_MS = 30 * 1000;   // intervalo entre leituras (30 s)


void setup() {
  Serial.begin(115200);
  delay(200);

  //& Conexão Wi-Fi
  Serial.print("Conectando em WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi conectado. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("AVISO: não conectou ao WiFi no tempo limite.");
  }

  //& Inicialização do cliente NTP para obter data/hora de rede
  timeClient.begin();
  timeClient.update();

  //& Inicialização do sensor DS18B20
  ds18b20.begin();
  if (ds18b20.getAddress(dsAddr, 0)) {
    ds18b20.setResolution(dsAddr, 12);  // resolução máxima (12 bits)
    Serial.println("DS18B20 inicializado.");
  } else {
    Serial.println("ATENÇÃO: nenhum DS18B20 encontrado.");
  }

  //& Inicialização do sensor DHT11
  dht.begin();
  Serial.println("DHT11 inicializado.");

  //& Configuração dos pinos do HC-SR04
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("HC-SR04 inicializado.");

  //& Configuração do sensor HL-69
  pinMode(HL69_PIN, INPUT);
#ifdef ARDUINO_ARCH_ESP32
  analogSetPinAttenuation(HL69_PIN, ADC_11db);  // melhora faixa de leitura no ADC do ESP32
#endif
  Serial.println("HL-69 inicializado.");
}


/////// LOOP PRINCIPAL //////

void loop() {
  unsigned long now = millis();
  if (now - lastRead < READ_INTERVAL_MS) return;  // respeita intervalo entre amostragens
  lastRead = now;

  Serial.println();
  Serial.println("===== NOVA LEITURA =====");

  //& Leitura DS18B20 (temperatura do solo)
  ds18b20.requestTemperatures();
  float ds_temp = NAN;
  if (ds18b20.getAddress(dsAddr, 0)) {
    ds_temp = ds18b20.getTempC(dsAddr);
    if (ds_temp != DEVICE_DISCONNECTED_C) {
      Serial.print("DS18B20 Temp solo: ");
      Serial.print(ds_temp);
      Serial.println(" °C");
    } else {
      Serial.println("DS18B20 ERRO (-127 °C)");
    }
  }

  //& Leitura DHT11 (temperatura e umidade do ar)
  float hum  = dht.readHumidity();
  float tDHT = dht.readTemperature();
  if (!isnan(hum) && !isnan(tDHT)) {
    Serial.print("DHT11 Temp ar: ");
    Serial.print(tDHT);
    Serial.print(" °C | Umidade: ");
    Serial.print(hum);
    Serial.println(" %");
  } else {
    Serial.println("DHT11 falha de leitura.");
  }

  //& Leitura HC-SR04 (distância em cm)
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30 ms para eco
  float distance = -1;
  if (duration == 0) {
    Serial.println("HC-SR04 falha (sem eco).");
  } else {
    distance = duration * 0.0343f / 2.0f;  // conversão para cm
    Serial.print("HC-SR04 Dist: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  //& Leitura HL-69 (umidade do solo)
  int hl_raw = analogRead(HL69_PIN);                             // valor analógico bruto
  float soil_pct = mapPercent(hl_raw, HL69_DRY_RAW, HL69_WET_RAW); // umidade em %
  Serial.print("HL-69 Bruto: ");
  Serial.print(hl_raw);
  Serial.print(" | Solo: ");
  Serial.print(soil_pct);
  Serial.println(" %");

  //& Obtém timestamp atual via NTP e formata em ISO 8601
  timeClient.update();
  String ts = formatIsoTimestamp(timeClient.getEpochTime());
  Serial.print("Timestamp ISO: ");
  Serial.println(ts);

  //& Envia os dados coletados para a API FastAPI via HTTP POST
  bool sent = sendSensorData(
    SERVER_URL,
    DEVICE_ID,
    ts,
    ds_temp,
    tDHT,
    hum,
    distance,
    hl_raw,
    soil_pct
  );

  if (sent) {
    Serial.println("Dados enviados com sucesso para a API.");
  } else {
    Serial.println("Falha ao enviar dados para a API.");
  }
}
/*

 * ENVIO DE DADOS DE SENSORES DO TELHADO VERDE PARA API FASTAPI (ESP32)

 * Autor: equipe de hardware Grupo 5 Projeto Integrador em Engenharia de Computação
*  Engenharia de Computação – UFSM
* Contato: grupo5.projeto.telhado.verde@gmail.com
 * Data de conclusao: 03/12/2025
 *
 * DESCRIÇÃO:
 * - Código para leitura de múltiplos sensores conectados a um ESP32 em um sistema de telhado verde inteligente.
 * - Coleta dados de:
 *   - DS18B20: temperatura do solo via barramento OneWire.
 *   - DHT11: temperatura e umidade do ar.
 *   - HC-SR04: distância (ex.: nível de reservatório ou altura da lâmina d’água).
 *   - HL-69: umidade do solo em forma de porcentagem a partir de leitura analógica.
 * - Obtém o horário atual via NTP (servidor pool.ntp.org) para gerar timestamp no formato ISO 8601.
 * - Monta um JSON com os dados dos sensores e metadados do dispositivo e envia via HTTP POST
 *   para uma API FastAPI exposta por Nginx na rota /api-fast/sensor-data.
 *
 * REQUISITOS:
 * - Hardware:
 *   - Placa ESP32 com Wi-Fi integrado.
 *   - Sensor DS18B20 (temperatura do solo) com resistor de pull-up adequado no barramento OneWire. [web:21][web:22]
 *   - Sensor DHT11 (temperatura/umidade do ar).
 *   - Sensor ultrassônico HC-SR04 (pinos TRIG/ECHO compatíveis com ESP32).
 *   - Sensor de umidade do solo HL-69 conectado a entrada analógica (HL69_PIN).
 *   - Fonte de alimentação estável compatível com o ESP32 e todos os sensores.
 * - Software:
 *   - Arduino IDE (ou plataforma compatível) com suporte para ESP32 configurado.
 *   - Bibliotecas instaladas:
 *     - WiFi.h e HTTPClient.h para conexão de rede e requisições HTTP. [web:22][web:27][web:38]
 *     - ArduinoJson para montagem e serialização do objeto JSON enviado na requisição POST. [web:21][web:23][web:32]
 *     - OneWire e DallasTemperature para comunicação e leitura do sensor DS18B20. [web:21]
 *     - DHT (Adafruit DHT) para leitura de temperatura e umidade do DHT11.
 *     - NTPClient e WiFiUdp para sincronização de horário com servidor NTP e obtenção de epoch time. [web:26][web:28][web:30]
 *   - Servidor de backend com FastAPI publicado atrás de Nginx, aceitando requisições HTTP POST em:
 *     - URL base configurada em SERVER_URL (ex.: http://10.5.1.100/api-fast/sensor-data), com corpo JSON compatível com o esperado pela API.
 * - Observações:
 *   - As credenciais de Wi-Fi (ssid e password) devem ser configuradas antes da gravação no dispositivo.
 *   - Os valores HL69_DRY_RAW e HL69_WET_RAW precisam ser ajustados por calibração prática em solo seco e úmido
 *     para que o cálculo de porcentagem de umidade represente corretamente a condição real. [web:10][web:13][web:31]
 *   - O intervalo de envio de dados é definido em READ_INTERVAL_MS (30 segundos), evitando requisições excessivas
 *     e reduzindo consumo de energia e carga no servidor.

 */


/////// INCLUSÃO DE BIBLIOTECAS //////

#include <WiFi.h>          // Gerenciamento de conexão Wi-Fi no ESP32
#include <HTTPClient.h>    // Cliente HTTP para requisições GET/POST
#include <ArduinoJson.h>   // Montagem e serialização de JSON
#include <OneWire.h>       // Protocolo OneWire (DS18B20)
#include <DallasTemperature.h> // Leitura de sensores DS18B20
#include "DHT.h"           // Biblioteca para sensor DHT (DHT11)
#include <NTPClient.h>     // Cliente NTP para horário de rede
#include <WiFiUdp.h>       // UDP para comunicação com servidor NTP


/////// CONFIGURAÇÕES DE REDE //////

//& SSID e senha da rede Wi-Fi à qual o ESP32 deve se conectar
const char* ssid     = "SSID";        // <-- TROCAR: nome da rede Wi-Fi
const char* password = "PASSWORD";   // <-- TROCAR: senha da rede Wi-Fi

//& URL da API FastAPI acessada via Nginx (rota /api-fast/sensor-data)
const char* SERVER_URL = "http://10.5.1.100/api-fast/sensor-data";

//& Identificador lógico deste dispositivo (usado no JSON enviado)
const char* DEVICE_ID = "ESP32_TELHADO_VERDE";


/////// CONFIGURAÇÃO NTP (DATA/HORA) //////

//& Cliente UDP e cliente NTP para obter horário atual (UTC-3) de pool.ntp.org
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -3 * 3600, 60 * 1000); // Fuso UTC-3, atualiza a cada 60 s

//& Converte epoch time (segundos desde 1970) em string no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
String formatIsoTimestamp(unsigned long epoch) {
  struct tm timeinfo;
  gmtime_r((time_t*)&epoch, &timeinfo);
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
}


/////// CONFIGURAÇÃO DOS SENSORES //////

//& DS18B20 – sensor de temperatura do solo via OneWire
#define ONE_WIRE_BUS  2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);
DeviceAddress dsAddr;         // Endereço do primeiro sensor DS18B20
float last_ds_temp = NAN;     // Armazena última leitura válida (opcional)

//& DHT11 – sensor de temperatura e umidade do ar
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//& HC-SR04 – sensor ultrassônico de distância
#define TRIG_PIN 12
#define ECHO_PIN 14

//& HL-69 – sensor resistivo de umidade do solo (saída analógica)
#define HL69_PIN  34
// Valores de calibração (ajustar conforme medições em solo seco e solo úmido)
#define HL69_DRY_RAW  3500   // valor analógico aproximado solo seco
#define HL69_WET_RAW  1200   // valor analógico aproximado solo molhado


//& Converte leitura analógica bruta do HL-69 em porcentagem de umidade (0–100 %)
float mapPercent(int raw, int dryRaw, int wetRaw) {
  float pct = (float)(dryRaw - raw) * 100.0 / (float)(dryRaw - wetRaw);
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return pct;
}


/////// FUNÇÃO DE ENVIO DE DADOS PARA API //////

//& Monta o JSON com leituras de sensores e envia via HTTP POST para a API configurada
bool sendSensorData(
  const char* serverUrl,
  const char* deviceId,
  const String& timestamp,
  float ds_temp,
  float dht_temp,
  float dht_hum,
  float hcsr_dist,
  int hl_raw,
  float hl_pct
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi não conectado, não foi possível enviar.");
    return false;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json"); // cabeçalho para JSON

  //& Documento JSON no formato esperado pela API (ex.: modelo DadosSensor)
  StaticJsonDocument<1024> doc;

  doc["device_id"] = deviceId;
  doc["timestamp"] = timestamp;

  JsonObject sensors = doc.createNestedObject("sensors");

  //& Bloco de dados do sensor DS18B20
  JsonObject ds18 = sensors.createNestedObject("ds18b20");
  ds18["temperature"] = isnan(ds_temp) ? 0.0 : ds_temp;   // não envia null
  ds18["unit"] = "celsius";
  ds18["status"] = isnan(ds_temp) ? "error" : "ok";

  //& Bloco de dados do sensor DHT11
  JsonObject dht = sensors.createNestedObject("dht11");
  dht["temperature"] = isnan(dht_temp) ? 0.0 : dht_temp;  // não envia null
  dht["humidity"]   = isnan(dht_hum)  ? 0.0 : dht_hum;    // não envia null
  dht["unit_temp"] = "celsius";
  dht["unit_humidity"] = "percent";
  dht["status"] = (isnan(dht_temp) || isnan(dht_hum)) ? "error" : "ok";

  //& Bloco de dados do sensor HC-SR04
  JsonObject hcsr = sensors.createNestedObject("hcsr04");
  hcsr["distance"] = hcsr_dist;
  hcsr["unit"] = "cm";
  hcsr["status"] = (hcsr_dist <= 0) ? "error" : "ok";

  //& Bloco de dados do sensor HL-69
  JsonObject hl = sensors.createNestedObject("hl69");
  hl["soil_moisture"] = hl_pct;
  hl["raw_value"] = hl_raw;
  hl["unit"] = "percent";
  hl["status"] = "ok";

  //& Serializa o documento JSON para string a ser enviada no corpo da requisição
  String payload;
  serializeJson(doc, payload);

  Serial.println("Enviando para API:");
  Serial.println(payload);

  int httpCode = http.POST(payload); // envia POST com corpo JSON

  if (httpCode > 0) {
    Serial.print("HTTP POST code: ");
    Serial.println(httpCode);
    String resp = http.getString();
    Serial.print("Resposta: ");
    Serial.println(resp);
    http.end();
    return (httpCode >= 200 && httpCode < 300); // considera sucesso códigos 2xx
  } else {
    Serial.print("Falha POST: ");
    Serial.println(http.errorToString(httpCode));
    http.end();
    return false;
  }
}


/////// CONFIGURAÇÕES INICIAIS //////

unsigned long lastRead = 0;                         // último instante de leitura
const unsigned long READ_INTERVAL_MS = 30 * 1000;   // intervalo entre leituras (30 s)


void setup() {
  Serial.begin(115200);
  delay(200);

  //& Conexão Wi-Fi
  Serial.print("Conectando em WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi conectado. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("AVISO: não conectou ao WiFi no tempo limite.");
  }

  //& Inicialização do cliente NTP para obter data/hora de rede
  timeClient.begin();
  timeClient.update();

  //& Inicialização do sensor DS18B20
  ds18b20.begin();
  if (ds18b20.getAddress(dsAddr, 0)) {
    ds18b20.setResolution(dsAddr, 12);  // resolução máxima (12 bits)
    Serial.println("DS18B20 inicializado.");
  } else {
    Serial.println("ATENÇÃO: nenhum DS18B20 encontrado.");
  }

  //& Inicialização do sensor DHT11
  dht.begin();
  Serial.println("DHT11 inicializado.");

  //& Configuração dos pinos do HC-SR04
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("HC-SR04 inicializado.");

  //& Configuração do sensor HL-69
  pinMode(HL69_PIN, INPUT);
#ifdef ARDUINO_ARCH_ESP32
  analogSetPinAttenuation(HL69_PIN, ADC_11db);  // melhora faixa de leitura no ADC do ESP32
#endif
  Serial.println("HL-69 inicializado.");
}


/////// LOOP PRINCIPAL //////

void loop() {
  unsigned long now = millis();
  if (now - lastRead < READ_INTERVAL_MS) return;  // respeita intervalo entre amostragens
  lastRead = now;

  Serial.println();
  Serial.println("===== NOVA LEITURA =====");

  //& Leitura DS18B20 (temperatura do solo)
  ds18b20.requestTemperatures();
  float ds_temp = NAN;
  if (ds18b20.getAddress(dsAddr, 0)) {
    ds_temp = ds18b20.getTempC(dsAddr);
    if (ds_temp != DEVICE_DISCONNECTED_C) {
      Serial.print("DS18B20 Temp solo: ");
      Serial.print(ds_temp);
      Serial.println(" °C");
    } else {
      Serial.println("DS18B20 ERRO (-127 °C)");
    }
  }

  //& Leitura DHT11 (temperatura e umidade do ar)
  float hum  = dht.readHumidity();
  float tDHT = dht.readTemperature();
  if (!isnan(hum) && !isnan(tDHT)) {
    Serial.print("DHT11 Temp ar: ");
    Serial.print(tDHT);
    Serial.print(" °C | Umidade: ");
    Serial.print(hum);
    Serial.println(" %");
  } else {
    Serial.println("DHT11 falha de leitura.");
  }

  //& Leitura HC-SR04 (distância em cm)
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30 ms para eco
  float distance = -1;
  if (duration == 0) {
    Serial.println("HC-SR04 falha (sem eco).");
  } else {
    distance = duration * 0.0343f / 2.0f;  // conversão para cm
    Serial.print("HC-SR04 Dist: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  //& Leitura HL-69 (umidade do solo)
  int hl_raw = analogRead(HL69_PIN);                             // valor analógico bruto
  float soil_pct = mapPercent(hl_raw, HL69_DRY_RAW, HL69_WET_RAW); // umidade em %
  Serial.print("HL-69 Bruto: ");
  Serial.print(hl_raw);
  Serial.print(" | Solo: ");
  Serial.print(soil_pct);
  Serial.println(" %");

  //& Obtém timestamp atual via NTP e formata em ISO 8601
  timeClient.update();
  String ts = formatIsoTimestamp(timeClient.getEpochTime());
  Serial.print("Timestamp ISO: ");
  Serial.println(ts);

  //& Envia os dados coletados para a API FastAPI via HTTP POST
  bool sent = sendSensorData(
    SERVER_URL,
    DEVICE_ID,
    ts,
    ds_temp,
    tDHT,
    hum,
    distance,
    hl_raw,
    soil_pct
  );

  if (sent) {
    Serial.println("Dados enviados com sucesso para a API.");
  } else {
    Serial.println("Falha ao enviar dados para a API.");
  }
}
