"""
API FastAPI com Firebase Firestore
Sistema de Monitoramento do Telhado Verde - UFSM

Este módulo implementa uma API REST para receber, validar e armazenar
dados de sensores IoT de um sistema de telhado verde.

Autor: Equipe Projeto Integrador 4 - UFSM
Data: 2025
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# ========================================
# CONFIGURAÇÃO INICIAL
# ========================================

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a aplicação FastAPI com título personalizado
app = FastAPI(
    title="API Telhado Verde",
    description="Sistema de monitoramento IoT para telhado verde com ESP32 e Firebase",
    version="1.0.0"
)

# Variável global para conexão com Firebase (inicializada no startup)
db = None

# ========================================
# MODELOS DE DADOS (Pydantic)
# ========================================
# Define a estrutura esperada dos dados JSON recebidos do ESP32

class SensorDS18B20(BaseModel):
    """
    Modelo para sensor de temperatura do solo DS18B20
    - Sensor digital de temperatura
    - Precisão: ±0.5°C
    """
    temperature: float  # Temperatura em graus Celsius
    unit: str = "celsius"  # Unidade de medida
    status: str = "ok"  # Status do sensor (ok, warning, error)


class SensorDHT11(BaseModel):
    """
    Modelo para sensor de temperatura e umidade DHT11
    - Sensor digital para ambiente
    - Temperatura: -40°C a 80°C
    - Umidade: 0% a 100%
    """
    temperature: float  # Temperatura do ar em Celsius
    humidity: float  # Umidade relativa do ar em %
    unit_temp: str = "celsius"
    unit_humidity: str = "percent"
    status: str = "ok"

class SensorHCSR04(BaseModel):
    """
    Modelo para sensor ultrassônico HC-SR04
    - Medição de distância por ultrassom
    - Usado para medir nível de água no reservatório
    - Alcance: 2cm a 400cm
    """
    distance: float  # Distância em centímetros
    unit: str = "cm"
    status: str = "ok"


class SensorHL69(BaseModel):
    """
    Modelo para sensor de umidade do solo HL-69
    - Sensor analógico resistivo
    - Mede umidade do solo
    """
    soil_moisture: float  # Umidade do solo em %
    raw_value: int  # Valor bruto analógico (0-4095)
    unit: str = "percent"
    status: str = "ok"


class Sensors(BaseModel):
    """
    Conjunto completo de todos os sensores do sistema
    Agrupa todas as leituras em uma única estrutura
    """
    ds18b20: SensorDS18B20
    dht11: SensorDHT11
    hcsr04: SensorHCSR04
    hl69: SensorHL69


class DadosSensor(BaseModel):
    """
    Modelo principal de dados enviados pelo ESP32
    
    Estrutura do JSON esperado:
    {
        "device_id": "ESP32_TELHADO_VERDE",
        "timestamp": "2025-11-12T14:30:00",
        "sensors": { ... }
    }
    """
    device_id: str  # Identificador único do dispositivo ESP32
    timestamp: str  # Timestamp da coleta (ISO 8601)
    sensors: Sensors  # Dados de todos os sensores


# ========================================
# INICIALIZAÇÃO DO FIREBASE
# ========================================

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da API
    
    Responsável por:
    1. Carregar credenciais do Firebase
    2. Inicializar conexão com Firestore
    3. Configurar cliente do banco de dados
    
    Raises:
        Exception: Se houver erro na conexão (API continua funcionando)
    """
    global db
    
    try:
        # Obtém o caminho das credenciais do arquivo .env
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase-credentials.json")
        
        # Verifica se o arquivo de credenciais existe
        if not os.path.exists(cred_path):
            print(f"AVISO: Arquivo de credenciais não encontrado: {cred_path}")
            print(f"A API funcionará, mas sem salvar no Firebase!")
            print(f"Siga o guia docs/GUIA_RAPIDO.md para configurar")
            return
        
        # Inicializa o Firebase Admin SDK
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        
        # Cria cliente do Firestore
        db = firestore.client()
        
        print("=" * 60)
        print("🔥 Firebase Firestore conectado com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro ao conectar Firebase: {str(e)}")
        print(f"A API funcionará sem Firebase")

# ========================================
# ENDPOINTS DA API
# ========================================

