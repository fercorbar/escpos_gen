# -*- coding: utf-8 -*-

import sys
import unicodedata
import socket
import struct
import os
from helpers import *

class ESCPrinter:

    def __init__(self, printerData):

        self.data = printerData

        if not any(datum in self.data for datum in ['type', '_id']):
            print("'type' or '_id' is required in data")
            raise Exception("'type' or '_id' is required in data")

        if '_id' in self.data:
            self.data['_id'] = str(self.data['_id'])
            try:
                self.data  = get_printer_data(self.data['_id'])
            except Exception as e:
                raise e
        elif 'type' in self.data:
            if not any(t == self.data['type'] for t in ['usb', 'eth']):
                print("Not valid type 'usb' or 'eth' required")
                raise Exception("Not valid type 'usb' or 'eth' required")
            if self.data['type'] == 'usb':
                if not 'device' in self.data:
                    raise Exception("'device' is required for 'usb' type")
            elif self.data['type'] == 'eth':
                if not all(datum in self.data for datum in ['ipaddr', 'port']):
                    raise Exception("'ipaddr' and 'port' are required for 'eth' type")

        self.commands = []
        if not 'lines_before_cut' in self.data: self.data['lines_before_cut'] = 7
        if not 'max_line_len' in self.data: self.data['max_line_len'] = 48

    def send(self):
        result = False
        error = None
        try:
            if self.data['type'] == 'eth':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,32000)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                server_address = (self.data['ipaddr'], int(self.data['port']))
                sock.connect(server_address)
                for command in self.commands:
                    if isinstance(command, bytes):
                        sock.sendall(command)
                    else:
                        sock.sendall(bytes(command, '850'))
                sock.close()
                self.commands = []
                result = True
            else:
                str_dev_printer = f"/dev/usb/{self.data['device']}"
                dev_printer = open(str_dev_printer, 'wb')
                for command in self.commands:
                    if isinstance(command, bytes):
                        dev_printer.write(command)
                    else:
                        dev_printer.write(bytes(command, '850'))

                # test_file = "/app/files/test.print"
                # test_stream = open(test_file, 'wb+')
                # allcommands = b''
                # for command in self.commands:
                #     if isinstance(command, bytes):
                #         allcommands += command
                #     else:
                #         allcommands += bytes(command, '850')
                # test_stream.write(allcommands)
                # test_stream.close()

                dev_printer.close()
                self.commands = []
                result = True
        except Exception as e:
            error = str(e)
            result = False
        
        return result, error

    def reset(self):
        self.commands.append(b'\x1b\x40')

    def lf(self, times = 1):
        for _ in range(times):
            self.commands.append(b'\x0a')

    def cut_paper(self):
        """
        Insert command to cut paper. Includes line feeds set on lines_before_cut.
        """
        self.lf(self.data['lines_before_cut'])
        self.commands.append(b'\x1d\x56\x01')

    def tab(self):
        self.commands.append(b'\x09')

    def text_left(self):
        self.commands.append(b'\x1b\x61\x00')

    def text_center(self):
        self.commands.append(b'\x1b\x61\x01')

    def text_right(self):
        self.commands.append(b'\x1b\x61\x02')

    def text_tittle(self):
        self.commands.append(b'\x1b\x21\x38')

    def text_total(self):
        self.commands.append(b'\x1b\x21\x30')

    def print_string(self, text):
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        self.commands.append(text.encode('850'))

    def line(self, line_type = 0):
        """
        Insert command to print a line. Line types -> 0: dashed (Default), 1: double-dashed, 2: solid, 3: double-solid, 4: hatch-light, 5: hatch-normal, 6: hatch-dark, 7: hatch-solid.
        """
        types = {
            0: '-'.encode('850'),
            1: '='.encode('850'),
            2: b'\xc4',
            3: b'\xcd',
            4: b'\xb0',
            5: b'\xb1',
            6: b'\xb2',
            7: b'\xdf'
        }
        text = types.get(line_type)
        self.commands.append(b'\x1c\x2e')
        self.commands.append(b'\x1b\x74\x02')
        command = text*self.data['max_line_len']
        self.commands.append(command)

    def open_drawer(self):
        self.commands.append(b'\x1b\x70\x00\x32\x32')

    def repeat_string(self, text, times):
        text = text.encode('850')
        text_to_print = (text * ((times/len(text))+1))[:times]
        self.commands.append(text_to_print)

    def ring_buzzer(self, rep):
        comandos = { '0': b'\x1b\x42\x00\x02', '1': b'\x1b\x42\x01\x02', '2': b'\x1b\x42\x02\x02', '3': b'\x1b\x42\x03\x02', '4': b'\x1b\x42\x04\x02', '5': b'\x1b\x42\x05\x02', '6': b'\x1b\x42\x06\x02', '7': b'\x1b\x42\x07\x02', '8': b'\x1b\x42\x08\x02', '9': b'\x1b\x42\x09\x02' }
        comando = comandos[str(rep)]
        self.commands.append(comando)

    def print_image(self, image):
        image_data = ''.join((
            '\x1d\x76\x30\x00',
            struct.pack('2B', image.size[0] / 8 % 256, image.size[0] / 8 / 256),
            struct.pack('2B', image.size[1] % 256, image.size[1] / 256),
            image.tobytes()
            ))
        self.commands.append(image_data)

    def test(self):
        try:
            self.commands.append(b'\x1b\x70\x00\x32\x32')
            self.reset()
            self.print_string('Print test - Prueba de impresión')
            self.lf()
            self.print_string('ÁÉÍÓÚÑáéíóúñ!»«¹²³¥×@#$%^&*()-_+={}[]\/|¿?<>,.*~')
            for i in range(8):
                self.line(i)
            self.cut_paper()
            self.ring_buzzer(1)
            status, error = self.send()
        except Exception as e:
            status = False
            error = str(e)
        return status, error

    def full_test(self):

        try:
            self.reset()
            # self.commands.append(b'\x1d\x28\x41\x02\x00\x00\x02')
            # self.commands.append(b'\x1d\x28\x41\x02\x00\x01\x31') # Entra en modo hexadecimal
            # self.commands.append(b'\x1d\x28\x41\x02\x00\x00\x33')
            # self.commands.append(b'\x1d\x28\x41')
            status, error = self.send()
        except Exception as e:
            status = False
            error = str(e)
        return status, error

    def print_file(self, file):
        self.commands.append(file)
        self.send()
        pass

