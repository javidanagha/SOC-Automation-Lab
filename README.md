<div align="center">

# 🛡️ SOC Lab

**A fully automated detection-to-response security pipeline, built from scratch.**

ModSecurity WAF → Wazuh SIEM → TheHive / Cortex / Shuffle SOAR → Telegram

<br>

![Wazuh](https://img.shields.io/badge/Wazuh-4.14-1F3864?style=for-the-badge&logo=wazuh&logoColor=white)
![ModSecurity](https://img.shields.io/badge/ModSecurity-OWASP%20CRS%203.3.8-1E7B4D?style=for-the-badge)
![TheHive](https://img.shields.io/badge/TheHive-5.2-D68910?style=for-the-badge)
![Cortex](https://img.shields.io/badge/Cortex-3.1.8-D68910?style=for-the-badge)
![Shuffle](https://img.shields.io/badge/Shuffle-SOAR-D68910?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

<br>

## 📌 Overview

An attacker sends a request against a damn vulnerable web app (DVWA). The request is inspected and blocked by a WAF, logged and matched against custom detection rules by a SIEM, enriched with threat intelligence, and turned into a tracked incident — all automatically, with no manual step in between.

```
                              🎯 Attacker
                                  │
                                  ▼
              🧱 ModSecurity (WAF)  ──blocks──▶  🔍 Wazuh (SIEM)
                                                       │
                        ┌──────────────────┬───────────┴───────────┐
                        ▼                  ▼                       ▼
                  📨 Telegram         🌐 Cortex               🔀 Shuffle
                 (real-time alert)  (IP enrichment)         (orchestration)
                                                                    │
                                                                    ▼
                                                              🗂️ TheHive
                                                            (incident case)
```

<div align="center">

📊 [`docs/topology.png`](docs/topology.png) — full architecture diagram &nbsp;•&nbsp; 🖥️ [`docs/hosts.png`](docs/hosts.png) — host inventory

</div>

---

## ⚙️ Tech stack

| Layer | Component | Purpose |
|:---|:---|:---|
| 🎯 **Target** | DVWA (Docker) | Intentionally vulnerable web application |
| 🧱 **Prevention** | ModSecurity + OWASP CRS 3.3.8 | Web application firewall, reverse-proxied in front of the target |
| 🔍 **Detection** | Wazuh 4.14 | SIEM — log aggregation, custom detection rules mapped to MITRE ATT&CK |
| 🌐 **Enrichment** | Cortex 3.1.8 | Automated IP reputation lookups (AbuseIPDB, VirusTotal) |
| 🗂️ **Case management** | TheHive 5.2 | Turns alerts into tracked, assignable incidents |
| 🔀 **Orchestration** | Shuffle | Connects Wazuh alerts to TheHive case creation |
| 📨 **Alerting** | Telegram Bot API | Real-time notification for level 8+ alerts |

---

## 📁 Repository structure

```
soc-lab/
├── 📊 docs/
│   ├── topology.png              # network + data flow diagram
│   └── hosts.png                 # host inventory table
├── 🔍 wazuh/
│   └── local_rules.xml           # custom detection rules (MITRE-mapped)
├── 🧱 modsecurity/
│   └── dvwa-proxy.conf           # reverse proxy config placing the WAF in-path
├── 🔌 integrations/
│   ├── custom-telegram.py        # Wazuh → Telegram alert script
│   └── custom-shuffle.py         # Wazuh → Cortex + Shuffle webhook script
├── 🔀 soar/
│   ├── thehive-cortex-compose.yml
│   └── shuffle-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🧩 Key challenges solved

> Every non-trivial part of this build came from debugging, not documentation. Four issues stood out:

<details>
<summary><b>1️⃣ ModSecurity was blocking nothing, even though it was installed correctly</b></summary>
<br>

The target application runs inside a Docker container with its own internal Apache server. ModSecurity, however, was installed on the *host's* Apache — a completely separate process. Traffic sent to the container never passed through the host, so the WAF never saw it.

**Fix:** configured the host Apache as a reverse proxy in front of the container. All traffic now hits ModSecurity first, before ever reaching the application.
</details>

<details>
<summary><b>2️⃣ Wazuh detected attacks correctly, but alerts never reached the SOAR pipeline</b></summary>
<br>

ModSecurity's audit log includes every matched rule, its full regex pattern, and OWASP CRS metadata — a single event could balloon past 30 KB of JSON. Shuffle's webhook couldn't handle payloads that large and silently dropped them.

**Fix:** wrote a small integration script that extracts only the handful of fields the pipeline actually needs (source IP, rule ID, request line, etc.) before forwarding — typically under 1 KB per alert.
</details>

<details>
<summary><b>3️⃣ Shuffle's automation workflows never executed — stuck in "Executing" forever</b></summary>
<br>

By default, Shuffle runs its worker engine (Orborus) in Docker Swarm mode, which expects a multi-node cluster to schedule work across. On a single VM, there was nowhere for it to dispatch jobs, so they silently never started.

**Fix:** `docker swarm leave --force` — drops Swarm mode and lets Orborus run workers as regular containers instead.
</details>

<details>
<summary><b>4️⃣ Filebeat kept crashing on startup, so no logs reached the indexer</b></summary>
<br>

The crash was `pthread_create failed: Operation not permitted` — caused by Filebeat's built-in seccomp syscall filter being incompatible with the host's kernel version.

**Fix:** added `seccomp.enabled: false` to Filebeat's config to disable the sandbox.
</details>

---

## 🔒 Security note

All configuration files in this repository have had real credentials replaced with placeholders (`BOT_TOKEN`, `CORTEX_KEY`, `CHANGE_ME`, etc.). This is a personal lab running on an isolated `192.168.40.0/24` network — none of the IP addresses shown are internet-reachable.

---

<div align="center">

📄 **License:** [MIT](LICENSE)

</div>
