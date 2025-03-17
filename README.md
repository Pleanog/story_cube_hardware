# Raspberry Pi Zero W Setup and Access Guide

This guide explains how to access the Raspberry Pi Zero W v1.1 via SSH, set up and use a Python virtual environment, run a Python script, and manage Wi-Fi configurations.

## 0. Quickstart
Explanation see below Point 2. Starting the Firmware

```bash
cd shared/ && source ~/pxdenv/bin/activate && sudo /home/pxd/pxdenv/bin/python3 main.py
```

## 1. **Accessing the Raspberry Pi via SSH**

### Prerequisites:
- The Pi is connected to the same local network as your PC.
- If the Pi is connected to a different network or can't be directly accesed, but has an internet you can use PiConnect (see further down)

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

     Username on the Pi: **pxd**
     Password: needs to be requested :P


   The Pi can also be accesed using Pi Connect: visit [Pi Connect Devices](https://connect.raspberrypi.com/devices) to find the Pi and connect to it via SSH. The credetianls for an account that is allready connected can be also requested :P
   As soon as the Pi haa internet connection it tries to connect with Pi-Connect. This takes between 3-5min and then you will see a "Connect" Button that opens anew window with a direct ssh tunel to the pi.
   
## Samba virtuall Drive

Samba Drive is located in pxd/shared
user: pxd
Passwort: tonsor25

---

## 2. Starting the Firmware
Die Firmware wird leider nicht automatisch beim Systemstart ausgeführt.

cd shared/ && source ~/pxdenv/bin/activate && sudo /home/pxd/pxdenv/bin/python3 main.py 

The following command is used to navigate to the correct directory, activate the Python virtual environment, and run the main Python script with elevated privileges:

```bash
cd shared/ && source ~/pxdenv/bin/activate && sudo /home/pxd/pxdenv/bin/python3 main.py
```
`cd shared/` - Changes the current working directory to shared/, where necessary files might be stored.
`source ~/pxdenv/bin/activate` - Activates the virtual environment located in ~/pxdenv/, ensuring that the correct Python dependencies are used.
`sudo /home/pxd/pxdenv/bin/python3 main.py` - Runs main.py using the Python interpreter inside the virtual environment.

`sudo` is used to grant the script elevated privileges, which is required for accessing the hardware.

#### Stopping the Program
To stop the program, press `Ctrl + C` in the terminal.



---


## 3. **Setting Up a Python Virtual Environment**

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
## 5. Wi-Fi Configuration
To configure Wi-Fi on Raspberry Pi:

Using `nmcli` (Recommended)
To connect to a Wi-Fi network:

```bash
nmcli dev wifi connect "SSID_NAME" password "WIFI_PASSWORD"
```

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

## 6. Other Information
IP Address:
The Raspberry Pi will likely have a dynamic IP address, meaning it may change if the Pi reboots or reconnects to the network. To keep track of the IP:

Use a network scanning tool to find the Pi’s IP on your network.
You can assign a static IP using your router’s DHCP settings, or configure the Pi’s network settings directly via /etc/dhcpcd.conf.

---

## 7. AutoStart
Die Firmware wird leider nicht automatisch beim Systemstart ausgeführt.
Autostart der firmware kann hier motifiziert werden, läuft aktuell aber leider nicht

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

