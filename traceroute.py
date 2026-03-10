# traceroute.py

'''
.py file needs to have the same name as the folder, so f folder is 'traceoute' file needs to be named 'traceroute.py' in order to be imported.
'''

# import flask app
from flask import Flask, render_template, render_template_string, request

# import what is needed for this plugin
import socket
import struct
import time
import os
import requests

# For translations
# https://python-babel.github.io/flask-babel/
from flask_babel import Babel, _

# Import stuff from OpenPanel core
from app import app, inject_data, login_required_route
from modules.core.init import fetch_public_ip

# custom funtion example
def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        client_ip = request.remote_addr

    return client_ip



# you can not run pip install for additional tools, and since mtr is not available in OpenPanel UI contianer, we need to use vanila python to simulate traceroute output
def simple_traceroute(dest_name, max_hops=30, timeout=1):
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        return f"Error: Invalid hostname or IP address '{dest_name}'"

    port = 33434
    result = []

    for ttl in range(1, max_hops + 1):
        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            recv_socket.settimeout(timeout)
            recv_socket.bind(("", port))

            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

            start_time = time.time()
            send_socket.sendto(b"", (dest_addr, port))

            try:
                data, curr_addr = recv_socket.recvfrom(512)
                end_time = time.time()
                curr_addr = curr_addr[0]

                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr

                elapsed = (end_time - start_time) * 1000  # ms
                line = f"{ttl}\t{curr_addr}\t{elapsed:.2f} ms"
            except socket.timeout:
                line = f"{ttl}\t*\tTimeout"

            send_socket.close()
            recv_socket.close()

            result.append(line)

            if curr_addr == dest_addr:
                break
        except PermissionError:
            return "Error: Root privileges required to run traceroute."
        except Exception as e:
            return f"Error: {str(e)}"

    return "\n".join(result)



# Route should be same as 'link' in readme.txt
@app.route('/advanced/traceroute', methods=['GET', 'POST'])
# remove login_required_route decorator if page should be accessed without login (NOT RECOMMENDED)
@login_required_route
def traceroute():
    result = ""
    if request.method == 'POST':
        target = request.form.get('target')
        if target:
            try:
                result = simple_traceroute(target)
            except Exception as e:
                result = f"Error: {str(e)}"
        else:
            # use _( ) to allow localization of the text
            result = _("Please enter a valid IP address or hostname.")

    # this is needed for tempaltes to overwrite global templates folder
    #exit the html file name accordingly
    template_path = os.path.join(os.path.dirname(__file__), 'traceroute.html')
    with open(template_path) as f:
        template = f.read()

    # return ip address for openpanel account
    current_username = inject_data().get('current_username') # returns username of the current openpanel account
    server_ip = fetch_public_ip() # returns IP for the current openpanel account
    client_ip = get_client_ip() # returns ip form our cusotm function

    return render_template_string(
        template,
        title=_('Traceroute'), # title is shown in breadcrumbs and browser tab
        server_ip=server_ip,
        client_ip=client_ip,
        result=result
    )
