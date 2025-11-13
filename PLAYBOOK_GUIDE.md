# Ansible Docker Lab - Complete Playbook Guide & Environment Setup

## Environment Setup

### Prerequisites
Ensure you have installed:
- Docker & Docker Compose
- Ansible (`pip install ansible`)
- SSH keys (`ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ""`)

### Initial Setup Steps

#### 1. Generate SSH Keys (if not already present)
```bash
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ""
```
The containers expect your public key to be available at `~/.ssh/id_rsa.pub` for passwordless SSH access.

#### 2. Build and Start Docker Containers
```bash
docker-compose up -d
```

This creates two Ubuntu 22.04 containers:
- **node1**: Accessible on localhost:2222 (SSH) and :8081 (HTTP)
- **node2**: Accessible on localhost:2223 (SSH) and :8082 (HTTP)

#### 3. Verify Setup
```bash
# Check running containers
docker ps

# Test SSH connectivity (optional)
ssh -i ~/.ssh/id_rsa -p 2222 devuser@127.0.0.1

# Verify Ansible connectivity
ansible-playbook ping-test.yml
```

### Environment Configuration Files

#### `ansible.cfg`
Main Ansible configuration:
- **inventory**: Points to `./inventory.ini` (can use `./docker_inventory.py` for dynamic)
- **host_key_checking**: Disabled for lab environment
- **forks**: Set to 20 for parallel execution
- **retry_files_enabled**: Disabled (no .retry files generated)

#### `inventory.ini`
Static inventory defining:
- **[node]**: All containers (node1, node2)
- **[web]**: node1 (port 2222)
- **[db]**: node2 (port 2223)

Each host configured with:
- `ansible_host=127.0.0.1` (localhost)
- `ansible_port` (2222 or 2223)
- `ansible_user=devuser` (unprivileged user with sudo)
- `ansible_ssh_private_key_file=~/.ssh/id_rsa`

#### `Dockerfile.node`
Creates Ubuntu 22.04 containers with:
- SSH server + Python 3 (required for Ansible)
- User `devuser:devpass` with passwordless sudo
- Root SSH login enabled
- SSH authorized_keys populated from host's public key

#### `docker-compose.yml`
Orchestrates two containers:
- Maps ports 2222 → node1 SSH, 2223 → node2 SSH
- Maps ports 8081 → node1 HTTP, 8082 → node2 HTTP
- Mounts SSH public key for both root and devuser

#### `docker_inventory.py`
Dynamic inventory script (alternative to static `inventory.ini`):
- Parses running Docker containers
- Extracts SSH ports automatically
- Usage: `ansible-playbook -i docker_inventory.py <playbook.yml>`

---

## Playbook Reference Guide

### Core Playbooks

#### **site.yml** ⭐ (Production Entry Point)
**Purpose**: Apply the `service_install` role to all nodes  
**Targets**: `[node]` group (all containers)  
**Privileges**: Elevated (`become: yes`)

```bash
ansible-playbook site.yml
```

**What it does**:
1. Installs nginx and git packages (from role vars)
2. Starts and enables services (nginx only, git excluded via `when`)
3. Deploys HTML homepage to `/var/www/html/index.html`
4. Triggers handler to restart nginx on config changes

---

### Basic Examples (Learning/Reference)

#### **ping-test.yml** 🔗
**Purpose**: Test Ansible connectivity to all nodes  
**Targets**: `[node]` group  
**Complexity**: Trivial

```bash
ansible-playbook ping-test.yml
```

**What it does**: Pings all nodes to verify SSH access. First step after environment setup.

---

#### **basic-apt.yml** 📦
**Purpose**: Demonstrate basic package installation  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook basic-apt.yml
```

**What it does**:
1. Updates APT package cache
2. Installs nginx and git

**Learning value**: Shows `apt` module usage with package arrays.

---

#### **basic-setup.yml** 🔧
**Purpose**: Full basic node setup (packages, services, content)  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook basic-setup.yml
```

**What it does**:
1. Gathers host facts (`gather_facts: yes`)
2. Updates APT cache with 1-hour validity
3. Installs nginx and git
4. Starts and enables nginx service
5. Deploys welcome page with hostname

**Learning value**: Combines `apt`, `service`, and `copy` modules. Shows facts usage.

---

### Intermediate Examples (Patterns & Techniques)

