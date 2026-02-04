# Procedura di Migrazione Senza Downtime

Questa sezione descrive la procedura definitiva per installare FW1, FW2, switch gestito e FRITZ!Box 5590 come Access Point, **senza interrompere la rete esistente** fino allo switch finale. È ottimizzata per la Vodafone Wi‑Fi 6 Station, che disattiva il routing quando si abilita *Static NAT Host*.

---

# 1. Principio Fondamentale

La funzione **Static NAT Host** della Vodafone Station:

- disattiva il routing
- disconnette tutti i client tranne l’host scelto
- funziona come pseudo‑bridge

👉 **Quindi va attivata SOLO nello switch finale.**

---

# 2. Fase 0 — Preparazione 

Tutti i dispositivi vengono configurati offline.

## 2.1 FW1 (Shargevedi N100)

- WAN temporaneamente su DHCP
- Interfaccia DMZ: `10.10.50.1/24`
- Non collegarlo ancora alla rete attuale

## 2.2 FW2 (Shargevedi J4125)

- Interfaccia DMZ: `10.10.50.2/24`
- Interfaccia LAN: `10.10.0.1/24`
- Prepara VLAN (LAN, IoT, Guest, Mgmt) ma non attivarle

## 2.3 Switch Gestito

- IP management: `10.10.0.2`
- Configura VLAN ma non collegarlo alla rete attuale

## 2.4 FRITZ!Box 5590 (Access Point)

- IP statico: `10.10.0.3`
- DHCP OFF
- Modalità IP Client
- Wi‑Fi ON

## 2.5 Host DMZ (Docker: Caddy + AIO)

- IP statico: `10.10.50.10`
- Non collegarlo ancora

👉 Nessun impatto sulla rete attuale.

---

# 3. Fase 1 — Preparazione Vodafone Station 

## 3.1 Disattiva solo ciò che non rompe la rete

- UPnP OFF
- Port forwarding vuoto
- Firewall minimo

## 3.2 NON toccare ancora

- DHCP
- Wi‑Fi
- Static NAT Host
- DMZ

👉 La rete attuale continua a funzionare.

---

# 4. Fase 2 — Collegamento FW1

## 4.1 Collega FW1 alla Vodafone Station

- Porta LAN Station → Porta WAN FW1
- FW1 ottiene un IP via DHCP

## 4.2 NON attivare Static NAT Host

👉 Attivarlo ora farebbe cadere tutta la rete.

---

# 5. Fase 3 — Costruzione DMZ Offline 

## 5.1 Collega FW1 ↔ FW2 (interfacce DMZ)

## 5.2 Collega Host AIO alla DMZ di FW2

## 5.3 Collega Switch e AP alla LAN di FW2

👉 La nuova rete è pronta ma non è ancora in produzione.

---

# 6. Fase 4 — Test della Nuova Rete 

- Connetti un laptop allo switch
- Verifica FW2 (`10.10.0.1`)
- Verifica Host DMZ (`10.10.50.10`)
- Verifica FRITZ AP (`10.10.0.3`)

👉 Tutto funziona senza toccare la rete attuale.

---

# 7. Fase 5 — Switch Finale (Downtime 10–20 secondi)

Questa è l’unica fase in cui la rete cade.

## 7.1 Disattiva DHCP sulla Vodafone Station

## 7.2 Disattiva Wi‑Fi sulla Vodafone Station

## 7.3 Attiva **Static NAT Host → IP WAN di FW1**

## 7.4 Riavvia FW1

## 7.5 Riavvia FW2

## 7.6 Collega tutti i client allo switch o al FRITZ AP

👉 Nuovo path attivo:

```
Internet → Vodafone Station (Static NAT Host) → FW1 → DMZ → FW2 → LAN
```

---

# 8. Fase 6 — Verifica Finale

- AIO raggiungibile da Internet
- Caddy funziona
- LAN operativa
- IoT isolata
- Guest isolata
- Mgmt accessibile
- Vodafone Station senza client

---

# Conclusione

Questa procedura garantisce una migrazione **senza downtime** fino allo switch finale, rispettando il comportamento reale della Vodafone Wi‑Fi 6 Station e integrando perfettamente FW1, FW2, DMZ reale, switch gestito e FRITZ!Box 5590 come AP.