# 

## 1. Switch TP-Link Omada (SW0)

### Stato effettivo

- VLAN create: 10 (Client), 20 (IoT), 30 (Guest), 40 (Mgmt)
- Porta uplink → FW2 (igc1)
  - Modalità: TRUNK
  - VLAN taggate: 10,20,30,40
  - Nessuna untagged
- Porte access configurate:
  - Porta 3 → VLAN10 (Client)
  - Porta 4 → VLAN20 (IoT)
  - Porta 5 → VLAN30 (Guest)
  - Porta 6 → VLAN40 (Mgmt) **porta fisica dedicata per GUI apparati**
- Porte 7–8 → libere

### Cosa manca

- Configurazione porta per Access Point (TRUNK)
- Test traffico WiFi → VLAN
- Verifica tagging/untagging lato AP

---

## 2. FW2 – VLAN e routing

### Stato effettivo

- VLAN su igc1:
  - VLAN10 → 10.10.10.0/24
  - VLAN20 → 10.10.20.0/24
  - VLAN30 → 10.10.30.0/24
  - VLAN40 → 10.10.40.0/24
- DMZ-SERVERS → 10.10.60.0/24
- DHCP attivo su tutte le VLAN
- Regole firewall:
  - VLAN20 → Internet only
  - VLAN30 → Internet only
  - VLAN40 → accesso solo a GUI apparati
  - VLAN10 → normale accesso LAN
  - DMZ-SERVERS → isolata da LAN/VLAN
- Routing FW1 ↔ FW2 funzionante

### Cosa manca

- Nessuna configurazione AP
- Nessuna regola specifica per traffico WiFi
- Nessun captive portal (non richiesto)

---

## 3. FW1 – Stato attuale

- WAN → collegata a Vodafone Station (DHCP)
- DMZ Transit → 10.10.50.1
- NAT inbound pronto (443 → FW2 → Caddy)
- NAT outbound per tutte le reti 10.10.x.x
- Regole DMZ Transit: solo FW1 ↔ FW2

### Cosa manca

- Passaggio VS → modalità bridge DHCP (Modem Generico)
- Disattivazione totale servizi VS

---

## 4. Access Point (Fritz WiFi6)

### Stato attuale

- **Mai acceso, mai configurato**

### Cosa va fatto

- Mettere AP in modalità Access Point puro
- Disattivare DHCP/NAT/firewall
- Configurare SSID → VLAN:
  - Client → VLAN10
  - IoT → VLAN20
  - Guest → VLAN30
  - Mgmt → VLAN40
- Impostare IP statico AP in VLAN40 (es. 10.10.40.10)
- Collegare AP alla **porta 2** dello switch (TRUNK)

---

## 5. UPS / NUT

### Stato effettivo

- UPS APC 550VA collegato a FW1
- FW1 = NUT server
- FW2 e NAS = NUT client (da configurare)

### Cosa manca

- Test blackout reale
- Verifica shutdown ordinato

---

## 6. Stato generale

### Completato

- VLAN
- Routing
- DMZ
- NAT
- Switch base
- FW1 ↔ FW2

### Da completare

- Configurazione Access Point
- Porta trunk AP su SW0
- Setup definitivo Vodafone Station
- Test WiFi → VLAN
- Test UPS

---

Questa pagina raccoglie tutto ciò che è ancora in sospeso e che va completato prima del rilascio definitivo.