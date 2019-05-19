'''
This is the main.py file for Pybytes
This code and included libraries are intended for users wishing to fully
customise pybytes. It is the same code that is included in the Pybytes firmware
If you're planning to use the Pybytes firmware, please check out the
examples in the examples directory which are much easier to use.
If you make changes to any of the libraries in the lib directory,
you only need to upload the changed files if using the Pybytes firmware.
The other libraries will be loaded from the built-in code.
If you make changes above "Please put your USER code below this line" while
using a Pybytes enabled firmware, you need to disable auto-start.
You can disable auto-start by setting "pybytes_autostart": false in
pybytes_project.json or pybytes_config.json.
If using the Pybytes firmware, the configuration is already loaded and this
cannot be deactivated. However if you disable auto-start, you can modify the
configuration before connecting to Pybytes manually using pybytes.connect()
'''

# Load configuration, migrate to pybytes_config.json if necessary
if 'pybytes_config' not in globals().keys():
    try:
        from pybytes_config import PybytesConfig
        frozen = False
        try:
            from pybytes import Pybytes
        except:
            frozen = True
    except:
        from _pybytes_config import PybytesConfig
        frozen = True

    pybytes_config = PybytesConfig().read_config()

# Load Pybytes if it is not already loaded
if 'pybytes' not in globals().keys() and pybytes_config.get('pybytes_autostart', True):
    if frozen:
        try:
            from _pybytes import Pybytes
        except:
            raise ImportError("Unable to load Pybytes. Please check your code...")

    pybytes = Pybytes(pybytes_config)
    pybytes.print_cfg_msg()
    pybytes.connect()

elif not pybytes_config.get('pybytes_autostart', True) and pybytes_config.get('cfg_msg') is not None:
    print(pybytes_config.get('cfg_msg'))
    print("Not starting Pybytes as auto-start is disabled")

del pybytes_config
del frozen
del PybytesConfig

if 'pybytes' in globals().keys():
    if pybytes.is_connected():

        print("Now starting user code in main.py")
        '''
        If Pybytes isn't connected at this time, it means you either deliberately
        disabled Pybytes auto-start, or something went wrong.
        This could be reading the configuration or establishing a connection.

        To connect to Pybytes manually when auto-start is disabled, please call:
        pybytes.connect()
        '''

        # Please put your USER code below this line

        # SEND SIGNAL
        # You can currently send Strings, Int32, Float32 and Tuples to pybytes using this method.
        # pybytes.send_signal(signalNumber, value)

        # SEND SENSOR DATA THROUGH SIGNALS
        # # If you use a Pysense, some libraries are necessary to access its sensors
        # # you can find them here: https://github.com/pycom/pycom-libraries
        #
        # # Include the libraries in the lib folder then import the ones you want to use here:
        from L76GNSS import L76GNSS
        gnss = L76GNSS()

        from LIS2HH12 import LIS2HH12
        accel = LIS2HH12()

        # Import what is necessary to create a thread
        import _thread
        import time
        from machine import Pin

        last_alert_time = time.time()

        def crash_detected(arg):
            global last_alert_time
            if (time.time() - last_alert_time) > 60:  # 60 seconds since last alert
                x, y, z = accel.acceleration()
                lat, lon = gnss.coordinates()
                print("Crash detected! ({x}, {y}, {z}): {}".format(arg, x=x, y=y, z=z))

                if lat is not None and lon is not None:
                    pybytes.send_signal(11, [lat, lon])
                # pybytes.send_signal(11, [51.26849, -1.072273])
                last_alert_time = time.time()
            else:
                print("Crash bounce protection activated. Last alert: {}, time now: {}".format(last_alert_time, time.time()))

        accel.enable_activity_interrupt(3500, 10, crash_detected)

        # Define your thread's behaviour, here it's a loop sending sensors data every 10 seconds
        def send_env_data():
            while (pybytes):
                x, y, z = accel.acceleration()
                lat, lon = gnss.coordinates()
                # can be none
                if x is not None and y is not None and z is not None:
                    pybytes.send_signal(8, [x, y, z])

                if lat is not None and lon is not None:
                    pybytes.send_signal(9, [lat, lon])
                time.sleep(60)

        # Start your thread
        _thread.start_new_thread(send_env_data, ())

        # SET THE BATTERY LEVEL
        # pybytes.send_battery_level(23)

        # SEND DIGITAL VALUE
        # pybytes.send_digital_pin_value(False, 12, Pin.PULL_UP)

        # SEND ANALOG VALUE
        # pybytes.send_analog_pin_value(False, 13)

        # REGISTER PERIODICAL DIGIAL VALUE SEND
        # pybytes.register_periodical_digital_pin_publish(False, PIN_NUMBER, Pin.PULL_UP, INTERVAL_SECONDS)

        # REGISTER PERIODICAL ANALOG VALUE SEND
        # pybytes.register_periodical_analog_pin_publish(False, PIN_NUMBER, INTERVAL_SECONDS)

        # CUSTOM METHOD EXAMPLE
        # def custom_print(params):
        #     print("Custom method called")
        #     return [255, 20]
        # pybytes.add_custom_method(0, custom_print)
