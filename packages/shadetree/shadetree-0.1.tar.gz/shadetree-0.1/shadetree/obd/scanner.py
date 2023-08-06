from __future__ import absolute_import
import time

import serial

from shadetree import elm327
from shadetree.obd import commands
from shadetree.obd.fuel_type import FUEL_TYPE_DESCRIPTION


class OBDScanner(object):
    """
        ELM327 OBD-II Scanner

        Information about OBD-II PIDs
        http://en.wikipedia.org/wiki/OBD-II_PIDs

        Additional details about EML327 OBD <-> RS232 found here:
        http://elmelectronics.com/DSheets/ELM327DS.pdf

    """

    def __init__(self):
        self.serial_port = None
        self.connected = False
        self.elm_version = ""

    def connect(self):
        """
            Opens a connection to an ELM327 OBD-II Interface
            :return:
        """
        self.serial_port = serial.Serial(elm327.DEFAULT_PORTNAME, baudrate=elm327.DEFAULT_BAUDRATE,
                                         bytesize=elm327.DEFAULT_BYTESIZE, parity=serial.PARITY_NONE,
                                         stopbits=elm327.DEFAULT_STOPBITS, timeout=elm327.DEFAULT_TIMEOUT)
        self.initialize()
        self.connected = True

    def __enter__(self):
        """
            Sets up the OBDScanner to work as a ContextManager
            :return:
        """
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def battery_voltage(self):
        """
            Reads the vehicle's battery voltage from a connected OBD-II Scanner
            :return: the battery voltage returned by the OBD-II Scanner
        """
        self.send(elm327.BATTERY_VOLTAGE_COMMAND)
        return self.receive()

    def clear_trouble_codes(self):
        """
            Uses OBD Mode 04 to clear trouble codes and the malfunction indicator lamp (MIL) / check engine light
            :return:
        """
        self.send(commands.CLEAR_TROUBLE_CODES_COMMAND)

    def current_engine_coolant_temperature(self):
        """
            Reads the vehicle's current engine coolant temperature from a connected OBD-II Scanner
            :return: the current engine coolant temperature in degrees Celsius
        """
        self.send(commands.CURRENT_ENGINE_COOLANT_TEMP_COMMAND)
        response = self.receive()
        response_data = response.strip().split(' ')[-1]
        #The data returned in the OBD response is in hexadecimal with a zero offset to account for negative temperatures
        #To return the current temperature in degrees Celsius, we must first convert to decimal and then subtract 40
        #to account for the zero offset.
        return int(response_data, 16) - 40

    def current_engine_oil_temperature(self):
        """
            Reads the vehicle's current engine oil temperature from a connected OBD-II Scanner
            :return: the current engine oil temperature in degrees Celsius
        """
        self.send(commands.CURRENT_ENGINE_OIL_TEMP_COMMAND)
        response = self.receive()
        response_data = response.strip().split(' ')[-1]
        #The data returned in the OBD response is in hexadecimal with a zero offset to account for negative temperatures
        #To return the current temperature in degrees Celsius, we must first convert to decimal and then subtract 40
        #to account for the zero offset.
        return int(response_data, 16) - 40

    def current_engine_rpm(self):
        """
            Reads the vehicle's current engine RPM value from a connected OBD-II Scanner
            :return: the current engine RPM
        """
        self.send(commands.CURRENT_ENGINE_RPM)
        response = self.receive()
        response_data = response.strip().split(' ')
        if len(response_data) >= 2:
            rpm = (int(response_data[-2], 16) * 256 + int(response_data[-1], 16)) / 4
            return rpm
        else:
            return None

    def ecu_name(self):
        """
            Returns the name of the Engine Control Unit (ECU)
            :return:
        """
        self.send(commands.ECU_NAME_COMMAND)
        return self.receive()

    def fuel_type(self):
        """
            Reads the vehicle's fuel type from a connected OBD-II Scanner
            :return: a description of the type of fuel used by the vehicle
        """
        self.send(commands.FUEL_TYPE_COMMAND)
        response = self.receive()
        response_data = response.strip().split(' ')[-1]
        return FUEL_TYPE_DESCRIPTION.get(int(response_data, 16))

    def echo_off(self):
        """
            Turns ECHO OFF for the OBD-II Scanner
            :return:
        """
        self.send(elm327.ECHO_OFF_COMMAND)

    def disconnect(self):
        """
            Disconnect from a connected OBD-II Scanner
            :return:
        """
        if self.connected:
            self.reset()
            self.serial_port.close()
        self.connected = False
        self.elm_version = ""

    def initialize(self):
        """
            Initialize the OBD-II Scanner state after connecting
            :return:
        """
        self.reset()
        self.echo_off()
        self.send(elm327.SELECT_PROTOCOL_COMMAND)
        self.receive()

    def receive(self):
        """
            Receive data from connected OBD-II Scanner
            :return: the data returned by the OBD-II Scanner
        """
        if self.connected:
            #Wait a second for data to become available
            time.sleep(1)
            retry_number = 0
            value = ""
            while True:
                data = self.serial_port.read(1)

                if data == '>':
                    break

                if len(data) == 0:
                    if retry_number >= elm327.DEFAULT_RETRIES:
                        break
                    retry_number += 1
                    continue

                if data == '\r':
                    continue

                value += data

            if value:
                return value

        return None

    def reset(self):
        """
            Reset the OBD-II Scanner
            :return:
        """
        if self.connected:
            self.send(elm327.RESET_COMMAND)
            self.elm_version = self.receive()

    def send(self, data):
        """
            Send data/command to the connected OBD-II Scanner
            :param data: the data/command to send to the connected OBD-II scanner
            :return:
        """
        if self.connected:
            self.serial_port.flushOutput()
            self.serial_port.flushInput()
            self.serial_port.write(data + "\r\n")

    def vehicle_id_number(self):
        """
            Returns the vehicle's identification number (VIN)
            :return:
        """
        self.send(commands.VEHICLE_ID_NUMBER_COMMAND)
        return self.receive()