#### **vars-example.yml** 📝
**Purpose**: Demonstrate variables in playbooks  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook vars-example.yml
```

**What it does**:
- Defines variable list: `packages: [nginx, git, curl]`
- Installs packages via variable reference: `apt: name: "{{ packages }}"`

**Learning value**: Shows how to use `vars` section for cleaner playbooks.

---

#### **loops-users.yml** 🔄
**Purpose**: Demonstrate loops for bulk user creation  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook loops-users.yml
```

**What it does**:
1. Defines user list: alice, bob, carol
2. Loops through list creating each user: `loop: "{{ users }}"`
3. Sets shell to `/bin/bash` for all

**Learning value**: Shows `loop` syntax and `{{ item }}` variable reference.

---

#### **file-module.yml** 📂
**Purpose**: Demonstrate file/directory operations  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook file-module.yml
```

**What it does**:
1. Creates `/home/devuser/logs` directory (mode 0755)
2. Creates `/home/devuser/logs/sample.txt` (mode 0644)

**Learning value**: Shows `file` module for directory and file creation.

---

#### **debug-example.yml** 🐛
**Purpose**: Demonstrate debugging output  
**Targets**: `[node]` group  
**Privileges**: Not required

```bash
ansible-playbook debug-example.yml
```

**What it does**:
1. Outputs custom message: `"My variable is: Hello from <hostname>"`
2. Dumps all host facts (for inspection)

**Learning value**: Shows `debug` module for troubleshooting. Useful for inspecting Ansible facts.

---

#### **users.yml** 👥
**Purpose**: Create user accounts with shell specification  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook users.yml
```

**What it does**:
1. Loops over user list with name and shell properties
2. Creates each user with specified shell

**Learning value**: Shows loop with dict items (structured data).

---

### Advanced Examples (Handlers, Multi-Play)

#### **handlers-example.yml** 🔔
**Purpose**: Demonstrate handler pattern (notify/listen)  
**Targets**: `[web]` group (node1 only)  
**Privileges**: Elevated

```bash
ansible-playbook handlers-example.yml
```

**What it does**:
1. Deploys `index.html` to `/var/www/html/`
2. Uses `notify: - restart nginx` to trigger handler if file changes
3. Handler restarts nginx service (only runs if notified)

**Learning value**: Shows when handlers execute (at end of play if notified). Handlers prevent unnecessary restarts.

---

#### **full-example.yml** 🎯
**Purpose**: Complete example combining variables, loops, and handlers  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook full-example.yml
```

**What it does**:
1. Defines package list + user list with groups
2. Installs packages (list form)
3. Creates users with group assignment (loop with dict)
4. Deploys HTML homepage
5. Handler restarts nginx on content change

**Learning value**: Shows integration of multiple concepts: vars, loops, handlers, and multi-module tasks.

---

#### **combined-playbook.yml** ⚙️
**Purpose**: Combined setup with packages, directories, and services  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook combined-playbook.yml
```

**What it does**:
1. Updates APT cache
2. Installs nginx
3. Creates `/home/devuser/project` directory
4. Deploys welcome page
5. Starts and enables nginx service

**Learning value**: Realistic multi-step deployment combining file creation, package install, and service management.

---

### Role-Based Playbooks

#### **service-install.yml** 🛠️ (Standalone Service Install)
**Purpose**: Demonstrate data-driven service installation  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook service-install.yml
```

**What it does**:
1. Defines services as list of dicts: `{name, package, port}`
2. Loops to install packages from each service definition
3. Loops to start services (excludes git via `when: item.name != "git"`)
4. Deploys HTML homepage
5. Handler restarts nginx on changes

**Learning value**: Shows separation of data (vars) and logic (tasks). Same task loop handles both nginx and git installation.

---

#### **site.yml** (via Role)
**Purpose**: Apply `service_install/` role  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook site.yml
```

**What it does**: Runs the `service_install/` role (identical to `service-install.yml`).  
**Learning value**: Shows Ansible role pattern for reusability.

**Role structure**:
```
service_install/
  tasks/main.yml      → Task definitions
  vars/main.yml       → Service data definitions
  handlers/main.yml   → Restart handlers
```

---

### Web/Database Group Playbooks

