# Raspberry Pi Zero W Setup and Access Guide

This guide explains how to access the Raspberry Pi Zero W v1.1 via SSH, set up and use a Python virtual environment, run a Python script, and manage Wi-Fi configurations.

## 0. Starting the firmaware
     ```bash
     cd shared/ && source ~/pxdenv/bin/activate && sudo ~/pxdenv/bin/python3 main.py
     ```

## 1. **Accessing the Raspberry Pi via SSH**

### Prerequisites:
- Raspberry Pi Zero W running Raspberry Pi OS (Lite or Full).
- The Pi is connected to the same local network as your PC.

### SSH Access:

You can access the Raspberry Pi using SSH (Secure Shell) from your PC. Follow these steps:

1. **Find the Pi's IP Address:**
   - You can find the Pi's IP by either using a network scan tool (e.g., `nmap`) or accessing the router's admin page.
   - Alternatively, you can use [Pi Connect](https://www.raspberrypi.com/documentation/services/connect.html) to find and connect to the Pi remotely.

2. **Connect to the Pi via SSH:**

   - Open a terminal on your PC (Linux/Mac/WSL or Windows terminal with SSH client installed).
   - Run the following command (replace `192.168.x.x` with your Pi's IP address):

     ```bash
     ssh pxd@192.168.x.x
     ```

     pxd is the username
     the password needs to be requested :P


   The Pi can also be accesed using Pi Connect: visit [Pi Connect Devices](https://connect.raspberrypi.com/devices) to find the Pi and connect to it via SSH. The credetianls for an account that is allready connected can be also requested :P

## Samba virtuall Drive

Samba Drive is located in pxd/shared
user: pxd
Passwort: tonsor25

---

## 2. **Setting Up a Python Virtual Environment**

### Create and Activate the Virtual Environment:

1. **Install Virtualenv (if not already installed):**

   ```bash
    sudo apt install python3-venv
    ```
    Create a virtual environment:

    ```bash
    python3 -m venv ~/pxdenv
    ```
2. **Activate the virtual environment:**

    ```bash
    source ~/pxdenv/bin/activate
    ```
    After activation, your terminal prompt will change, indicating that you're working inside the virtual environment.

3. **Upgrade pip (recommended):**

    ```bash
    pip install --upgrade pip
    ```

## 3. Installing Dependencies
Once inside the virtual environment, install any necessary libraries for your project. For example:

```bash
pip install rpi_ws281x adafruit-circuitpython-neopixel
```
Running Your Script:
Once dependencies are installed, you can run your Python script:

```bash
 sudo /home/pxd/pxdenv/bin/python3 main.py
```
Deactivate the Virtual Environment:
When done, you can deactivate the virtual environment:

```bash
deactivate
```
## 4. Wi-Fi Configuration
To configure Wi-Fi on your Raspberry Pi:

Change Wi-Fi Configuration:
Open the Wi-Fi configuration file:

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
Add or modify network details for your Wi-Fi connection:

```bash
network={
    ssid="Your_SSID"
    psk="Your_Password"
}
```
Replace Your_SSID and Your_Password with your Wi-Fi credentials.

Save the file and restart the networking service:

```bash
sudo systemctl restart dhcpcd
```
Adding Multiple Wi-Fi Networks:
To allow the Raspberry Pi to connect to multiple Wi-Fi networks, add multiple network={} blocks inside the wpa_supplicant.conf file:

```bash
network={
    ssid="Your_SSID_1"
    psk="Your_Password_1"
}

network={
    ssid="Your_SSID_2"
    psk="Your_Password_2"
}
```
This way, the Pi will automatically connect to any available network listed in the configuration.

## Connect to Eduroam

i configured the pi allready here:
`nano eduroam.profile`
i need to connect to eduroam manually when i am near it next time with: 
```
sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/eduroam.profile
```


## 5. Other Information
IP Address:
The Raspberry Pi will likely have a dynamic IP address, meaning it may change if the Pi reboots or reconnects to the network. To keep track of the IP:

Use a network scanning tool to find the Pi’s IP on your network.
You can assign a static IP using your router’s DHCP settings, or configure the Pi’s network settings directly via /etc/dhcpcd.conf.

## Autostart
Die Firmware wird nun automatisch beim Systemstart ausgeführt, sobald eine Internetverbindung gefunden wurde.
Es wird im pxdenv-Environment ausgeführt, und zwar mit sudo-Rechten, um sicherzustellen, dass alle erforderlichen Berechtigungen vorhanden sind.

Autostart der firmware läuft automatisch und kann hier gefunden / bearbeitet werden:
```
sudo nano /etc/systemd/system/firmware_pxd_autostart.service 
```
So wurde die firmware aktiviert und kann auch deaktiviert werden (stichwort enable/disable):
```
sudo systemctl enable firmware_pxd_autostart.service 
```
logs ansehen:
```
sudo journalctl -u firmware_pxd_autostart.service -f
```
service manuell stoppen:
```
sudo systemctl stop firmware_pxd_autostart.service
```
und dann nach dem stoppen schauen, ob er auch wirklich beendet ist:
```
sudo systemctl status myscript.service
```

### clean up audio files

sudo rm -rf audio


## 6. Pi Connect (Optional)
You can use Pi Connect to access and manage your Pi remotely.

Visit Pi Connect Devices to link your Pi.
Use Pi Connect to access the Pi via an easy-to-use web interface.

