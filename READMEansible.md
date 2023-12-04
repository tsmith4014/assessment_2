## Ansible Configuration for Flask Application Deployment

Ansible automates the deployment and configuration of the Flask application and MySQL database on AWS.

### Ansible Playbooks

#### Main Playbook (`/Ansible-project/site.yml`)

```yaml
---
- hosts: type_database
  become: true
  vars_files:
    - roles/mysql/vars/secret.yml
  roles:
    - common
    - mysql

- hosts: type_backend
  become: true
  vars_files:
    - roles/mysql/vars/secret.yml
    - roles/flask_backend/vars/main.yml
  roles:
    - common
    - flask_backend
    - s3_upload
```

### Ansible Configuration File (`/ansible-project/ansible.cfg`)

```ini
[defaults]
private_key_file = /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/cpdevopsew-eu-west-2.pem
remote_user = ubuntu
host_key_checking = False
```

---

## Ansible Tasks for Flask Application Deployment

### MySQL Role Configuration

#### Tasks (`/ansible-project/roles/mysql/tasks/main.yml`)

```yaml
- name: Install MySQL server
  apt:
    name: "mysql-server"
    state: present
  become: true

- name: Start MySQL service and enable on boot
  systemd:
    name: mysql
    state: started
    enabled: yes
  become: true

- name: Check MySQL root user's authentication method
  command: mysql -u root -p'{{ vault_mysql_root_password }}' -e "SELECT plugin FROM mysql.user WHERE User = 'root'"
  register: root_auth_method
  ignore_errors: true
  become: true

- name: Change MySQL root user's authentication method
  mysql_query:
    login_user: root
    login_unix_socket: /var/run/mysqld/mysqld.sock
    query:
      - ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{{ vault_mysql_root_password }}';
      - FLUSH PRIVILEGES;
  become: true
  when: "'mysql_native_password' not in root_auth_method.stdout"

- name: Allow remote connections to MySQL
  lineinfile:
    path: /etc/mysql/mysql.conf.d/mysqld.cnf
    line: "bind-address = 0.0.0.0"
    regexp: "^bind-address"
  become: true

- name: Restart MySQL service
  systemd:
    name: mysql
    state: restarted
  become: true

- name: Create todo_db database
  mysql_db:
    name: todo_db
    state: present
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
  become: true

- name: Create MySQL user for Flask application
  mysql_user:
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
    name: "{{ vault_mysql_user }}"
    password: "{{ vault_mysql_user_password }}"
    host: "%"
    state: present
  become: true

- name: Grant all privileges to MySQL user for Flask application
  mysql_user:
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
    name: "{{ vault_mysql_user }}"
    host: "%"
    priv: "*.*:ALL"
    state: present
  become: true
```

### Flask Backend Role Configuration

#### Tasks (`/ansible-project/roles/flask_backend/tasks/main.yml`)

```yaml
- name: Get backend host IP
  set_fact:
    backend_host_ip: "{{ (hostvars[groups['type_backend'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"

- name: Debug env_vars
  debug:
    var: env_vars

- name: Debug MYSQL_DATABASE_IP
  debug:
    msg: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
  run_once: true

- name: Install MySQL client
  apt:
    name: mysql-client
    state: present
  become: true

- name: Clone the Flask application repository
  git:
    repo: "{{ git_repo }}"
    dest: "{{ project_path }}"
    version: "env"
  become: true

- name: Update API_URL in index.html
  lineinfile:
    path: "{{ project_path }}/index.html"
    regexp: 'const API_URL\s*=\s*"http://localhost"; // replace with your API endpoint'
    line: "        const API_URL = 'http://{{ backend_host_ip }}';"
  become: true

- name: Display the contents of index.html
  command: cat "{{ project_path }}/index.html"
  register: output
  changed_when: false

- name: Print the contents of index.html
  debug:
    var: output.stdout_lines

- name: Copy gunicorn_config.py
  copy:
    src: "{{ role_path }}/templates/gunicorn_config.py"
    dest: "{{ project_path }}/gunicorn_config.py"
    owner: ubuntu
    group: ubuntu
    mode: "0644"
  become: true

- name: Create a virtual environment
  command:
    cmd: python3 -m venv "{{ virtualenv_path }}"
    creates: "{{ virtualenv_path }}"
  become: true

- name: Install Python dependencies
  pip:
    requirements: "{{ project_path }}/{{ requirements_file }}"
    virtualenv: "{{ virtualenv_path }}"
  become: true

- name: Install Gunicorn
  pip:
    name: gunicorn
    virtualenv: "{{ virtualenv_path }}"
  become: true

- name: Debug MYSQL_DATABASE_PORT
  debug:
    var: env_vars.MYSQL_DATABASE_PORT

- name: Set environment variables
  lineinfile:
    path: "{{ virtualenv_path }}/bin/activate"
    line: "export {{ item.key }}={{ item.value }}"
    state: present
  loop: "{{ env_vars | dict2items }}"
  become: true

- name: Print environment variables
  debug:
    msg: "{{ ansible_env }}"

- name: Create environment file
  template:
    src: env.j2
    dest: "{{ project_path }}/.env"
  vars:
    MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
    MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
    MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
    MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
    MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
  become: true

- name: Print .env file
  command: cat "{{ project_path }}/.env"
  register: env_file
  changed_when: false

- name: Show .env file
  debug:
    var: env_file.stdout_lines

- name: Create systemd service file for the todolist
  template:
    src: todolist.service.j2
    dest: /etc/systemd/system/todolist.service
    mode: "0644"
  vars:
    MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
    MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
    MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
    MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
    MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
  become: true

- name: Reload systemd to read new todolist service
  systemd:
    daemon_reload: yes
  become: true

- name: Enable and start todolist service
  systemd:
    name: todolist
    enabled: yes
    state: started
  become: true

- name: Check todolist service status
  command: systemctl status todolist
  register: todolist_status
  changed_when: false
  ignore_errors: true
```

