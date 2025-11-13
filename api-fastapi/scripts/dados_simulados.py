"""
DADOS SIMULADOS - 30 LEITURAS DE SENSORES
Sistema de Monitoramento de Telhado Verde

Este arquivo contém 30 leituras simuladas representando diferentes condições
climáticas e estados do telhado verde ao longo de um período.

Cenários simulados:
- Leituras 1-10: Após chuva (solo úmido, temperaturas amenas)
- Leituras 11-20: Período seco (solo seco, temperaturas mais altas)
- Leituras 21-30: Transição (variações graduais)

Autor: Equipe Projeto Integrador 4 - UFSM
"""

from datetime import datetime

# ========================================
# 30 LEITURAS SIMULADAS
# ========================================

LEITURAS_SIMULADAS = [
    # ==================== APÓS CHUVA (1-10) ====================
    # Solo úmido, temperaturas amenas, reservatório cheio
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 22.3, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 25.8, "humidity": 72.3, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 15.7, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 68.4, "raw_value": 2380, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 22.1, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 25.5, "humidity": 73.8, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 14.9, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 70.2, "raw_value": 2420, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 21.8, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 24.9, "humidity": 75.1, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 14.5, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 72.5, "raw_value": 2480, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 22.5, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 26.2, "humidity": 71.4, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 15.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 69.8, "raw_value": 2400, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 23.1, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 26.8, "humidity": 70.2, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 15.8, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 67.3, "raw_value": 2350, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 22.7, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 25.9, "humidity": 72.9, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 16.1, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 66.1, "raw_value": 2310, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 23.4, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 27.1, "humidity": 68.7, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 16.5, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 64.5, "raw_value": 2270, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 23.8, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 27.5, "humidity": 67.3, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 17.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 62.8, "raw_value": 2230, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 24.2, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 28.1, "humidity": 65.9, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 17.8, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 61.2, "raw_value": 2190, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 24.6, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 28.7, "humidity": 64.5, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 18.4, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 59.7, "raw_value": 2150, "unit": "percent", "status": "ok"}
        }
    },
    
    # ==================== PERÍODO SECO (11-20) ====================
    # Solo seco, temperaturas altas, reservatório vazio
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 25.3, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 29.5, "humidity": 58.2, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 22.1, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 48.3, "raw_value": 1820, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 26.1, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 30.2, "humidity": 55.7, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 23.5, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 45.6, "raw_value": 1750, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 26.8, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 31.1, "humidity": 52.3, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 25.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 42.1, "raw_value": 1680, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 27.5, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 32.4, "humidity": 49.8, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 26.7, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 39.4, "raw_value": 1610, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 28.2, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 33.1, "humidity": 47.2, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 28.3, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 36.8, "raw_value": 1540, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 28.9, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 34.2, "humidity": 44.6, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 29.8, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 34.2, "raw_value": 1470, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 29.3, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 34.8, "humidity": 42.1, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 31.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 31.7, "raw_value": 1400, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 29.8, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 35.5, "humidity": 39.8, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 32.6, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 29.3, "raw_value": 1330, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 30.1, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 36.1, "humidity": 37.5, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 33.9, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 27.1, "raw_value": 1260, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 30.5, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 36.7, "humidity": 35.3, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 35.1, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 25.2, "raw_value": 1190, "unit": "percent", "status": "ok"}
        }
    },
    
    # ==================== TRANSIÇÃO - RECUPERAÇÃO (21-30) ====================
    # Chuva voltando, solo se recuperando, temperaturas normalizando
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 29.8, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 35.2, "humidity": 38.7, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 33.5, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 28.4, "raw_value": 1240, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 28.5, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 33.1, "humidity": 43.2, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 30.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 32.8, "raw_value": 1420, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 27.1, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 30.8, "humidity": 48.9, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 26.8, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 37.6, "raw_value": 1580, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 25.7, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 28.4, "humidity": 54.5, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 23.1, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 42.9, "raw_value": 1740, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 24.3, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 26.9, "humidity": 60.3, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 19.7, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 48.7, "raw_value": 1900, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 23.2, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 25.6, "humidity": 65.8, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 17.3, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 54.2, "raw_value": 2050, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 22.4, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 24.8, "humidity": 70.4, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 15.9, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 59.6, "raw_value": 2190, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 21.9, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 24.1, "humidity": 74.2, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 14.8, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 64.8, "raw_value": 2320, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 21.5, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 23.7, "humidity": 77.1, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 13.9, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 69.3, "raw_value": 2430, "unit": "percent", "status": "ok"}
        }
    },
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": datetime.now().isoformat(),
        "sensors": {
            "ds18b20": {"temperature": 21.2, "unit": "celsius", "status": "ok"},
            "dht11": {"temperature": 23.4, "humidity": 79.5, "unit_temp": "celsius", "unit_humidity": "percent", "status": "ok"},
            "hcsr04": {"distance": 13.2, "unit": "cm", "status": "ok"},
            "hl69": {"soil_moisture": 73.1, "raw_value": 2510, "unit": "percent", "status": "ok"}
        }
    }
]
