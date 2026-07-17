# Getting Started Guide

Welcome! This guide will walk you through setting up and connecting to your devices quickly and easily.

If you haven’t installed **InsPy** yet, please follow these instructions:

1. Go to the InsPy installation page: [Installation Guide](../README.md/#installation).
2. Follow the on-screen instructions to install InsPy on your device.

## Import the module:
Firstly, create a python file and import the instrument class you need. You can import like the following example:


```python
from inspy.instrument.powersupply import PsuAimTTiPL303QMDP
```

## Get the address of the instrument:

If you already know how to do get the address, head over to [Instantiate the class](#instantiate-the-class) section below.

To get the address of the instrument, we need to install **Keysight IO Libraries Suite**. After installing, we can obtain the address from the application depending on the connection type.

The steps for obtaining the address are explained in detail below:


### Step 1: Install Keysight IO Libraries Suite

1. **Download the Software**: Go to the [Keysight IO Libraries Suite download page](https://www.keysight.com/find/iosuite).
2. **Run the Installer**: Once downloaded, open the installer file and follow the on-screen instructions to complete the installation.
3. **Open Keysight IO Libraries Suite**: After installation, launch the software. It will open the main interface with access to **Keysight Connection Expert**.


### Step 2: Obtain Instrument Address Using Keysight Connection Expert

1. **Open Keysight Connection Expert**: Inside Keysight IO Libraries Suite, click on **Keysight Connection Expert**.
2. **Auto-Discover Instruments**: Connection Expert will automatically scan for all connected instruments and display them in the "Instrument I/O on this PC" list.
3. **Locate Your Instrument**: Each detected instrument will show its address based on the connection type (USB, LAN, GPIB, etc.).

**Instrument not showing up**: If your instrument is not showing up and you are using a USB connection, go to `Step 2.1`.
**Connecting a LAN device**: If you want to connect a device via LAN, go to `Step 2.2`.


#### Step 2.1: Manually add USB device:

**Note**: If you are running InsPy on linux then you an extra step to get USB device to work.

``` bash
sudo tee /etc/udev/rules.d/99-inspy.rules > /dev/null <<'EOF'
SUBSYSTEM=="usb", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="xxxx", MODE="0660", GROUP="plugdev"
EOF
sudo usermod -aG plugdev "$USER"
sudo udevadm control --reload-rules && sudo udevadm trigger
```

1. **Locate the COM Port your device is connected to**:
   - It should show you a windows notification with the port number when you connect the device. If you missed it then go to next point.
   - Open **Device Manager** on your computer and locate the **Ports (COM & LPT)** section.
   - Find the COM port that corresponds to your instrument (It is usually shown as USB Serial Device).

2. **Add the instrument on Keysight Connection Expert**: 
   - Open **Keysight Connection Expert** and under **My Instruments** there should be some COM (ASRLx) options. Select the ASRLx that corresponds to the COMx identified before. For example, if you saw your device is connected to COM4, click on COM (ASRL4).
   - Without changing anything, click on `+ Instrument` and then `OK`.
   - Now you should be able to follow the next steps.


#### Step 2.2: Add LAN device:
1. **Make sure the device is connected to the network**
   - If you connect your device via LAN directly to your PC, it is a complicated process and is out of scope for this guide.
   - Easiest thing is to connect it to the network and access via IP address or use a USB connection.

2. **Add the instrument on Keysight Connection Expert**:
   - Open **Keysight Connection Expert** and under **My Instruments** there should be an option for **LAN (TCPIP0)**. Click on that.
   - Click on `+ Instrument`. For most instruments, the device should show under **Select from List**. Just select that device and click on `OK`.
   - If it is not present, click on **Enter Address**.
   - Find the IP address of the device by either going to `Utility -> I/O` (Present for most devices) or look at the manual to figure out how to get the IP address.
   - Once you have the IP address, enter the address in **Hostname or IP Address** field and click on `OK`.


### Step 3: Identify the Instrument Address

1. USB Instruments
   - Just click on the device and you should be able to see the address under **VISA Address**
   - Click on the address and copy it.
   - The address can be of the form `ASRL16::INSTR` or `USB0::0x2A8D::0x1797::CN57046469::0::INSTR`

2. LAN (Ethernet) Instruments
   - Just click on the device and you should be able to see the address under **VISA Address**
   - Click on the address and copy it.
   - The address should be of the form `TCPIP0::172.18.44.89::5025::SOCKET` or some other form.
   - You can also get the address directly from the IP Address. Search the IP address on your browser and you should be able to see the addresses you need.

3. Serial (RS232) Instruments
   - **RS232 Instruments will be added soon**

4. GPIB Instruments
   - **Currently GPIB instruments are out of scope**

If you are still facing issues, please let one of the team members know.


After getting the address, store it in a variable for usage later. We are using a USB connector for the example:



```python
address = 'ASRL16::INSTR'
```

## Instantiate the class:

After you identify the address, you need to make an instance of the classes like the following (Use whatever name you want):


```python
psu = PsuAimTTiPL303QMDP(address)
```

The instrument builds the right transport from the address for you. If you need to customise the connection (e.g. a specific serial setting), you can still pass a transport instance explicitly with the `transport` keyword:


```python
from inspy.transport.serial_transport import SerialTransport

psu = PsuAimTTiPL303QMDP(transport=SerialTransport(visa_resource_name=address, baudrate=9600))
```

## Make sure your instrument is connected:

Run the following command to check if your device is connected properly. If it throws error, your device isn't connected.


```python
with psu as _psu:
    print(_psu.get_id())
```

    2024-11-22 13:43:48 [    INFO] PsuAimTTiPL303QMDP.get_id()
    2024-11-22 13:43:49 [    INFO] PsuAimTTiPL303QMDP.get_id -> 'THURLBY THANDAR,...
    

    THURLBY THANDAR, PL303QMD-P,  360604, 3.00 - 3.02
    

## Connecting to the instrument via InsPy:

The above line will make an object of the instrument but will not connect yet.
There are a few ways you can connect to the instument. Examples are given below. You can use any of them as you like

1. **Using a context manager (Recommended)**:
You have seen this just back and the benefit of this is that you don't need to manually connect or disconnect. It will do it automatically.


```python
with psu as _psu:
    print(_psu.get_id())
```

    2024-11-22 13:43:49 [    INFO] PsuAimTTiPL303QMDP.get_id()
    2024-11-22 13:43:51 [    INFO] PsuAimTTiPL303QMDP.get_id -> 'THURLBY THANDAR,...
    

    THURLBY THANDAR, PL303QMD-P,  360604, 3.00 - 3.02
    

2. **Using connect and disconnect**: For this you have to connect, then use the instrument and then again disconnect manually. If something goes wrong, you have to make sure it is still calling the disconnect function. For this complexity, it is recommended to use the first approach. Remember to `Disconnect`!


```python
psu.connect()
print(psu.get_id())
psu.disconnect()
```

    2024-11-22 13:43:51 [    INFO] PsuAimTTiPL303QMDP.get_id()
    2024-11-22 13:43:51 [    INFO] PsuAimTTiPL303QMDP.get_id -> 'THURLBY THANDAR,...
    

    THURLBY THANDAR, PL303QMD-P,  360604, 3.00 - 3.02
    

Now we can use more useful functions. But before that let's learn how to get help or more information about what you are dealing with.

## Getting Help:

To get information about the class, type the following command and it should provide you information about what you're dealing with. For example:


```python
help(psu)

# or

help(PsuAimTTiPL303QMDP)
```

You can also extract the methods that are supported by the instrument:


```python
from inspy import list_methods

print(list_methods(psu))
```

    To connect and disconnect:
     - connect
     - disconnect
    Other available methods:
     - await_completion
     - get_channel_state
     - get_current
     - get_current_range
     - get_id
     - get_output_current_trip_point
     - get_output_voltage_trip_point
     - get_voltage
     - measure_current
     - measure_voltage
     - reset
     - set_channel_state
     - set_current
     - set_current_range
     - set_output_current_trip_point
     - set_output_voltage_trip_point
     - set_voltage
    

You can also get more information about the method you are going to use. For example:


```python
help(psu.set_current_range)
```

    Help on function set_current_range in module inspy.instrument.powersupply.aimtti_psu:
    
    set_current_range(current_range: Literal['Low', 'High'], channel: int = 1) -> None method of inspy.instrument.powersupply.aimtti_psu.PsuAimTTiPL303QMDP instance
        Set the current range of the channel.
        
        Requires channel to be switched off before changing.
        
        Args:
            current_range: Low current range or high current range
            channel: Channel to set range of.
        
        Raises:
            Exception: Changing current range requires channel to be disabled!
            ValueError: Invalid value for range
    
    

## Writing a small program:

Now since we have gone through all the things, we can write a small program to get started with


```python

from inspy.instrument.powersupply import PsuAimTTiPL303QMDP
import logging

address = 'ASRL16::INSTR'
psu = PsuAimTTiPL303QMDP(address)

# By default it will log all the commands and responses to the console
# You can disable it by the following command
logging.getLogger("PsuAimTTiPL303QMDP").setLevel(logging.WARNING)

# Connect to the instrument
with psu as _psu:
    # Get the ID of the instrument
    print("ID of the instrument:")
    print(_psu.get_id())
    
    # Set the channel 1 to 2V and 0.1A
    print("Setting channel 1 to 2V and 0.1A:")
    _psu.set_channel_state(enable=True, channel=1)
    _psu.set_voltage(voltage=2, channel=1)
    _psu.set_current(current=0.1, channel=1)
    print("Done setting channel 1 to 2V and 0.1A")    

    # Get the voltage and current of channel 1
    print("Getting voltage and current of channel 1:")
    print(_psu.get_channel_state(channel=1))
    print(_psu.get_voltage(channel=1))
    print(_psu.get_current(channel=1))

    # Set the channel 2 to 5V and 0.2A
    print("Setting channel 2 to 5V and 0.2A:")
    _psu.set_channel_state(enable=True, channel=2)
    _psu.set_voltage(voltage=5, channel=2)
    _psu.set_current(current=0.2, channel=2)
    print("Done setting channel 2 to 5V and 0.2A")

    # Get the voltage and current of channel 2
    print("Getting voltage and current of channel 2:")
    print(_psu.get_channel_state(channel=2))
    print(_psu.get_voltage(channel=2))
    print(_psu.get_current(channel=2))
```

    ID of the instrument:
    THURLBY THANDAR, PL303QMD-P,  360604, 3.00 - 3.02
    Setting channel 1 to 2V and 0.1A:
    Done setting channel 1 to 2V and 0.1A
    Getting voltage and current of channel 1:
    True
    2.0
    0.1
    Setting channel 2 to 5V and 0.2A:
    Done setting channel 2 to 5V and 0.2A
    Getting voltage and current of channel 2:
    True
    5.0
    0.2
    

### Notes:

If something is giving timeout or any error that doesn't look right, try using:
> _psu.await_completion()

If that still doesn't work, you could try:
> time.sleep(0.5)

In rare cases, all your tests might fail. If that happens, it's either your IDE problem or the device. We suggest restarting the IDE and reconnect the device.
    

## All Done!

Now you can create your own program and utilise it as you need