---

#### Templates

- **Gunicorn Configuration (`/ansible-project/roles/flask_backend/templates/gunicorn_config.py`):**

```python
bind = "0.0.0.0:80"
workers = 4
preload_app = True
```

- **Systemd Service File (`/ansible-project/roles/flask_backend/templates/todolist.service.j2`):**

```jinja

  [Unit]
Description=Gunicorn instance to serve todolist flask app

Wants=network.target
After=syslog.target network-online.target

[Service]
Type=simple
WorkingDirectory={{ project_path }}
ExecStart={{ virtualenv_path }}/bin/gunicorn todo:app -c {{ project_path }}/gunicorn_config.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Environment File Template (`/ansible-project/roles/flask_backend/templates/env.j2`)

This template file creates an environment configuration file for the Flask application:

```jinja
MYSQL_DATABASE_HOST={{ MYSQL_DATABASE_HOST }}
MYSQL_DATABASE_USER={{ MYSQL_DATABASE_USER }}
MYSQL_DATABASE_PASSWORD={{ MYSQL_DATABASE_PASSWORD }}
MYSQL_DATABASE_DB={{ MYSQL_DATABASE_DB }}
MYSQL_DATABASE_PORT={{ MYSQL_DATABASE_PORT }}
```

This template is used to set up necessary environment variables required by the Flask application, ensuring that it can connect to the MySQL database correctly.

---

#### Variables

(`/ansible-project/roles/flask_backend/vars/main.yml`)

```yaml
system_packages:
  - python3-pip
  - python3-venv
  - git
  - build-essential
  - libmysqlclient-dev
git_repo: "https://github.com/chandradeoarya/todolist-flask.git"
project_path: "/home/ubuntu/todolist-flask"
virtualenv_path: "{{ project_path }}/venv"
gunicorn_bind: "0.0.0.0:80"
requirements_file: "requirements.txt"
env_vars:
  FLASK_APP: "todo.py"
  FLASK_ENV: "development"
  MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '') | replace('-', '.') }}"
  MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
  MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
  MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
  MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
```

(`/ansible-project/roles/mysql/vars/main.yml`)

This file contains variables specific to the MySQL role:

```yaml
system_packages:
  - mysql-server
  - python3-pymysql

mysql_root_password: "{{ vault_mysql_root_password }}"
mysql_user: "{{ vault_mysql_user }}"
mysql_user_password: "{{ vault_mysql_user_password }}"
```

These variables include the system packages needed for MySQL setup, the root password, and the user credentials for the MySQL database. The `vault_mysql_root_password`, `vault_mysql_user`, and `vault_mysql_user_password` are stored in an Ansible Vault for security.

---

### Common Role Configuration

#### Tasks (`/ansible-project/roles/common/tasks/main.yml`)

```yaml
- name: Update all system packages to latest version
  apt:
    update_cache: yes
    upgrade: "dist"
    cache_valid_time: 3600
  become: true

- name: Install required system packages
  apt:
    name: "{{ item }}"
    state: latest
  loop: "{{ system_packages }}"
  become: true
  register: package_install

- name: Output result of package installation
  debug:
    var: package_install.results
```

---

### Inventory Configuration (`/ansible-project/inventory/aws_ec2.yml`)

```yaml
plugin: aws_ec2
regions:
  - eu-west-2
filters:
  tag:Environment: dev
keyed_groups:
  - key: tags['Environment']
    prefix: env
  - key: tags['Type']
    prefix: type
  - key: tags['Team']
    prefix: team
```

---

### Conclusion

This README provides a comprehensive guide for deploying and managing the Todo-List Flask application using Terraform and Ansible on AWS

---
