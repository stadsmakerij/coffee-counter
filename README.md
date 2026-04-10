# Coffee Counter — Koffieteller

Draait op een Raspberry Pi en telt het aantal gezette kopjes koffie door het stroomverbruik van een Shelly Plug te monitoren via MQTT. Gebruikt een machine learning model dat getraind is op gelabelde stroomverbruikdata.

## Installatie

```bash
bash install.sh
```

Dit zet de virtual environment op, installeert dependencies, configureert de Mosquitto MQTT broker en maakt een systemd service aan.

## Gebruik

### 1. Data verzamelen

Na de installatie draait de service in dataverzamelmodus. Stroomdata wordt gelogd naar `power_log.csv`.

### 2. Koffiezetbeurten labelen

Start een sessie als je erbij bent en markeer de zetbeurten:

```bash
python label_coffee.py start   # sessie starten
python label_coffee.py on      # begin van een zetbeurt
python label_coffee.py off     # einde van een zetbeurt
python label_coffee.py stop    # sessie stoppen
```

Data die buiten een actieve sessie wordt gelogd krijgt het label `unlabeled` en wordt niet meegenomen in de training. Zo worden onbewaakte zetbeurten niet per ongeluk als `no` gelabeld.

### 3. Model trainen

Na het labelen van ~10-20 zetbeurten:

```bash
bash retrain.sh
```

Dit traint het model en herstart de service. Koffiezetbeurten worden nu automatisch gedetecteerd en gelogd in `coffee_log.csv`.

## Commando's

| Commando                                        | Omschrijving |
|-------------------------------------------------|---|
| `bash install.sh`                               | Volledige installatie |
| `python label_coffee.py start`                  | Sessie starten |
| `python label_coffee.py stop`                   | Sessie stoppen |
| `python label_coffee.py on`                     | Begin zetbeurt labelen |
| `python label_coffee.py off`                    | Einde zetbeurt labelen |
| `python label_coffee.py status`                 | Sessie- en labelstatus bekijken |
| `bash reset.sh`                                  | Alle data, model en markers verwijderen |
| `bash retrain.sh`                               | Model opnieuw trainen en service herstarten |
| `sudo journalctl -u coffee-counter.service -f`  | Live logs bekijken |
| `sudo systemctl restart coffee-counter.service` | Service herstarten |

## Configuratie

De Shelly Plug moet geconfigureerd zijn om MQTT-data te sturen naar het IP van de Pi op poort `1883`. Het MQTT-topic wordt ingesteld in `main.py`.

### Metrics API

Koffiedetecties kunnen naar een externe API gestuurd worden. Configureer dit via environment variables in het systemd service-bestand (`/etc/systemd/system/coffee-counter.service`):

| Variabele | Omschrijving |
|---|---|
| `METRICS_API_ENABLED` | Zet op `true` om in te schakelen (standaard: `false`) |
| `METRICS_API_URL` | URL van het API-endpoint |
| `METRICS_API_TOKEN` | Bearer token voor authenticatie |

Voorbeeld:

```
Environment=METRICS_API_ENABLED=true
Environment=METRICS_API_URL=https://example.com/api/metrics
Environment=METRICS_API_TOKEN=your-token-here
```

Na het aanpassen, herladen en herstarten:

```bash
sudo systemctl daemon-reload
sudo systemctl restart coffee-counter.service
```
