# Architettura Completa FW1/FW2 con DMZ Reale

Questa pagina integra le tre sezioni fondamentali:

- **1) Schema ASCII con IP già inseriti**
- **2) Mappa IP completa**
- **3) Checklist firewall definitiva**

Tutto è coerente con la tua architettura: DMZ reale tra FW1 e FW2, host Docker nella DMZ, FW2 per VLAN interne, FRITZ!Box 5590 come AP.

---

# 1. Schema ASCII con IP già inseriti

```
                           Internet (WAN)
                                 │
                           [ONT Vodafone]
                                 │
                        [Vodafone Station]
                     LAN: 192.168.100.1/24
                     Exposed Host → 192.168.100.2
                                 │
────────────────────────────────────────────────────
                                 │
                         [FW1 - N100]
                 WAN: 192.168.100.2/24 (GW .1)
                 DMZ: 10.10.50.1/24
                                 │
──────────────────────────  DMZ REALE  ──────────────────────────
                           Subnet: 10.10.50.0/24
                                 │
                 FW2 DMZ interface: 10.10.50.2
                                 │
                 Host DMZ Docker: 10.10.50.10
                 (Caddy Reverse Proxy + Nextcloud AIO)
                                 │
──────────────────────────  TRANSIT LAN  ─────────────────────────
                           Subnet: 10.10.0.0/24
                                 │
                         [FW2 - J4125]
                 LAN: 10.10.0.1/24
                                 │
                           [Switch Gestito]
                           Mgmt: 10.10.0.2
                                 │
                         [FRITZ!Box 5590 AP]
                           IP: 10.10.0.3
                                 │
────────────────────────────── VLAN ──────────────────────────────

LAN principale:   10.10.10.0/24   (GW 10.10.10.1)
IoT:              10.10.20.0/24   (GW 10.10.20.1)
Guest:            10.10.30.0/24   (GW 10.10.30.1)
Management:       10.10.40.0/24   (GW 10.10.40.1)
```

---

# 2. Mappa IP Completa

## 2.1 WAN interna (Vodafone Station → FW1)

| Dispositivo      | IP            | Note                              |
|------------------|---------------|-----------------------------------|
| Vodafone Station | 192.168.100.1 | DHCP OFF, Wi‑Fi OFF, Exposed Host |
| FW1 WAN          | 192.168.100.2 | Statico, gateway .1               |

---

## 2.2 DMZ reale tra FW1 e FW2

| Dispositivo | IP          | Note                  |
|-------------|-------------|-----------------------|
| FW1 DMZ     | 10.10.50.1  | Gateway DMZ lato FW1  |
| FW2 DMZ     | 10.10.50.2  | Gateway DMZ lato FW2  |
| Host Docker | 10.10.50.10 | Caddy + Nextcloud AIO |

---

## 2.3 Transit LAN (FW2 → Switch → AP)

| Dispositivo    | IP        | Note             |
|----------------|-----------|------------------|
| FW2 LAN        | 10.10.0.1 | Gateway VLAN     |
| Switch         | 10.10.0.2 | Mgmt             |
| FRITZ!Box 5590 | 10.10.0.3 | Access Point LAN |

---

## 2.4 VLAN interne

| VLAN  | Subnet        | Gateway    |
|-------|---------------|------------|
| LAN   | 10.10.10.0/24 | 10.10.10.1 |
| IoT   | 10.10.20.0/24 | 10.10.20.1 |
| Guest | 10.10.30.0/24 | 10.10.30.1 |
| Mgmt  | 10.10.40.0/24 | 10.10.40.1 |

---

# 3. Checklist Firewall Definitiva

## 3.1 FW1 → DMZ

- Allow WAN → 10.10.50.10 (porte 80/443)
- Block tutto il resto
- Allow DMZ → Internet (solo HTTPS)

---

## 3.2 DMZ → FW2 / LAN

- Block DMZ → LAN (default)
- Allow DMZ → DNS (solo se necessario)
- Allow DMZ → Internet (HTTPS)

---

## 3.3 LAN → DMZ

- Allow LAN → 10.10.50.10 (solo servizi necessari)
- Block LAN → DMZ per tutto il resto

---

## 3.4 IoT → LAN/DMZ

- Block IoT → LAN
- Block IoT → DMZ
- Allow IoT → Internet (solo HTTPS)

---

## 3.5 Guest → tutto

- Block Guest → LAN
- Block Guest → DMZ
- Block Guest → IoT
- Allow Guest → Internet (solo HTTP/HTTPS)

---

## 3.6 Mgmt → tutto

- Allow Mgmt → FW1/FW2/Switch/AP
- Block Mgmt → Internet (opzionale)

---

# Conclusione

Questa rappresenta la tua architettura definitiva: DMZ reale tra FW1 e FW2, host Docker isolato, VLAN pulite e firewall con regole professionali.