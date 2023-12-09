#!/bin/bash

# Ubuntu 22.04 LTS: disable the popup "Which service should be restarted ?"
sudo sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
sudo apt update
sudo apt install -y python3-pip python3-venv
sudo apt-get install -y apache2 libapache2-mod-wsgi-py3
sudo apt install python3-flask

mkdir /home/ubuntu/flaskapp && cd /home/ubuntu/flaskapp
python3 -m venv myenv

# Link to the app directory from the site-root defined in apache’s configuration
sudo ln -sT /home/ubuntu/flaskapp /var/www/html/flaskapp

# move the files to the flask directory
cd ~/flaskapp
sudo mkdir templates
sudo mv ../index.html templates
sudo mv ../result.html templates
sudo mv ../cloud_pattern_private_ip.txt .

# Configure access to port 80
sudo apt install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80

source myenv/bin/activate

# The flask app
cat > /home/ubuntu/flaskapp/flaskapp.py << 'EOF'
from flask import Flask, render_template, request
import socket

app = Flask(__name__)

def send_data_to_trusted_host(operation, actor_first_name, actor_last_name):
    # Open the config file to get the private ip of the gatekeeper
    filename = '/home/ubuntu/flaskapp/cloud_pattern_private_ip.txt'
    with open(filename, 'r') as file:
        ip_addresses = file.readlines()

    # Connect to the trusted host
    trusted_host_host = ip_addresses[1].strip()
    trusted_host_port = 8080

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((trusted_host_host, trusted_host_port))

    # Send the operation and user input to the trusted host
    data_to_send = f"{operation}|{actor_first_name}|{actor_last_name}"
    client_socket.sendall(data_to_send.encode('utf-8'))

    # Receive and return the result from the trusted host
    result = client_socket.recv(1024).decode('utf-8')

    client_socket.close()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_query', methods=['POST'])
def submit_query():
    operation = request.form['operation']
    actor_first_name = request.form.get('first_name', '')
    actor_last_name = request.form.get('last_name', '')

    # Send the operation and user input to the trusted host
    result = send_data_to_trusted_host(operation, actor_first_name, actor_last_name)

    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
EOF

# Create a .wsgi file to load the app
cat > /home/ubuntu/flaskapp/flaskapp.wsgi << 'EOF'
import sys
sys.path.insert(0, '/var/www/html/flaskapp')
sys.path.insert(0, "/home/ubuntu/flaskapp/myenv/lib/python3.10/site-packages")

from flaskapp import app as application

EOF

# Enable mod_wsgi
sudo sed -i "/DocumentRoot \/var\/www\/html/r /dev/stdin" /etc/apache2/sites-enabled/000-default.conf <<'EOF'
    WSGIDaemonProcess flaskapp threads=5 python-path=/var/www/html/flaskapp/myenv
    WSGIProcessGroup flaskapp
    WSGIApplicationGroup %{GLOBAL}
    WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi

    <Directory /var/www/html/flaskapp>
        Options FollowSymlinks
        AllowOverride All
        Require all granted
        allow from all
    </Directory>
EOF

export flaskapplication=/home/ubuntu/flaskapp/flaskapp.py
authbind --deep python3 /home/ubuntu/flaskapp/flaskapp.py

sudo chmod -R +x /home/ubuntu/
sudo service apache2 restart