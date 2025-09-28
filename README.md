# Sistema de Monitoramento: Telhado Verde Jardim Botânico UFSM

Este repositório contém o código e a documentação do **Sistema de Monitoramento do Telhado Verde do Jardim Botânico da UFSM**. O projeto foi desenvolvido na disciplina de Projeto Integrador em Engenharia de Computação, em parceria com o Grupo de Pesquisas em Modelagem HidroAmbiental e Ecotecnologias da UFSM.

---

## Tecnologias

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![C++](https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)

| Componente | Tecnologias                                                         |
|------------|---------------------------------------------------------------------|
| Backend    | API Python, Firebase|
| Firmware   | C++ (Arduino Core), ESP32                                           |
| Frontend   | HTML5, CSS, JavaScript, Chart.js (para gráficos de histórico)           |
| Sensores   | DS18B20, DHT-11, HCSR04, HL-69 |
| Hardware final | PCB + case |

---

## Visão Geral do Sistema

O sistema é uma solução completa para **coleta, armazenamento e visualização de dados em tempo real**. Ele é dividido em três grandes módulos:

1. **Hardware & Firmware**: Sensores e microcontrolador ESP32 para coleta de dados.

2. **Backend & Cloud**: Uma API em Python para processamento de dados e o Firebase para armazenamento.

3. **Dashboard & Visualização**: Interface de usuário para visualizar os dados de forma clara e intuitiva.

---

## Arquitetura de Software
```mermaid
---
config:
  layout: fixed
---
flowchart TD
    E["**Views.py**"] -- **Show data graphs** --> A["**Frontend: Dashboard Web**"]
    B["**API: Django Backend**"] -- **Validating and processing** --> C["**Models.py**"]
    C -- **Save and recover** --> D[("**Firebase**")]
    D -- **Search and show** --> C
    B -- **Send POST** --> E
    F["**Hardware: ESP32**"] -- **Converted and packed** --> H["**Json File**"]
    H -- **Send data_sensors** --> B
    G["**Sensors**"] -- **Analog or digital Sinal** --> F
     E:::Backend
     A:::Frontend
     B:::Backend
     C:::Backend
     D:::Banco
     F:::Hardware
     H:::Aqua
     G:::Hardware
    classDef Backend fill:#f9f,stroke:#333,stroke-width:2px
    classDef Frontend fill:#ccf,stroke:#333,stroke-width:2px
    classDef Banco fill:#FFD580,stroke:#333,stroke-width:2px
    classDef Hardware fill:#FFE0B2, color:#000000
    classDef Aqua stroke-width:1px, stroke-dasharray:none, stroke:#46EDC8, fill:#DEFFF8, color:#378E7A
    style E color:#000000
    style A color:#000000 
    style B color:#000000
    style C color:#000000
    style D color:#000000
    style F color:#000000
    style H color:#000000
    style G stroke:#000000,color:#000000
```
---
## Funcionalidades
