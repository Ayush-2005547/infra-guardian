# webhook.py

from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/alert', methods=['POST'])
def alertmanager_webhook():
    data = request.json
    print("Received alert:", data)

    # Trigger Ansible playbook
    try:
        subprocess.run(
    ["ansible-playbook", "ansible/restart_app.yml", "-i", "ansible/inventory"],
    check=True
)
        return "Ansible playbook executed.", 200
    except subprocess.CalledProcessError as e:
        print("Ansible execution failed:", e)
        return "Failed to run Ansible playbook", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
