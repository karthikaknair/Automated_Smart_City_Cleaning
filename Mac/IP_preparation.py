import re
import xml.etree.ElementTree as ET
import socket

def get_local_ip():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Can't use 127.0.0.1 because we want to get the external IP
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def replace_ip_in_file(file_path, new_ip):
    # Read the XML file
    with open(file_path, 'r') as file:
        file_contents = file.read()

    # Use regular expression to find all IP addresses
    ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    replaced_contents = re.sub(ip_pattern, new_ip, file_contents)

    # Save the modified file
    with open(file_path, 'w') as file:
        file.write(replaced_contents)

def main():
    new_ip = get_local_ip()

    paths = [
        "/usr/local/Cellar/hadoop/3.3.6/libexec/etc/hadoop/core-site.xml",
        "/usr/local/Cellar/hadoop/3.3.6/libexec/etc/hadoop/mapred-site.xml",
        "/Users/jichanglong/PycharmProjects/pythonProject/vedio_picture.py",
        "/Users/jichanglong/PycharmProjects/pythonProject/state_machine.py"
    ]

    for path in paths:
        replace_ip_in_file(path, new_ip)
        print(f"Replaced IP addresses in {path} with {new_ip}")

if __name__ == "__main__":
    main()