@app.get("/", tags=["Status"])
def health_check():
    """
    Endpoint raiz - Health check e informações da API
    
    Returns:
        dict: Status da API e lista de endpoints disponíveis
        
    Example:
        GET http://localhost:8000/
    """
    firebase_status = "✅ Conectado" if db else "⚠️ Não configurado"
    
    return {
        "mensagem": "API Telhado Verde funcionando! 🌱",
        "firebase": firebase_status,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "enviar_dados": "POST /sensor-data",
            "consultar_dados": "GET /sensor-data",
            "documentacao_swagger": "/docs",
            "documentacao_redoc": "/redoc"
        }
    }


@app.post("/sensor-data", tags=["Sensores"])
def receber_dados(dados: DadosSensor):
    """
    Recebe dados dos sensores enviados pelo ESP32
    
    Este endpoint:
    1. Recebe o JSON com dados dos sensores
    2. Valida a estrutura usando Pydantic
    3. Adiciona timestamp de recebimento
    4. Salva no Firebase Firestore
    
    Args:
        dados (DadosSensor): Dados dos sensores no formato JSON
        
    Returns:
        dict: Confirmação do salvamento e IDs gerados
        
    Raises:
        HTTPException 503: Se Firebase não estiver configurado
        HTTPException 500: Se houver erro ao salvar
        
    Example:
        POST http://localhost:8000/sensor-data
        Body: { "device_id": "ESP32_001", ... }
    """
    
    # Verifica se o Firebase está configurado
    if not db:
        raise HTTPException(
            status_code=503,
            detail="Firebase não configurado. Configure as credenciais primeiro. Veja docs/GUIA_RAPIDO.md"
        )
    
    try:
        # Prepara os dados para salvar no Firestore
        dados_para_salvar = {
            "device_id": dados.device_id,
            "timestamp": dados.timestamp,  # Timestamp do ESP32
            "timestamp_recebido": datetime.now().isoformat(),  # Timestamp do servidor
            "sensors": dados.sensors.model_dump()  # Converte Pydantic para dict
        }
        
        # Salva no Firestore (coleção: sensor_readings)
        doc_ref = db.collection('sensor_readings').add(dados_para_salvar)
        
        # Log no console
        print(f"Dados salvos no Firebase!")
        print(f"Document ID: {doc_ref[1].id}")
        print(f"Device: {dados.device_id}")
        
        return {
            "mensagem": "Dados recebidos e salvos no Firebase!",
            "device_id": dados.device_id,
            "firestore_id": doc_ref[1].id,
            "timestamp_recebido": dados_para_salvar["timestamp_recebido"],
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar no Firebase: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar dados: {str(e)}"
        )


@app.get("/sensor-data", tags=["Sensores"])
def ver_dados(limit: int = 10, device_id: str = None):
    """
    Consulta dados armazenados no Firebase
    
    Permite filtrar e limitar os resultados retornados.
    Os dados são ordenados do mais recente para o mais antigo.
    
    Args:
        limit (int): Número máximo de registros a retornar (padrão: 10)
        device_id (str, optional): Filtrar por ID do dispositivo
        
    Returns:
        dict: Lista de leituras e total de registros
        
    Raises:
        HTTPException 503: Se Firebase não estiver configurado
        HTTPException 500: Se houver erro na consulta
        
    Example:
        GET http://localhost:8000/sensor-data?limit=5
        GET http://localhost:8000/sensor-data?device_id=ESP32_001
    """
    
    # Verifica se o Firebase está configurado
    if not db:
        raise HTTPException(
            status_code=503,
            detail="Firebase não configurado"
        )
    
    try:
        # Inicia query na coleção
        query = db.collection('sensor_readings')
        
        # Aplica filtro por device_id se fornecido
        if device_id:
            query = query.where('device_id', '==', device_id)
        
        # Ordena por timestamp (mais recente primeiro) e limita resultados
        docs = query.order_by('timestamp_recebido', direction='DESCENDING').limit(limit).stream()
        
        # Converte documentos Firestore para lista de dicionários
        resultados = []
        for doc in docs:
            dados = doc.to_dict()
            dados['id'] = doc.id  # Adiciona o ID do documento Firestore
            resultados.append(dados)
        
        # Log no console
        print(f"📊 Consultando Firebase: {len(resultados)} resultados")
        
        return {
            "total": len(resultados),
            "limit": limit,
            "device_id_filter": device_id if device_id else "todos",
            "dados": resultados,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Erro ao consultar Firebase: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar dados: {str(e)}"
        )


# ========================================
# EXECUÇÃO DIRETA
# ========================================

if __name__ == "__main__":
    """
    Permite executar a API diretamente com: python api_firebase.py
    Recomendado usar: uvicorn api_firebase:app --reload
    """
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
