# Migrazione Nextcloud AIO su Ugreen UGoS – Diario tecnico completo (24h)

Questo documento raccoglie tutte le informazioni tecniche, i problemi affrontati, le soluzioni, i comandi usati e le scoperte forensi durante le 24 ore di lavoro dedicate alla migrazione di Nextcloud AIO su Ugreen UGoS.

## 1. Contesto iniziale

- Obiettivo: migrare Nextcloud AIO da un ambiente precedente a Ugreen UGoS mantenendo dati, configurazioni, backup Borg e reverse proxy esterno.
- Ambiente UGoS:
  - RAID1 NVMe montato su `/volume1`.
  - USB EXT4 montato su `/mnt/@usb/sda1`.
  - Docker preinstallato con volumi in `/volume1/@docker/volumes/`.
  - Porta 443 liberata da NGINX interno.

## 2. Preparazione dell’ambiente

### 2.1 Liberazione della porta 443

- Disattivazione del reverse proxy interno Ugreen.
- Verifica con `ss`, `curl` e conferma che nessun servizio occupasse più la porta.

### 2.2 Verifica mount reali

- RAID1 → `/volume1`.
- USB EXT4 → `/mnt/@usb/sda1`.
- Validazione con `lsblk`, `mount`, `df -h`.

## 3. Restore Nextcloud AIO – Prima fase

### 3.1 Restore iniziale

- Restore Borg completato.
- Volumi ripristinati.
- Mastercontainer avviato.

### 3.2 Problema critico: runtime NVIDIA

Errore ricorrente:

```
unknown or invalid runtime name: nvidia
```

Cause:

- Il backup conteneva configurazioni GPU NVIDIA.
- UGoS non ha runtime NVIDIA.
- AIO tentava di ricreare i container con `"runtime": "nvidia"`.

Effetti:

- Nextcloud non veniva creato.
- Apache non partiva.
- Caddy restava in "Starting".
- GUI AIO in errore continuo.

## 4. Analisi forense del problema NVIDIA

### 4.1 Verifica volumi mastercontainer

- Montaggio volume:

  ```
  sudo docker run -it --rm -v nextcloud_aio_mastercontainer:/mnt alpine sh
  ```
- Struttura trovata: `caddy/`, `certs/`, `data/`, `session/`.

### 4.2 Individuazione del file incriminato

- Ricerca:

  ```
  grep -R "nvidia" -n /mnt/data
  ```
- Risultato:

  ```
  ./configuration.json:40: "enable_nvidia_gpu": "true",
  ```

### 4.3 Rimozione manuale

- Apertura file:

  ```
  vi configuration.json
  ```
- Eliminazione riga:

  ```
  "enable_nvidia_gpu": "true",
  ```

### 4.4 Riavvio mastercontainer

```
sudo docker restart nextcloud-aio-mastercontainer
```

## 5. Ricreazione del mastercontainer – Comando finale

```
sudo docker run \
  --init \
  --sig-proxy=false \
  --name nextcloud-aio-mastercontainer \
  --restart always \
  --publish 8080:8080 \
  --publish 8444:8444 \
  --env NEXTCLOUD_ENABLE_CADDY=false \
  --env APACHE_PORT=11000 \
  --env APACHE_IP_BINDING=0.0.0.0 \
  --env NEXTCLOUD_DATADIR="/volume1/ncdata" \
  --volume nextcloud_aio_mastercontainer:/mnt/docker-aio-config \
  --volume nextcloud_aio_database:/var/lib/postgresql/data \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/nextcloud-releases/all-in-one:latest
```

## 6. Volumi Docker su UGoS – Percorsi reali

UGoS usa:

```
/volume1/@docker/volumes/
```

Esempio:

```
/volume1/@docker/volumes/nextcloud_aio_nextcloud/_data/
```

## 7. Pulizia log Nextcloud

### 7.1 Metodo diretto (host)

```
sudo truncate -s 0 /volume1/@docker/volumes/nextcloud_aio_nextcloud/_data/data/nextcloud.log
```

### 7.2 Metodo interno al container

```
sudo docker exec -it nextcloud-aio-nextcloud bash -c "truncate -s 0 /var/www/html/data/nextcloud.log"
```

## 8. Problemi risolti durante le 24h

- Porta 443 occupata da Ugreen NGINX.
- Restore AIO incompleto per volumi vuoti.
- Configurazioni NVIDIA residue nel backup.
- GUI AIO in crash loop.
- Caddy in stato "Starting".
- Apache non avviabile.
- Nextcloud non creato.
- Percorsi volumi non standard su UGoS.
- Log Nextcloud non pulibili con percorso classico.
- Warning API Docker Desktop.
- Differenze tra CLI e GUI Ugreen.

## 9. Stato finale

- Mastercontainer avviato correttamente.
- Runtime NVIDIA rimosso definitivamente.
- Restore AIO funzionante.
- Tutti i container avviati.
- Caddy esterno pronto.
- Percorsi reali documentati.
- Log gestibili.
- Ambiente stabile.

## 10. Possibili estensioni future

- Script di manutenzione automatica log.
- Monitoraggio UPS.
- Documentazione per migrazione futura su Proxmox.
- Integrazione con Caddy AIO community container.
- Procedure di rollback forensic.