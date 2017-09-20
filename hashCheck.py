#!/usr/bin/python3
#you need to install paramiko using pip3 for this to work (it is the ssh library used) 
#********the bottom of the iceberg**********
from urllib.request import urlopen
from time import sleep
from paramiko import client
import os

lowHash = 155

#email variables
e_username='email username'
e_password='email password'
email_address='email address'
site='not used'
subject='email subject'
message='email body message'

#power device to reboot if in accessable variables
p_ip='ip of device to reboot'
p_username='username'
p_password='password'

#email alert function 
def send_alert():
    from smtplib import SMTP
    from email.mime.text import MIMEText

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = email_address

    server = SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(e_username, e_password)
    server.sendmail(email_address, [email_address], msg.as_string())
    server.quit()

#ssh class for connecting with power controller (mfi) and then issuing command to reboot
class ssh:
    client = None

    def __init__(self, address, username, password):
        print("Connecting to server.")
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)

    def sendCommand(self, command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata

                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")

#*************actual work being done (the top of the iceberg)**********
while True:
   os.system('show stats |grep status|awk \'{print $2}\' > /tmp/hashrate ')
   f=open("/tmp/hashrate", "r")
   hashrate = f.read()
   if (hashrate == "miner"):
     print("not ready yet wait 5 minutes")
     sleep(300)
   else:
     if (int(float(hashrate.strip())) > int(float(lowHash))):
       #print (hashrate.strip())
       print("all is well")
     else:
       print ("all is not well")
       send_alert()
       os.system('sudo reboot')
     #ssh into power controller and issue reboot command
     #connection = ssh(p_ip, p_username, p_password)
     #connection.sendCommand("echo 0 > /proc/power/relay1 && sleep 20 && echo 1 > /proc/power/relay1")
   f.close()
   sleep(600)
