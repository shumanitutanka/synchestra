# Checklist Pre-Produzione – Rilascio Rete Enterprise

Questa checklist è operativa, diretta e pensata per il giorno del rilascio. Nessun formalismo inutile.

---

## 1. Vodafone Station (VS)

### 1.1 Disattivare tutto

- Wi‑Fi: OFF
- DHCP: OFF
- DNS locale: OFF
- Firewall: OFF
- NAT: OFF
- UPnP: OFF
- Port forwarding: rimuovere tutto
- DMZ: OFF
- Rete Sicura / filtri vari: OFF

### 1.2 Configurare *Modem Generico*

- Tipo connessione: **DHCP**
- NAT: **OFF**
- Firewall: **OFF**
- VLAN ID: **0**
- MTU: **1500**
- DNS: automatico
- Opzione 12: vuoto
- Opzione 60: vuoto
- Opzione 125: OFF

### 1.3 Riavvio VS

- Riavviare la Station dopo il salvataggio.

---

## 2. FW1 (pfSense) – Firewall Primario

### 2.1 WAN

- Collegata a VS (LAN1)
- Configurazione: **DHCP**
- MTU: 1500
- Gateway: automatico

### 2.2 Verifica IP pubblico

Da FW1:

```
curl ifconfig.me
```

Deve restituire un IP pubblico (109.x.x.x).

### 2.3 NAT inbound

- 443 → FW2 (DMZ Transit) → Caddy
- 80 → FW2 (solo ACME)
- Altre porte se necessarie

### 2.4 NAT outbound

Reti da NATtare:

- 10.10.0.0/24
- 10.10.10.0/24
- 10.10.20.0/24
- 10.10.30.0/24
- 10.10.40.0/24
- 10.10.60.0/24

### 2.5 DMZ Transit

- FW1 IP: 10.10.50.1
- Regole firewall: consentire solo traffico FW1 ↔ FW2

### 2.6 UPS – NUT Server

- Installare NUT server su FW1
- Configurare shutdown coordinato

---

## 3. FW2 (pfSense) – Firewall Secondario

### 3.1 WAN

- IP statico: 10.10.50.2
- Gateway: 10.10.50.1

### 3.2 LAN e VLAN

- LAN: 10.10.0.0/24
- VLAN10: 10.10.10.0/24 (Client)
- VLAN20: 10.10.20.0/24 (IoT)
- VLAN30: 10.10.30.0/24 (Guest)
- VLAN40: 10.10.40.0/24 (Mgmt)
- DMZ-SERVERS: 10.10.60.0/24

### 3.3 Regole firewall

- DMZ-SERVERS → Internet: ALLOW
- DMZ-SERVERS → LAN/VLAN: BLOCK
- LAN/VLAN → DMZ-SERVERS: ALLOW solo se necessario
- VLAN20 ↔ VLAN30 ↔ VLAN10: isolate
- VLAN40: accesso solo a GUI FW1/FW2/SW0

### 3.4 UPS – NUT Client

- FW2 come client NUT

---

## 4. NAS Ugreen (DMZ-SERVER)

- Rete: 10.10.60.x
- Servizi: Nextcloud AIO, Borg, Docker
- NUT client attivo

---

## 5. Switch TP-Link Omada (SW0)

### 5.1 Trunk

- Porta uplink → FW2 LAN (igc1)
- Tutte le VLAN taggate

### 5.2 Porte access

- VLAN10: client
- VLAN20: IoT
- VLAN30: guest
- VLAN40: mgmt (solo porta fisica dedicata)

---

## 6. Access Point Fritz WiFi6

- SSID Client → VLAN10
- SSID IoT → VLAN20
- SSID Guest → VLAN30
- SSID Mgmt → VLAN40

---

## 7. UPS – Gestione blackout

- UPS APC 550VA collegato a FW1
- FW1 = NUT server
- FW2, NAS, altri host = NUT client
- Shutdown ordinato quando:
  - batteria < 30%
  - autonomia < soglia configurata

---

## 8. Test finali

### 8.1 WAN

- IP pubblico su FW1
- Ping 8.8.8.8 OK
- Ping dominio pubblico OK

### 8.2 DMZ inbound

- HTTPS → Caddy → Nextcloud OK
- HTTP → redirect → HTTPS OK

### 8.3 Segmentazione

- VLAN20 non raggiunge VLAN10
- VLAN30 non raggiunge VLAN10
- VLAN40 raggiunge solo GUI apparati
- DMZ-SERVERS non raggiunge LAN/VLAN

### 8.4 UPS

- Simulare blackout
- Verificare shutdown ordinato

---

Questa checklist è pronta per l'uso il giorno del rilascio, senza formalismi inutili.