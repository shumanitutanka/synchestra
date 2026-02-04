# Configurazione Switch SG3210XHP‑M2 – Stato Aggiornato

## 1. Stato generale

Lo switch TP-Link SG3210XHP‑M2 è ora correttamente collegato a FW2 tramite porta **1/0/1** in modalità trunk (operativa), con VLAN10 funzionante e VLAN20/30/40 pronte per i test successivi.

La porta di gestione temporanea rimane **1/0/8**, in VLAN1 untagged.

---

## 2. VLAN configurate

### 2.1 Tabella VLAN

| VLAN | Nome        | Porte membri |
|------|-------------|--------------|
| **1**    | System-VLAN | 1–10         |
| **10**   | Clients     | 1, 5         |
| **20**   | IoT         | 1            |
| **30**   | Guest       | 1            |
| **40**   | Mgmt        | 1            |

### 2.2 Logica TP-Link

- Porta presente nella VLAN → **Tagged**
- Porta presente + PVID = VLAN ID → **Untagged**
- Porta assente → **Excluded**

---

## 3. Configurazione porte

### 3.1 Port Config

| Porta            | PVID | Ingress Checking | Acceptable Frame Types | Ruolo                      |
|------------------|------|------------------|------------------------|----------------------------|
| **1/0/1**            | 1    | Enabled          | **Admit All**              | Trunk temporaneo verso FW2 |
| **1/0/5**            | 10   | Enabled          | Admit All              | Access VLAN10              |
| **1/0/8**            | 1    | Enabled          | Admit All              | Porta gestione             |
| 1/0/2–4,6–7,9–10 | 1    | Enabled          | Admit All              | Default (VLAN1)            |

### 3.2 Note operative

- Porta 1/0/1 deve rimanere **Admit All** finché VLAN1 è attiva.
- Porta 5 è correttamente configurata come **ACCESS VLAN10**.
- Porta 8 rimane la porta di gestione sicura.

---

## 4. Test eseguiti

### 4.1 VLAN10 (porta 5)

- DHCP: **OK** → 10.10.10.100
- Ping 10.10.10.1: **OK**
- Ping 1.1.1.1: **OK**
- Ping google.com: **OK**
- Ping 10.10.0.1: **BLOCCATO** (corretto: isolamento VLAN)

---

## 5. Impostazioni temporanee da correggere più avanti

| Componente        | Impostazione attuale               | Da modificare              | Quando                          |
|-------------------|------------------------------------|----------------------------|---------------------------------|
| Porta 1/0/1       | Acceptable Frame Types = **Admit All** | Tagged Only                | Quando VLAN1 non sarà più usata |
| VLAN1             | Presente su tutte le porte         | Ridurre a sola porta trunk | Dopo migrazione completa        |
| Switch mgmt       | VLAN1                              | VLAN40                     | Dopo test VLAN40                |
| DHCP VLAN20/30/40 | Non attivi                         | Attivare                   | Prima migrazione dispositivi    |

---

## 6. Prossimi passi

1. Test VLAN20 (porta dedicata)
2. Test VLAN30
3. Test VLAN40
4. Spostare lo switch in VLAN40
5. Ridurre VLAN1 alle sole porte necessarie
6. Impostare porta 1/0/1 su Tagged Only

---

## 7. Porta da usare alla ripresa dei lavori

### **Porta consigliata: 1/0/8**

- VLAN1 untagged
- Accesso garantito
- Non coinvolta nella migrazione

---

## 8. Stato finale

La configurazione dello switch è stabile, VLAN10 è operativa e il trunk funziona correttamente. Le impostazioni temporanee sono chiaramente identificate e verranno modificate nella fase successiva della migrazione.