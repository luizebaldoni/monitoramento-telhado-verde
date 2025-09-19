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
