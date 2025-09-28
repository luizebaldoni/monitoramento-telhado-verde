# Módulo de Hardware — Sistema de Monitoramento do Telhado Verde

Este diretório contém os arquivos, esquemas e códigos relacionados ao hardware do Sistema de Monitoramento do Telhado Verde do Jardim Botânico da UFSM.

---

## 📑 Sumário
- [Descrição](#descrição)
- [Estrutura](#estrutura)
- [Tecnologias e Componentes](#tecnologias-e-componentes)
- [Sensores Utilizados](#sensores-utilizados)
- [Integração com o Software](#integração-com-o-software)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## 📋 Descrição

O módulo de hardware é responsável pela coleta de dados ambientais (temperatura, umidade, chuva) utilizando sensores conectados a um microcontrolador ESP32. Os dados são enviados via WiFi, em formato JSON, diretamente para o backend do sistema.

---

## 📂 Estrutura

- **/circuitos/** — Esquemas elétricos e diagramas de montagem
- **/firmware/** — Códigos para microcontroladores (ESP32)
- **/docs/** — Documentação técnica do hardware

---

## 🔌 Tecnologias e Componentes

- Microcontrolador: **ESP32**
- Comunicação: **WiFi** (envio de arquivo JSON para o servidor)
- Alimentação: **Energia elétrica convencional (tomada)**

---

## 🛠️ Sensores Utilizados

- **HL-69** — Sensor de umidade do solo
- **DS18B20** — Sensor de temperatura do solo
- **DHT11** — Sensor de temperatura e umidade do ar
- **Pluviômetro (pluviogravo)** — Sensor para captação de chuva

---

## 🔗 Integração com o Software

O hardware envia dados em formato JSON para a API REST do backend Django, que armazena e disponibiliza as informações para visualização e análise.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para sugerir melhorias, abrir issues ou enviar pull requests.

---

## 📄 Licença

Este projeto é reservado aos autores e não possui licença aberta de uso ou distribuição.
