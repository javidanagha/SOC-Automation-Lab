# SOC Lab

A fully functional security monitoring lab built from scratch, chaining a **Wazuh SIEM**, **ModSecurity WAF**, and a **TheHive / Cortex / Shuffle SOAR** stack into a single automated detection-to-response pipeline.

![Wazuh](https://img.shields.io/badge/Wazuh-4.14-1F3864)
![ModSecurity](https://img.shields.io/badge/ModSecurity-OWASP%20CRS%203.3.8-1E7B4D)
![TheHive](https://img.shields.io/badge/TheHive-5.2-D68910)
![Cortex](https://img.shields.io/badge/Cortex-3.1.8-D68910)
![Shuffle](https://img.shields.io/badge/Shuffle-SOAR-D68910)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

---

## Overview

An attacker sends a request against a deliberately vulnerable web app (DVWA). The request is inspected and blocked by a WAF, logged and matched against custom detection rules by a SIEM, enriched with threat intelligence, and turned into a tracked incident. All automatically, with no manual step in between.

```
Attacker
   │
   ▼
ModSecurity (WAF)  ──blocks──▶  Wazuh (SIEM)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                Telegram         Cortex          Shuffle
              (real-time alert) (IP enrichment)  (orchestration)
                                                     │
                                                     ▼
                                                  TheHive
                                              (incident case)
```

See [`docs/topology.png`](docs/topology.png) for the full architecture diagram and [`docs/hosts.png`](docs/hosts.png) for the host inventory.

---

## Tech stack

| Layer | Component | Purpose |
|---|---|---|
| Target | DVWA (Docker) | Intentionally vulnerable web application |
| Prevention | ModSecurity + OWASP CRS 3.3.8 | Web application firewall, reverse-proxied in front of the target |
| Detection | Wazuh 4.14 | SIEM - log aggregation, custom detection rules mapped to MITRE ATT&CK |
| Enrichment | Cortex 3.1.8 | Automated IP reputation lookups (AbuseIPDB, VirusTotal) |
| Case management | TheHive 5.2 | Turns alerts into tracked, assignable incidents |
| Orchestration | Shuffle | Connects Wazuh alerts to TheHive case creation |
| Alerting | Telegram Bot API | Real-time notification for level 8+ alerts |

---

## Repository structure

```
soc-lab/
├── docs/
│   ├── topology.png              # network + data flow diagram
│   └── hosts.png                 # host inventory table
├── wazuh/
│   └── local_rules.xml           # custom detection rules (MITRE-mapped)
├── modsecurity/
│   └── dvwa-proxy.conf           # reverse proxy config placing the WAF in-path
├── integrations/
│   ├── custom-telegram.py        # Wazuh → Telegram alert script
│   └── custom-shuffle.py         # Wazuh → Cortex + Shuffle webhook script
├── soar/
│   ├── thehive-cortex-compose.yml
│   └── shuffle-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## Errors you might encounter

**ModSecurity was silently not blocking anything.** The target app runs in its own container with its own Apache instance, fully independent from the host Apache where ModSecurity was installed. Fixed by making the host Apache a reverse proxy in front of the container, so all traffic passes through the WAF first.

**Wazuh alerts never reached the SOAR webhook.** ModSecurity's JSON audit log ballooned to 30+ KB per event once triggered rules and OWASP CRS metadata were included — too large for Shuffle to process. Fixed with a purpose-built integration script that extracts only the fields the pipeline actually needs.

**Shuffle workers never started.** Docker was running in Swarm mode by default, and the orchestration engine (Orborus) couldn't dispatch work to a single-node Swarm cluster. Fixed with `docker swarm leave --force`.

**Filebeat was stuck in a crash loop.** A `seccomp`/kernel incompatibility caused silent `pthread_create` failures. Fixed by disabling the seccomp sandbox in Filebeat's config.


---

## Security note

All configuration files in this repository have had real credentials replaced with placeholders (`BOT_TOKEN`, `CORTEX_KEY`, `CHANGE_ME`, etc.). This is a personal lab running on an isolated `192.168.40.0/24` network — none of the IP addresses shown are internet-reachable.

---

## License

MIT — see [`LICENSE`](LICENSE).
