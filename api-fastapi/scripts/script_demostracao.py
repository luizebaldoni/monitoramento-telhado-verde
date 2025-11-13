"""
SCRIPT DE DEMONSTRAÇÃO EM TEMPO REAL
Sistema de Monitoramento de Telhado Verde

Este script simula um ESP32 enviando dados de sensores para a API,
permitindo testar e demonstrar todo o sistema funcionando sem o hardware físico.

Autor: Equipe Projeto Integrador 4 - UFSM
Uso: python script_demostracao.py
"""

import requests
import time
from datetime import datetime
from dados_simulados import LEITURAS_SIMULADAS

# ========================================
# CONFIGURAÇÕES
# ========================================

# URL base da API (deve estar rodando antes de executar este script)
API_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 10  # Timeout para requisições HTTP em segundos

# Carrega as 30 leituras simuladas do arquivo separado
leituras = LEITURAS_SIMULADAS


# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def enviar_leitura(leitura, numero):
    """
    Envia uma leitura simulada para a API
    
    Args:
        leitura (dict): Dados do sensor no formato JSON
        numero (int): Número sequencial da leitura (para exibição)
    """
    print("\n" + "="*60)
    print(f" ENVIANDO LEITURA #{numero}")
    print("="*60)
    
    # Atualiza timestamp para o momento atual
    leitura["timestamp"] = datetime.now().isoformat()
    
    # Exibe preview dos dados que serão enviados
    print(f" Device: {leitura['device_id']}")
    print(f" Temperatura Solo: {leitura['sensors']['ds18b20']['temperature']}°C")
    print(f" Temperatura Ar: {leitura['sensors']['dht11']['temperature']}°C")
    print(f" Umidade: {leitura['sensors']['dht11']['humidity']}%")
    
    try:
        # Envia POST para a API
        response = requests.post(
            f"{API_URL}/sensor-data",
            json=leitura,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print("\n✅ SUCESSO!")
            print(f"Firebase ID: {resultado['firestore_id']}")
        else:
            print(f"\nErro: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.RequestException as e:
        print(f"\n Erro ao conectar: {str(e)}")
        print("Certifique-se que a API está rodando!")
        print(" Execute: uvicorn api_firebase:app --reload")


def consultar_dados():
    """
    Consulta os dados mais recentes salvos no Firebase
    Útil para verificar se os dados foram armazenados corretamente
    """
    print("\n" + "="*60)
    print(" CONSULTANDO DADOS MAIS RECENTES")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_URL}/sensor-data?limit=5",  # Mostra apenas as 5 mais recentes
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\nTotal de leituras encontradas: {resultado['total']}")
            print(f"Exibindo as 5 mais recentes:")
            
            for i, dado in enumerate(resultado['dados'], 1):
                print(f"\n--- Leitura #{i} ---")
                print(f"Device: {dado['device_id']}")
                print(f"Timestamp: {dado['timestamp_recebido']}")
                print(f"Temp Solo: {dado['sensors']['ds18b20']['temperature']}°C")
                print(f"Temp Ar: {dado['sensors']['dht11']['temperature']}°C")
                print(f"Umidade: {dado['sensors']['dht11']['humidity']}%")
                print(f"Umidade Solo: {dado['sensors']['hl69']['soil_moisture']}%")
        else:
            print(f"❌ Erro: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {str(e)}")


# ========================================
# FUNÇÃO PRINCIPAL
# ========================================

def main():
    """
    Função principal que executa a demonstração completa
    
    Fluxo:
    1. Exibe informações sobre o que o script fará
    2. Aguarda confirmação do usuário
    3. Envia 30 leituras simuladas (com intervalo de 1s)
    4. Consulta os dados salvos no Firebase
    5. Exibe instruções para verificação manual
    """
    print("\n" + "🌱"*30)
    print("DEMONSTRAÇÃO EM TEMPO REAL - TELHADO VERDE")
    print("🌱"*30)
    
    input("\nPressione ENTER para começar...")
    
    # ETAPA 1: Envio das leituras
    print("\n" + "-"*60)
    print(f"🚀 INICIANDO ENVIO DE {len(leituras)} LEITURAS")
    print("-"*60)
    
    tempo_inicio = time.time()
    
    for i, leitura in enumerate(leituras, 1):
        enviar_leitura(leitura, i)
        if i < len(leituras):  # Não aguarda após a última leitura
            time.sleep(1)  # Pausa de 1 segundo entre envios
    
    tempo_total = time.time() - tempo_inicio
    
    # ETAPA 2: Consulta dos dados
    print("\n" + "-"*60)
    print("VERIFICANDO DADOS SALVOS")
    print("-"*60)
    time.sleep(1)
    consultar_dados()
    
    # ETAPA 3: Finalização e instruções
    print("\n" + "="*60)
    print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"\n Tempo total: {tempo_total:.1f} segundos")
    print(f" Leituras enviadas: {len(leituras)}")
    
    print("\n Próximos passos:")
    print("   1. Abra o Firebase Console para ver os dados:")
    print("      https://console.firebase.google.com/")
    print("\n   2. Acesse a documentação Swagger da API:")
    print("      http://localhost:8000/docs")
    print("\n   3. Teste manualmente enviando dados personalizados")
    print("\n")


# ========================================
# PONTO DE ENTRADA
# ========================================

if __name__ == "__main__":
    """
    Executa o script quando chamado diretamente
    Uso: python script_demostracao.py
    """
    main()
