# Ansible Docker Lab

A hands-on Ansible learning environment using Docker containers as managed nodes. Spin up two Ubuntu containers, connect via SSH, and work through progressively complex playbooks — from basic pings to multi-group deployments with roles and handlers.

## Project Structure

```
ansible-docker-lab/
├── ansible.cfg                  # Ansible configuration
├── docker-compose.yml           # Container orchestration (2 nodes)
├── Dockerfile.node              # Ubuntu 22.04 SSH-enabled image
├── site.yml                     # Production entry point (role-based)
├── inventory/
│   ├── inventory.ini            # Static inventory (default)
│   └── docker_inventory.py      # Dynamic inventory (auto-discovers containers)
├── playbooks/
│   ├── playbook-template.yml    # Blank playbook scaffold
│   ├── 01-basics/               # Connectivity, packages, files, debug
│   ├── 02-intermediate/         # Variables, loops, user management
│   ├── 03-advanced/             # Handlers, combined workflows, data-driven tasks
│   └── 04-multi-group/          # Group-specific and multi-play deployments
└── docs/
    └── USER_MANUAL.md           # Full walkthrough and reference
```

## Quick Start

```bash
# 1. Generate SSH keys (skip if you already have them)
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ""

# 2. Build and start the lab containers
docker-compose up -d

# 3. Verify Ansible can reach both nodes
ansible-playbook playbooks/01-basics/ping-test.yml

# 4. Run the full production playbook
ansible-playbook site.yml

# 5. Check the deployed web pages
curl http://localhost:8081
curl http://localhost:8082
```

## Prerequisites

- Docker & Docker Compose
- Ansible (`pip install ansible`)
- SSH key pair at `~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`

## Lab Environment

| Container | SSH Port | HTTP Port | Inventory Groups |
|-----------|----------|-----------|------------------|
| node1     | 2222     | 8081      | node, web        |
| node2     | 2223     | 8082      | node, db         |

Both containers run Ubuntu 22.04 with:
- SSH server + Python 3 (Ansible requirement)
- User `devuser` with passwordless sudo
- Your SSH public key pre-loaded for key-based auth

## Playbook Progression

Work through the playbooks in order to build your Ansible skills:

| Level | Directory | Concepts |
|-------|-----------|----------|
| 1 | `01-basics/` | Ping, apt, services, files, debug |
| 2 | `02-intermediate/` | Variables, loops, user management |
| 3 | `03-advanced/` | Handlers, notify, combined workflows, data-driven tasks |
| 4 | `04-multi-group/` | Group targeting, multi-play, service management |
| Prod | `site.yml` | Roles pattern |

## Useful Commands

```bash
# Tear down the lab
docker-compose down

# Rebuild containers from scratch
docker-compose up -d --build

# Run with verbose output
ansible-playbook -v playbooks/01-basics/basic-setup.yml

# Use dynamic inventory instead of static
ansible-playbook -i inventory/docker_inventory.py playbooks/01-basics/ping-test.yml

# SSH into a container manually
ssh -i ~/.ssh/id_rsa -p 2222 devuser@127.0.0.1
```

## Documentation

See [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) for the complete walkthrough, playbook reference, and troubleshooting guide.

## License

This project is for educational purposes.


---

<div align="center">

### Built by

**Durrell Gemuh** - Founder @ NextGen Playground | DevOps & Cloud Infrastructure Engineer | AWS Community Builder

[![Portfolio](https://img.shields.io/badge/Portfolio-durrellgemuh.com-000?style=flat-square&logo=vercel)](https://durrellgemuh.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-durrello-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/durrello/)
[![Dev.to](https://img.shields.io/badge/Dev.to-durrello-0A0A0A?style=flat-square&logo=devdotto)](https://dev.to/durrello)
[![X](https://img.shields.io/badge/X-@durrelloo-000?style=flat-square&logo=x)](https://x.com/durrelloo)
[![GitHub](https://img.shields.io/badge/GitHub-durrello-181717?style=flat-square&logo=github)](https://github.com/durrello)
[![Email](https://img.shields.io/badge/Email-durrell.gemuh.a@gmail.com-EA4335?style=flat-square&logo=gmail)](mailto:durrell.gemuh.a@gmail.com)

---

⭐ **Star this repo** if you found it useful - it helps others discover it!

</div>
