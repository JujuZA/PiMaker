# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 16:00:12 2014

@author: Jason
"""

import json
import yaml
from x3gparams import params
import serial
import threading
import os
import re
import time

import makerbot_driver


class makerbot(object):
    def __init__(self, port='/dev/ttyACM0'):
        self.r = makerbot_driver.s3g()
        self.file = serial.Serial(port, 115200, timeout=1)
        self.condition = threading.Condition()
        self.r.writer = makerbot_driver.Writer.StreamWriter(self.file, self.condition)

        printer_name = 'Replicator2'
        # printer_name = (r.getname()).replace(' ', '')
        current_point = self.r.get_extended_position()[0]
        self.p = params(printer_name, current_point)
        with open('gctx.json') as f:
            d = json.load(f)
        self.d = d
        self.buildname = 'Unknown'
        self.ec = 0

    def break_down_gcode(self, gcode):
        code = ''
        regs = ''
        comment = ''

        l = re.split(';|\(', gcode)
        if len(l[0]) != 0:
            d = l[0].split()
            if len(d) != 0:
                code = d[0]
                regs = d[1:]
        if len(l) > 1:
            if len(l[1]) != 0:
                comment = l[1]

        return code, regs, comment

    def gcode_to_command(self, gcode):
        code, regs, comment = self.break_down_gcode(gcode)
        call = self.d.get(code, '')
        pf = 'get_' + call + '_args'
        if (code != 'M136') & (code != 'M137') & (code != ''):
            args = getattr(self.p, pf)(regs)
        else:
            args = []

        if code == 'M70':
            if '(' not in comment:
                comment = comment.replace(')', '')
            timeout = args[0]
            args = [0, 0, comment, timeout, True, True, False]
        elif code == 'M126':
            args.append(True)
        elif code == 'M127':
            args.append(False)
        elif code == 'M136':
            args.append(self.buildname)

        return call, args

        # WARNING: Takes a while

    def gcode_file_to_commands(self, filename):
        fn = filename.split('.')
        commands = []
        if fn[1] == 'gcode':
            f = open(filename)
            self.buildname = fn[0]
            for line in f:
                call, args = self.gcode_to_command(line)
                commands.append([call, args])
            f.close()
        return commands

    def gcode_file_to_inter(self, filename):
        n = 0
        fn = filename.split('.')
        ifn = fn[0] + ".j3g"
        if fn[1] == 'gcode':
            f = open(filename)
            j = open(ifn, 'w+')
            self.buildname = fn[0]
            for line in f:
                call, args = self.gcode_to_command(line)
                j.write(json.dumps([call, args]) + '\n')
                print "Translating line ", n
                n += 1
            f.close()
            j.close()
        return ifn

    def commands_to_inter(self, filename, commands):
        fn = filename.split('.')
        ifn = fn[0] + '.j3g'
        j = open(ifn, 'w+')
        for c in commands:
            j.write(json.dumps(c) + '\n')
        j.close()
        return ifn

    # WARNING: Takes a while
    def commands_to_sdf(self, filename, commands):
        fn = filename.split('.')
        nfn = fn[0] + '.x3g'
        self.r.capture_to_file(nfn)
        for c in commands:
            self.execute_inter_command(c[0], c[1])
        fs = self.r.end_capture_to_file()
        return fs

    def inter_to_sdf(self, filename):
        #n = 0
        fs = 0
        fn = filename.split('.')
        if fn[1] == 'j3g':
            nfn = fn[0] + '.x3g'
            j = open(filename)
            self.r.capture_to_file(nfn)
            for line in j:
                c = yaml.load(line)
                self.execute_inter_command(c[0], c[1])
                #if (n % 100) == 0:
                #    print "Sending line ", n
                #n += 1
            fs = self.r.end_capture_to_file()
            #print c
            j.close()
        return fs

    def gcode_to_sdf(self, filename):
        fn = filename.split('.')
        fs = 0
        if fn[1] == 'gcode':
            nfn = fn[0] + '.x3g'
            self.r.capture_to_file(nfn)
            f = open(filename)
            self.buildname = fn[0]
            for line in f:
                call, args = self.gcode_to_command(line)
                print call, ': ', args
                self.execute_inter_command(call, args)
            fs = self.r.end_capture_to_file()
            f.close()
        return fs

    def get_sd_files(self):
        fn = self.r.get_next_filename(True)
        cf = fn
        sdf = []
        while cf != '\x00':
            sdf.append(cf)
            cf = self.r.get_next_filename(False)
        return sdf

    def print_from_sd(self, filename):
        sdf = self.get_sd_files()
        if filename in sdf:
            self.r.playback_capture(filename)
        else:
            print('File not found')

    def execute_gcode_single(self, gcode):
        call, args = self.gcode_to_command(gcode)
        self.execute_inter_command(call, args)

    def execute_inter_command(self, call, args):
        if call == 'set_potentiometer_value':
            for a, v in zip(args[0], args[1]):
                getattr(self.r, call)(a, v)
        elif len(call) != 0:
            getattr(self.r, call)(*args)
        else:
            self.ec += 1

    def execute_gcode_file(self, filename):
        fn = filename.split('.')
        if fn[1] == 'gcode':
            f = open(filename)
            self.buildname = fn[0]
            for line in f:
                call, args = self.gcode_to_command(line)
                bfs = self.r.get_available_buffer_size()
                time.sleep(0.01)
                while bfs < 50:
                    time.sleep(0.2)
                    bfs = self.r.get_available_buffer_size()
                self.execute_inter_command(call, args)
            f.close()

    def execute_inter_file(self, filename):
        fn = filename.split('.')
        if fn[1] == 'j3g':
            j = open(filename, 'r')
            for line in j:
                c = yaml.load(line)
                if c[0] == 'set_build_percent':
                    print c[1][0], "% complete"
                #print "Calling: ", c
                bfs = self.r.get_available_buffer_size()
                while bfs < 50:
                    #print 'Buffer Size: ', bfs
                    time.sleep(0.2)
                    bfs = self.r.get_available_buffer_size()
                self.execute_inter_command(c[0], c[1])
            print 'Done!'
            j.close()

    def close(self):
        self.r.close()
        self.file.close()