#### **nginx.yml** 🌐
**Purpose**: Minimal nginx setup  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook nginx.yml
```

**What it does**:
1. Installs nginx package
2. Starts nginx service

**Learning value**: Simplest nginx playbook. No content deployment.

---

#### **nginx-config.yml** 🔧
**Purpose**: Configure nginx web servers with content  
**Targets**: `[web]` group (node1 only)  
**Privileges**: Elevated

```bash
ansible-playbook nginx-config.yml
```

**What it does**:
1. Deploys custom `index.html` with hostname
2. Notifies handler to restart nginx

**Learning value**: Targets specific group `[web]`. Shows conditional deployment.

---

#### **manage-service.yml** 🎛️
**Purpose**: Manage nginx service state  
**Targets**: `[node]` group  
**Privileges**: Elevated

```bash
ansible-playbook manage-service.yml
```

**What it does**:
1. Ensures nginx is running and enabled on boot
2. Explicitly restarts nginx

**Learning value**: Shows service state management (started vs restarted).

---

#### **full-setup.yml** 📊
**Purpose**: Multi-play setup for different host groups  
**Targets**: `[web]` (node1) + `[db]` (node2)  
**Privileges**: Elevated

```bash
ansible-playbook full-setup.yml
```

**What it does**:
- **Play 1 (web servers)**:
  1. Installs nginx
  2. Deploys homepage with hostname
- **Play 2 (database servers)**:
  1. Installs mariadb-server
  2. Starts mariadb service

**Learning value**: Multi-play pattern for different node types. Demonstrates group-specific provisioning.

---

### Template/Reference Files

#### **playbook.yml** 📋
**Purpose**: Template showing playbook structure  
**Status**: Not executable (placeholder)

```yaml
---
- name: <Play description>
  hosts: <target group or host>
  become: yes | no
  vars:
    <variable_name>: <value>
  tasks:
    - name: <Task 1>
      <module>: <parameters>
    - name: <Task 2>
      <module>: <parameters>
  handlers:
    - name: <Handler task>
      <module>: <parameters>
```

**Learning value**: Reference structure for new playbooks.

---

## Playbook Execution Matrix

| Playbook | Targets | Privilege | Use Case |
|----------|---------|-----------|----------|
| ping-test.yml | node | No | Test connectivity |
| basic-apt.yml | node | Yes | Learn apt module |
| basic-setup.yml | node | Yes | Complete basic setup |
| vars-example.yml | node | Yes | Learn variables |
| loops-users.yml | node | Yes | Learn loops |
| file-module.yml | node | Yes | Learn file operations |
| debug-example.yml | node | No | Learn debugging |
| users.yml | node | Yes | Create users |
| handlers-example.yml | web | Yes | Learn handlers |
| full-example.yml | node | Yes | Integration example |
| combined-playbook.yml | node | Yes | Realistic setup |
| service-install.yml | node | Yes | Data-driven services |
| site.yml | node | Yes | Production playbook |
| nginx.yml | node | Yes | Minimal nginx |
| nginx-config.yml | web | Yes | Configure web servers |
| manage-service.yml | node | Yes | Service management |
| full-setup.yml | web+db | Yes | Multi-group setup |

---

## Quick Start Commands

```bash
# 1. Initialize environment
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ""
docker-compose up -d

# 2. Test connectivity
ansible-playbook ping-test.yml

# 3. Run production playbook
ansible-playbook site.yml

# 4. Verify deployment
curl http://localhost:8081
curl http://localhost:8082

# 5. Access container
ssh -i ~/.ssh/id_rsa -p 2222 devuser@127.0.0.1
```

---

## Troubleshooting

### SSH Connection Refused
- Ensure SSH keys exist: `ls ~/.ssh/id_rsa`
- Check containers running: `docker ps`
- Verify ports mapped: `docker port node1`

### "SSH host key verification failed"
- Playbooks disable this in `ansible.cfg` (`host_key_checking = False`)
- Or manually: `ssh-keyscan -p 2222 127.0.0.1 >> ~/.ssh/known_hosts`

### "Python not found on remote"
- Dockerfile installs Python 3 and `python3-apt`
- Verify: `ansible node1 -m setup -a 'filter=*python*'`

### Playbook changes not applied
- Check handler notifications: `notify:` + `handlers:` section
- Run with `-v` for verbose output: `ansible-playbook -v <playbook>`

