## Configurazione Switch - Troubleshootings - Documento Tecnico Sessione Mattutina

## 1. Obiettivo della sessione

La sessione ha avuto come scopo:

- Ripristinare la connettività tra FW2 (pfSense) e lo switch TP-Link SG3210XHP-M2.
- Stabilizzare l’uplink sulla porta 1.
- Verificare e attivare VLAN10.
- Preparare la struttura per VLAN20/30/40.
- Identificare le impostazioni temporanee da correggere in una fase successiva.

---

## 2. Stato iniziale e problemi riscontrati

### 2.1 Perdita di connettività

La porta 1 dello switch era stata configurata come **Tagged Only** prima che FW2 fosse pronto a gestire solo traffico taggato. Questo ha causato:

- Perdita di DHCP
- Perdita di routing
- Perdita di accesso allo switch
- Necessità di collegarsi tramite porta 8

### 2.2 VLAN incomplete su FW2

Le VLAN erano definite e assegnate, ma non tutte avevano:

- IP statico
- DHCP attivo
- Regole firewall minime

### 2.3 Comportamento specifico dello switch TP-Link

Lo switch non utilizza la classica interfaccia Tagged/Untagged/Excluded. La logica reale è:

- Porta presente nella VLAN → Tagged
- Porta presente + PVID = VLAN ID → Untagged
- Porta assente → Excluded

---

## 3. Interventi eseguiti

### 3.1 Recupero accesso allo switch

- Collegamento tramite **porta 8**.
- Ripristino porta 1 come:
  - PVID 1
  - Ingress Checking Enabled
  - Acceptable Frame Types: Admit All
- Ripristino VLAN1 untagged sull’uplink.

### 3.2 Verifica e completamento configurazione VLAN su FW2

- Confermata presenza VLAN10/20/30/40 su igc1.
- Confermata assegnazione interfacce.
- Verificate regole firewall:
  - Blocchi inter-VLAN corretti
  - Accesso Internet consentito
  - Accesso a FW2 consentito da VLAN40
- DHCP attivo e funzionante su VLAN10.

### 3.3 Configurazione trunk su porta 1 dello switch

- Porta 1 membro di tutte le VLAN (1/10/20/30/40).
- Porta 1 mantiene **Admit All** (temporaneo).
- Trunk operativo.

### 3.4 Configurazione porta 5 come access VLAN10

- Porta 5 membro VLAN10.
- PVID 10.
- Acceptable Frame Types: Admit All.
- Test DHCP → OK (10.10.10.100).
- Test Internet → OK.
- Test isolamento VLAN → OK.

---

## 4. Configurazione attuale

### 4.1 Switch – VLAN Config

- VLAN1 → porte 1–10
- VLAN10 → porte 1, 5
- VLAN20 → porta 1
- VLAN30 → porta 1
- VLAN40 → porta 1

### 4.2 Switch – Port Config

| Porta | PVID | Ingress Checking | Acceptable Frame Types | Note              |
|-------|------|------------------|------------------------|-------------------|
| 1/0/1 | 1    | Enabled          | Admit All              | Trunk temporaneo  |
| 1/0/5 | 10   | Enabled          | Admit All              | Access VLAN10     |
| 1/0/8 | 1    | Enabled          | Admit All              | Porta di gestione |
| Altre | 1    | Enabled          | Admit All              | Default           |

### 4.3 FW2 – VLAN

- VLAN10 → 10.10.10.1/24
- VLAN20 → 10.10.20.1/24
- VLAN30 → 10.10.30.1/24
- VLAN40 → 10.10.40.1/24

### 4.4 FW2 – DHCP

- VLAN10 → attivo (range 10.10.10.100–199)
- VLAN20 → da attivare
- VLAN30 → da attivare
- VLAN40 → da attivare

### 4.5 FW2 – Firewall

- VLAN10 → blocco verso LAN e DMZ, allow verso Internet, allow DNS
- VLAN40 → blocco verso DMZ, allow verso Internet, allow GUI e DNS

---

## 5. Impostazioni temporanee da correggere più avanti

- Porta 1/0/1 → Acceptable Frame Types = Admit All
  - Da cambiare in Tagged Only solo quando VLAN1 non sarà più usata.
- VLAN1 ancora attiva su tutte le porte
  - Da ridurre progressivamente.
- Switch ancora in VLAN1 (management)
  - Da spostare in VLAN40.

---

## 6. Prossimi passi

### 6.1 Testare VLAN20, VLAN30, VLAN40

- Configurare porte dedicate.
- Verificare DHCP.
- Verificare isolamento.

### 6.2 Spostare lo switch in VLAN40

- Impostare IP management su 10.10.40.x.
- Aggiornare PVID porta di gestione.
- Aggiornare regole firewall.

### 6.3 Rimuovere VLAN1 dalle porte non necessarie

- Ridurre VLAN1 a sola porta trunk.

### 6.4 Impostare porta 1/0/1 su Tagged Only

- Solo dopo migrazione completa.

---

## 7. Porta da usare alla ripresa dei lavori

### Porta consigliata: **1/0/8**

- VLAN1 untagged
- Accesso garantito
- Non coinvolta nella migrazione

---

## 8. Stato finale

La rete è stabile, VLAN10 è operativa e il trunk funziona correttamente. Le impostazioni temporanee sono chiaramente identificate e verranno modificate nella fase successiva della migrazione.