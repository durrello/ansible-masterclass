# Ansible Docker Lab — User Manual

This manual walks you through the complete lab environment, every playbook, and how to use them effectively.

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Architecture Overview](#architecture-overview)
3. [Configuration Reference](#configuration-reference)
4. [Playbook Guide](#playbook-guide)
   - [01 — Basics](#01--basics)
   - [02 — Intermediate](#02--intermediate)
   - [03 — Advanced](#03--advanced)
   - [04 — Multi-Group](#04--multi-group)
   - [Production Entry Point](#production-entry-point-siteyml)
5. [Playbook Template](#playbook-template)
6. [Execution Quick Reference](#execution-quick-reference)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Best Practices](#tips--best-practices)

---

## Environment Setup

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Docker | Run managed nodes as containers | [docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | Orchestrate multi-container lab | Included with Docker Desktop |
| Ansible | Automation engine | `pip install ansible` |
| SSH Keys | Passwordless auth to containers | `ssh-keygen` |

### Step-by-Step Setup

#### 1. Generate SSH Keys

```bash
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ""
```

The containers mount your `~/.ssh/id_rsa.pub` as the authorized key for both `root` and `devuser`.

#### 2. Build and Start Containers

```bash
docker-compose up -d
```

This builds the custom Ubuntu image (`Dockerfile.node`) and starts two containers.

#### 3. Verify Containers Are Running

```bash
docker ps
```

You should see `node1` and `node2` with their port mappings.

#### 4. Test Ansible Connectivity

```bash
ansible-playbook playbooks/01-basics/ping-test.yml
```

Expected output: both nodes return `pong`.

#### 5. (Optional) Test SSH Manually

```bash
ssh -i ~/.ssh/id_rsa -p 2222 devuser@127.0.0.1
ssh -i ~/.ssh/id_rsa -p 2223 devuser@127.0.0.1
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Your Machine (Control Node)        │
│                                                     │
│   ansible-playbook ──► inventory ──► SSH ──►        │
└──────────────────────────────┬──────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
     ┌──────────────┐  ┌──────────────┐
     │    node1     │  │    node2     │
     │  (web group) │  │  (db group)  │
     │  SSH: 2222   │  │  SSH: 2223   │
     │  HTTP: 8081  │  │  HTTP: 8082  │
     │  Ubuntu 22.04│  │  Ubuntu 22.04│
     └──────────────┘  └──────────────┘
```

Both nodes are in the `[node]` group. Additionally:
- **node1** is in the `[web]` group
- **node2** is in the `[db]` group

This lets you practice targeting specific groups of hosts.

---

## Configuration Reference

### ansible.cfg

```ini
[defaults]
inventory = ./inventory/inventory.ini
host_key_checking = False
retry_files_enabled = False
deprecation_warnings = False
forks = 20
```

| Setting | Purpose |
|---------|---------|
| `inventory` | Default inventory file path |
| `host_key_checking = False` | Skip SSH fingerprint prompts (lab only) |
| `retry_files_enabled = False` | Don't create `.retry` files on failure |
| `forks = 20` | Run tasks on up to 20 hosts in parallel |

### inventory/inventory.ini

Defines three host groups:

```ini
[node]          # All containers
node1           # SSH port 2222
node2           # SSH port 2223

[web]           # Web servers
node1

[db]            # Database servers
node2
```

Each host is configured with:
- `ansible_host=127.0.0.1`
- `ansible_port=2222` or `2223`
- `ansible_user=devuser`
- `ansible_ssh_private_key_file=~/.ssh/id_rsa`

### inventory/docker_inventory.py

A dynamic inventory script that auto-discovers running Docker containers and their SSH ports. Use it as an alternative:

```bash
ansible-playbook -i inventory/docker_inventory.py <playbook>
```

### Dockerfile.node

Builds an Ubuntu 22.04 image with:
- `openssh-server`, `python3`, `python3-apt`, `sudo`
- User `devuser:devpass` with `NOPASSWD` sudo
- SSH authorized_keys directory prepared
- Port 22 exposed

### docker-compose.yml

Runs two instances of the image:
- Maps SSH and HTTP ports to localhost
- Mounts your SSH public key into both containers

---

## Playbook Guide

### 01 — Basics

These playbooks teach fundamental Ansible modules and connectivity.

#### ping-test.yml

**What it does**: Verifies Ansible can connect to all nodes via SSH.

```bash
ansible-playbook playbooks/01-basics/ping-test.yml
```

**Concepts**: `ansible.builtin.ping` module, host groups, basic playbook structure.

**Run this first** after setting up the environment.

---

#### basic-apt.yml

**What it does**: Updates the APT cache and installs `nginx` + `git`.

```bash
ansible-playbook playbooks/01-basics/basic-apt.yml
```

**Concepts**: `apt` module, `update_cache`, installing multiple packages, `become: yes` for privilege escalation.

---

#### basic-setup.yml

**What it does**: Complete basic node provisioning — packages, services, and web content.

```bash
ansible-playbook playbooks/01-basics/basic-setup.yml
```

**Tasks**:
1. Update APT cache (with 1-hour validity)
2. Install nginx and git
3. Start and enable nginx
4. Deploy a welcome page with the hostname

**Concepts**: `gather_facts`, `cache_valid_time`, `service` module, `copy` module with inline content, Jinja2 `{{ inventory_hostname }}`.

---

#### file-module.yml

**What it does**: Creates directories and files on the remote nodes.

```bash
ansible-playbook playbooks/01-basics/file-module.yml
```

**Tasks**:
1. Create `/home/devuser/logs` directory (mode 0755)
2. Create `/home/devuser/logs/sample.txt` file (mode 0644)

**Concepts**: `file` module, `state: directory`, `state: touch`, file permissions.

---

#### debug-example.yml

**What it does**: Prints variables and dumps all host facts.

```bash
ansible-playbook playbooks/01-basics/debug-example.yml
```

**Tasks**:
1. Print a custom message using a variable
2. Display all `ansible_facts` for inspection

**Concepts**: `debug` module, `msg` vs `var`, Jinja2 templating, fact gathering.

---

#### nginx.yml

**What it does**: Minimal nginx install and start (no content deployment).

```bash
ansible-playbook playbooks/01-basics/nginx.yml
```

**Concepts**: Simplest possible service playbook — install package, start service.

---

### 02 — Intermediate

These playbooks introduce variables, loops, and structured data.

#### vars-example.yml

**What it does**: Installs packages defined in a variable list.

```bash
ansible-playbook playbooks/02-intermediate/vars-example.yml
```

**Key pattern**:
```yaml
vars:
  packages:
    - nginx
    - git
    - curl
tasks:
  - apt:
      name: "{{ packages }}"
```

**Concepts**: `vars` section, list variables, referencing variables with `{{ }}`.

---

#### loops-users.yml

**What it does**: Creates multiple user accounts using a loop.

```bash
ansible-playbook playbooks/02-intermediate/loops-users.yml
```

**Key pattern**:
```yaml
vars:
  users: [alice, bob, carol]
tasks:
  - user:
      name: "{{ item }}"
    loop: "{{ users }}"
```

**Concepts**: `loop` keyword, `{{ item }}` magic variable, `user` module.

---

#### users.yml

**What it does**: Creates users with structured data (name + shell).

```bash
ansible-playbook playbooks/02-intermediate/users.yml
```

**Key pattern**:
```yaml
vars:
  users:
    - name: alice
      shell: /bin/bash
    - name: bob
      shell: /bin/bash
tasks:
  - user:
      name: "{{ item.name }}"
      shell: "{{ item.shell }}"
    loop: "{{ users }}"
```

**Concepts**: Looping over dictionaries, accessing nested properties with `item.key`.

---

### 03 — Advanced

These playbooks demonstrate handlers, combined workflows, and data-driven automation.

#### handlers-example.yml

**What it does**: Deploys a web page and restarts nginx only if the file changed.

```bash
ansible-playbook playbooks/03-advanced/handlers-example.yml
```

**Key pattern**:
```yaml
tasks:
  - copy:
      content: "<h1>Hello</h1>"
      dest: /var/www/html/index.html
    notify: restart nginx

handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
```

**Concepts**: `notify`, `handlers`, idempotency — handlers only fire when a task reports "changed".

**Targets**: `[web]` group only (node1).

---

#### full-example.yml

**What it does**: Combines variables, loops, and handlers in a single playbook.

```bash
ansible-playbook playbooks/03-advanced/full-example.yml
```

**Tasks**:
1. Install packages from a variable list
2. Create users with group assignments (loop over dicts)
3. Deploy HTML content
4. Handler restarts nginx on change

**Concepts**: Integration of all intermediate concepts into a realistic workflow.

---

#### combined-playbook.yml

**What it does**: Multi-step node provisioning — cache, packages, directories, content, services.

```bash
ansible-playbook playbooks/03-advanced/combined-playbook.yml
```

**Tasks**:
1. Update APT cache
2. Install nginx
3. Create `/home/devuser/project` directory
4. Deploy welcome page
5. Start and enable nginx

**Concepts**: Realistic deployment sequence combining multiple modules.

---

#### service-install.yml

**What it does**: Data-driven service installation with conditional logic.

```bash
ansible-playbook playbooks/03-advanced/service-install.yml
```

**Key pattern**:
```yaml
vars:
  services:
    - name: nginx
      package: nginx
      port: 80
    - name: git
      package: git
tasks:
  - apt:
      name: "{{ item.package }}"
    loop: "{{ services }}"
  - service:
      name: "{{ item.name }}"
      state: started
    loop: "{{ services }}"
    when: item.name != "git"
```

**Concepts**: Data-driven design, `when` conditionals, separating data from logic.

---

### 04 — Multi-Group

These playbooks target specific inventory groups and demonstrate multi-play patterns.

#### nginx-config.yml

**What it does**: Configures nginx on web servers only.

```bash
ansible-playbook playbooks/04-multi-group/nginx-config.yml
```

**Targets**: `[web]` group (node1 only).

**Concepts**: Group-specific targeting, handler pattern.

---

#### manage-service.yml

**What it does**: Ensures nginx is running, enabled, and performs a restart.

```bash
ansible-playbook playbooks/04-multi-group/manage-service.yml
```

**Concepts**: Service state management — `started` vs `restarted`, `enabled: yes`.

---

#### full-setup.yml

**What it does**: Multi-play playbook that provisions different node types differently.

```bash
ansible-playbook playbooks/04-multi-group/full-setup.yml
```

**Play 1** (web group — node1):
- Install nginx
- Deploy homepage

**Play 2** (db group — node2):
- Install mariadb-server
- Start mariadb service

**Concepts**: Multiple plays in one file, group-specific provisioning, different software stacks per role.

---

### Production Entry Point: site.yml

```bash
ansible-playbook site.yml
```

This is the top-level playbook that applies the `service_install` role to all nodes. It represents the Ansible best practice of using roles for reusable, organized automation.

**Note**: The `service_install` role must exist in a `roles/` directory for this to work. The role's logic mirrors `playbooks/03-advanced/service-install.yml`.

---

## Playbook Template

Use `playbooks/playbook-template.yml` as a starting point for new playbooks:

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

---

## Execution Quick Reference

| Playbook | Command | What You'll See |
|----------|---------|-----------------|
| Ping test | `ansible-playbook playbooks/01-basics/ping-test.yml` | Both nodes return pong |
| Basic setup | `ansible-playbook playbooks/01-basics/basic-setup.yml` | Nginx installed + page deployed |
| Create users | `ansible-playbook playbooks/02-intermediate/loops-users.yml` | alice, bob, carol created |
| Handlers | `ansible-playbook playbooks/03-advanced/handlers-example.yml` | Nginx restarted on change |
| Multi-group | `ansible-playbook playbooks/04-multi-group/full-setup.yml` | Nginx on web, MariaDB on db |
| Production | `ansible-playbook site.yml` | Full role-based deployment |

### Common Flags

```bash
# Verbose output (add more v's for more detail)
ansible-playbook -v playbook.yml
ansible-playbook -vvv playbook.yml

# Dry run (check mode — no changes made)
ansible-playbook --check playbook.yml

# Limit to specific host
ansible-playbook --limit node1 playbook.yml

# Use dynamic inventory
ansible-playbook -i inventory/docker_inventory.py playbook.yml

# Override a variable
ansible-playbook -e "packages=['nginx','curl']" playbook.yml
```

---

## Troubleshooting

### SSH Connection Refused

```
fatal: [node1]: UNREACHABLE! => {"msg": "Failed to connect to the host via ssh"}
```

**Fix**:
1. Check containers are running: `docker ps`
2. Verify SSH keys exist: `ls ~/.ssh/id_rsa.pub`
3. Rebuild containers: `docker-compose down && docker-compose up -d --build`

---

### Host Key Verification Failed

```
Host key verification failed.
```

**Fix**: Already handled by `ansible.cfg` (`host_key_checking = False`). If running ad-hoc commands, add `-o StrictHostKeyChecking=no`:

```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 2222 devuser@127.0.0.1
```

---

### Python Not Found on Remote

```
MODULE FAILURE: No module named 'apt'
```

**Fix**: The Dockerfile installs `python3` and `python3-apt`. If you see this, rebuild:

```bash
docker-compose down
docker-compose up -d --build
```

---

### Playbook Changes Not Taking Effect

**Possible causes**:
- Handlers only run when notified (task must report "changed")
- APT cache might be stale — add `update_cache: yes`
- Run with `-v` to see what's happening

```bash
ansible-playbook -v playbooks/03-advanced/handlers-example.yml
```

---

### Port Already in Use

```
Error: Bind for 0.0.0.0:2222 failed: port is already allocated
```

**Fix**: Stop conflicting containers or change ports in `docker-compose.yml`.

```bash
docker-compose down
docker ps -a  # check for orphaned containers
docker-compose up -d
```

---

## Tips & Best Practices

1. **Start with ping-test.yml** — always verify connectivity before running complex playbooks.

2. **Use `--check` mode** — preview changes without applying them:
   ```bash
   ansible-playbook --check playbooks/01-basics/basic-setup.yml
   ```

3. **Read the output** — Ansible color codes results:
   - **Green** = OK (no change needed)
   - **Yellow** = Changed (task made a modification)
   - **Red** = Failed (something went wrong)

4. **Idempotency** — run any playbook multiple times safely. The second run should show all green (no changes).

5. **Use variables** — avoid hardcoding values. Put them in `vars:` or external files.

6. **Handlers save restarts** — use `notify` instead of always restarting services.

7. **Group your hosts** — target specific groups (`web`, `db`) instead of `all` when tasks are role-specific.

8. **Tear down cleanly** — when done:
   ```bash
   docker-compose down
   ```
