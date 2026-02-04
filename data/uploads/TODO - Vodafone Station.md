## TODO: Vodafone Station – Setup di produzione

### Stato attuale

- FW1 è collegato alla **porta LAN1** della Vodafone Station.
- Riceve **IP via DHCP** dalla Station.
- Introduce NAT su subnet **10.10.x.x** per la fase di bring-up.

### Sezione da configurare

- La **sezione "Modem Generico"** è l'unica che va configurata per il setup di produzione.
- Parametri consigliati:
  - Tipo di connessione: **DHCP**
  - NAT: **disattivato**
  - Firewall: **disattivato**
  - VLAN ID: **0**
  - MTU: **1500**
  - DNS: automatico
  - Opzioni 12/60/125: **non necessarie**

### Sezioni da ignorare/disattivare

- La sezione **Static NAT** **non serve** in questo setup.
  - Il NAT inbound viene gestito da **FW1 → FW2 → DMZ-SERVERS**.
- Tutte le altre funzioni del modem (firewall, routing, NAT, Wi-Fi, LAN) vanno **disattivate o ignorate**.

### Obiettivo finale

- La Vodafone Station deve comportarsi come un **bridge DHCP trasparente** verso FW1.
- Nessuna interferenza lato modem.
- Tutto il controllo è demandato a FW1/FW2.

### Nota per il rilascio

- In fase di produzione, FW1 riceverà IP pubblico direttamente.
- La Station deve solo convertire GPON → Ethernet e consegnare la connettività.
- Nessun NAT, nessun firewall, nessun routing sul modem.