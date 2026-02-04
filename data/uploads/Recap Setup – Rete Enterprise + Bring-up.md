## Recap Setup – Rete Enterprise + Fase di Bring-up

### Stato attuale

- **Vodafone Station (VS)** attiva con:
  - NAT, firewall, DNS, DHCP, routing LAN
  - Subnet: `192.168.100.x` ("casa - old")
- **FW1 (pfSense)** collegato alla porta **LAN1** della VS
  - Riceve IP via DHCP da VS
  - Gateway per la rete enterprise in fase di attivazione
  - Introduce NAT su subnet `10.10.x.x`

### Rete enterprise da mettere in opera

#### FW1 – Firewall Primario

- WAN: collegata a VS (LAN1)
- LAN: `192.168.1.0/24` (temporanea)
- DMZ Transit: `10.10.50.0/24` → collegamento diretto con FW2
- IP Transit: `10.10.50.1`
- Sarà installato **NUT server** per gestione blackout UPS

#### FW2 – Firewall Secondario

- WAN: `10.10.50.2` (verso FW1)
- LAN: `10.10.0.0/24`
- DMZ-SERVERS: `10.10.60.0/24` → ospita NAS Ugreen
- VLANs su igc1:
  - VLAN10: `10.10.10.0/24` (Client)
  - VLAN20: `10.10.20.0/24` (IoT)
  - VLAN30: `10.10.30.0/24` (Guest)
  - VLAN40: `10.10.40.0/24` (Mgmt)

#### NAS Ugreen (DMZ-SERVER)

- Collegato a FW2 su interfaccia DMZ-SERVERS
- IP: `10.10.60.x`
- Servizi: Nextcloud AIO, Borg backup, Docker stack
- Previsto NUT client per shutdown controllato

#### SW0 – Switch TP-Link Omada gestito

- Uplink: collegato a FW2 LAN (igc1)
- VLAN trunk attivo
- Porte access assegnate a VLAN10/20/30/40
- VLAN40 accessibile **solo da porta fisica dedicata** per gestione web FW1/FW2/SW0

#### Access Point Fritz WiFi6

- Collegato a SW0 su porta trunk
- SSID mappati:
  - SSID Client → VLAN10
  - SSID IoT → VLAN20
  - SSID Guest → VLAN30
  - SSID Mgmt → VLAN40

### Segmentazione e sicurezza

- VLAN20 (IoT) e VLAN30 (Guest) **isolate** da VLAN10 e VLAN40
- VLAN40 (Mgmt) accessibile **solo fisicamente** da porta dedicata su SW0
- DMZ-SERVERS isolata da LAN/VLAN
- NAT outbound gestito da FW2
- NAT inbound gestito da FW1 → FW2 → DMZ-SERVERS

### UPS e gestione blackout

- UPS APC 550VA collegato a FW1
- Gestione blackout via **NUT client/server**:
  - Server NUT su FW1
  - Client NUT su FW2, NAS Ugreen, altri host critici

### Promemoria operativo per rilascio

- VS sarà configurata come **bridge DHCP trasparente** verso FW1
- Sezione da configurare: **Modem Generico**
- Static NAT su VS **non va usato**
- Tutto il resto su VS va **disattivato** (NAT, firewall, DHCP, Wi-Fi)

---

Questa pagina è il riferimento principale per tutte le discussioni future sul setup enterprise. Ogni modifica hardware, VLAN, UPS o routing va riportata qui.