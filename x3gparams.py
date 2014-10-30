# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 13:26:58 2014

@author: Jason
"""
import json
import math

class params(object):
    
    def __init__(self, pName,cPoint):
        with open(pName + '.json') as f:
            printer = json.load(f)
        amf = printer['axes']['A']['max_feedrate']
        aspm = printer['axes']['A']['steps_per_mm']
        #bmf = printer['axes']['B']['max_feedrate'] #Not needed for Rep 2
        #bspm = printer['axes']['B']['steps_per_mm'] #Not needed for Rep 2
        xmf = printer['axes']['X']['max_feedrate']
        xspm = printer['axes']['X']['steps_per_mm']
        xpl = printer['axes']['X']['platform_length']
        
        ymf = printer['axes']['Y']['max_feedrate']
        yspm = printer['axes']['Y']['steps_per_mm']
        ypl = printer['axes']['Y']['platform_length']
        
        zmf = printer['axes']['Z']['max_feedrate']
        zspm = printer['axes']['Z']['steps_per_mm']
        zpl = printer['axes']['Z']['platform_length']
        
        self.current_point = cPoint
        self.origin = [0,0,0,0,0]
        self.spm = [xspm, yspm, zspm, aspm, 0]
        self.mf = [xmf, ymf, zmf, amf, 0]
        self.pl = [xpl, ypl, zpl]
        
        self.printer = printer
    
    def get_printer_info(self):
        return self.printer
    
    #     #QEP (self, position, dda_speed, e_distance, feedrate_mm_sec, relative_axes=[]):
    #     #ed = abs(point[3] - self.current_point[3])
    #     #args = [point,dda,flags,distance,feedrate]

    def get_queue_extended_point_classic_args(self,comArgs):
        """
        Given the registers following a G1 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the queue_extended_point_x3g function.
        """
        params, flags = self.get_params(comArgs)
        point = self.get_point(params)
        step_point = self.multiply_vector(point, self.spm)
        feedrate = params.get('F',0) #(mm/min)
        dda = self.get_movement_dda(self.current_point, point, feedrate, self.mf, self.spm)

        #QEP classic (position, dda_speed)
        args = [step_point,dda]
        self.current_point = point
        return args

    def get_queue_extended_point_x3g_args(self,comArgs):
        """
        Given the registers following a G1 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the queue_extended_point_x3g function.
        """
        params, flags = self.get_params(comArgs)
        point = self.get_point(params)
        step_point = self.multiply_vector(point,self.spm)
        feedrate = params.get('F',0) #(mm/min)
        dda = self.get_movement_dda(self.current_point, point, feedrate, self.mf, self.spm)
        if dda != 0:
            ddar = 1000000.0/dda
        else:
            ddar = 1000000.0/400
        #QEP X3G STYLE (position, dda_rate, relative_axes, distance, feedrate (mm/sec))
        distance = self.get_distance(point,self.current_point) # Distance in mm
        args = [step_point,ddar,flags,distance,(feedrate/60.0)] #feedrate arg must be in mm/sec
        #ddar argument is in steps per second, and refers to the "master axis". Assuming this is the longest axis,
        #which get_movement_dda seems to already calculate for, although conversion must take place.
        self.current_point = point
        return args
        
    def get_delay_args(self,comArgs):
        """
        Given the registers following a G4 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the delay function.
        """
        # Delay claims to be specified in MICROSECONDS in s3g.py
        # Is actually in MILLISECONDS
        params, flags = self.get_params(comArgs)
        args = [params.get('P', 0)]
        return args 

    def get_set_extended_position_args(self,comArgs):
        """
        Given the registers following a G92 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the set_extended_position function.
        """
        params, flags = self.get_params(comArgs)
        point = self.get_point(params)
        step_point = self.multiply_vector(point,self.spm)
        args = [step_point]
        self.current_point = point
        return args
    
    def get_set_potentiometer_value_args(self,comArgs):
        """
        Given the registers following a G130 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the set_potentiometer_value function.
        """
        params, flags = self.get_params(comArgs)
        axes = []
        values = []
        for k in params:
            values.append(params[k])
            axes.append(k.lower())
        acodes = {'x':0,'y':1,'z':2,'a':3,'b':4}
        axs = []
        for a in axes:
            axs.append(acodes[a])
        args = [axs, values]
        return args
    
    def get_find_axes_minimums_args(self,comArgs):
        """
        Given the registers following a G161 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the find_axes_minimums function.
        """
        params, flags = self.get_params(comArgs)
        feedrate = params['F']
        mf = []
        spm = []

        point = self.current_point
        if 'x' in flags:
            point[0] = 0
            mf.append(self.mf[0])
            spm.append(self.spm[0])
        if 'y' in flags:
            point[1] = 0
            mf.append(self.mf[1])
            spm.append(self.spm[2])
        if 'z' in flags:
            point[2] = 0
            mf.append(self.mf[2])
            spm.append(self.spm[2])
        self.current_point = point

        dda = self.get_homing_dda(feedrate, mf, spm)
        args = [flags, dda, 60] #Issue with DDA, see get_queue_extended_point_x3g_args
        return args
    
    def get_find_axes_maximums_args(self,comArgs):
        """
        Given the registers following a G162 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the find_axes_maximums function.
        """
        params, flags = self.get_params(comArgs)
        feedrate = params['F']
        mf = []
        spm = []

        point = self.current_point
        pl = self.pl
        if 'x' in flags:
            point[0] = pl[0]
            mf.append(self.mf[0])
            spm.append(self.spm[0])
        if 'y' in flags:
            point[1] = pl[1]
            mf.append(self.mf[1])
            spm.append(self.spm[1])
        if 'z' in flags:
            point[2] = pl[2]
            mf.append(self.mf[2])
            spm.append(self.spm[2])
        self.current_point = point

        dda = self.get_homing_dda(feedrate, mf, spm)
        args = [flags, dda, 60] #Issue with DDA, see get_queue_extended_point_x3g_args
        return args
    
    def get_toggle_axes_args(self,comArgs):
        """
        Given the registers following a M18 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the toggle_axes function.
        """
        params, flags = self.get_params(comArgs)
        args = [flags, False]
        return args 
    
    def get_display_message_args(self,comArgs):
        """
        Given the registers following a M70 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the display_message function.
        """
        params, flags = self.get_params(comArgs)
        duration = params.get('P', 0)
        args = [duration]
        return args 
    
    def get_queue_song_args(self,comArgs):
        """
        Given the registers following a M72 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the queue_song function.
        """
        params, flags = self.get_params(comArgs)
        args = [params.get('P', 1)]
        return args 
    
    def get_set_build_percent_args(self,comArgs):
        """
        Given the registers following a M73 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the set_build_percent function.
        """
        params, flags = self.get_params(comArgs)
        args = [params.get('P', 50)]
        return args 
    
    def get_set_toolhead_temperature_args(self,comArgs):
        """
        Given the registers following a M104 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the toolhead_temperature function.
        """
        params, flags = self.get_params(comArgs)
        temp = params.get('S')        
        tool = params.get('T')
        args = [tool,temp]
        return args 
    
    def get_set_platform_temperature_args(self,comArgs):
        """
        Given the registers following a M109 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the set_platform_temperature function.
        """
        params, flags = self.get_params(comArgs)
        temp = params.get('S')        
        tool = params.get('T')
        args = [temp,tool] 
        return args 
    
    def get_toggle_extra_output_args(self,comArgs):
        """
        Given the registers following a M126 or M127 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the toggle_extra_output function.
        """
        params, flags = self.get_params(comArgs)        
        args = [params.get('T')]
        return args
    
    def get_recall_home_positions_args(self,comArgs):
        """
        Given the registers following a M132 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the recall_home_positions function.
        """
        params, flags = self.get_params(comArgs)
        args = [flags]
        return args 
    
    def get_wait_for_tool_ready_args(self,comArgs):
        """
        Given the registers following a M133 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the wait_for_tool_ready function.
        """
        params, flags = self.get_params(comArgs)
        tool = params.get('T')         
        delay = 100
        timeout = params.get('P', 100)
        args =  [tool, delay, timeout]  
        return args 
    
    def get_wait_for_platform_ready_args(self,comArgs):
        """
        Given the registers following a M134 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the wait_for_platform_ready function.
        """
        params, flags = self.get_params(comArgs)
        tool = params.get('T')         
        delay = 100
        timeout = params.get('P', 60)
        args =  [tool, delay, timeout]     
        return args 
    
    def get_change_tool_args(self,comArgs):
        """
        Given the registers following a M135 command, calculate and return the correct arguments for calling the
        queue_extended_point_x3g function

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return list args: The necessary arguments for calling the change_tool function.
        """
        params, flags = self.get_params(comArgs)
        args = [params.get('T')] 
        return args
        
    def get_params(self, comArgs):
        """
        Given the registers following any gcode command, separate them into a dictionary of registers that had values,
        and a list of registers without values. (Which are to be considered flags.)

        @param string list comArgs: The registers of a gcode command, as a list of strings. (eg. ['X100', 'Y20'])
        @return dict params: Parameter dictionary parsed from the registers of the Gcode. (eg. {'X': 100, 'Y': 20})
        @return string list flags: Any register flags that appeared without numbers, in lower case form. (eg. ['x','y'])
        """
        params = {}
        flags = []
        
        for c in comArgs:
            if len(c) == 1:
                flags.append(c.lower())
            else:
                k = c[0]
                v = c[1:]
                params[k] = float(v)
        return params, flags
        
    def get_point(self, params):
        """
        Given a dictionary form of gcode registers, get the point in 5D space which the gcode is referring to.

        @param dict params: Parameter dictionary parsed from the registers of the Gcode. (eg. {'X': 100, 'Y': 20})
        @return float list point: The point specified in mm
        """
        spm = self.spm
        cpoint = self.current_point
        x = params.get('X',cpoint[0])
        y = params.get('Y',cpoint[1])
        z = params.get('Z',cpoint[2])
        a = cpoint[3]
        b = cpoint[4]
        if 'E' in params:
            a = params.get('E',cpoint[3])
        elif 'A' in params:
            a = params.get('A',cpoint[3])
        elif 'B' in params:
            b = params.get('B',cpoint[4])
        point = [x,y,z,a,b]
        return point

###########################################################################################################
### The below functions are copied (in essence) from Makerbot's s3g/makerbot_driver/Gcode/Utils.py file ###
###########################################################################################################

    def get_homing_dda(self, f, mf, spmList):
        """
        Given a set of feedrates and spm values, calculates the homing DDA speed
        We always use the limiting axis' feedrate and SPM
        constant, if applicable.  If there is no limiting axis, we default to
        the first axis' spm value.

        @param int f: The feedrate we want to move at (TODO: mm/min? mm/sec?)
        @param int list mf: The max feedrates we will be using (TODO: mm/min? mm/sec?)
        @param float list spmList: The steps_per_mm we use to calculate the DDA speed
        @return float dda: The speed we will be moving at
        """
        uf = f #Assuming f is in mm/min
        uspm = spmList[0]
        for m, s in zip(mf, spmList):#Assuming mf are in mm/min
            if m != 0:
                if uf > m:
                    uf = m
                    uspm = s
        dda = self.calc_dda(uf, uspm)
        return dda
    
    def get_movement_dda(self, cpoint, point, f, mf, spm):
        """
        Given an initial position, target position, and target feedrate, calculate an achievable
        travel speed.

        @param cpoint: 5D starting position of the move, in mm
        @param point: 5D target position to move to, in mm
        @param f: Requested feedrate, in mm/s (TODO: Is this correct???? mm/min?)
        @param mf: 5D vector of maximum feedrates, in mm/s (TODO: Is this correct???? mm/min?)
        @param spm: 5D vector of steps per milimeters conversion, in steps/mm
        @return float dda: The speed in us/step we move at
        """
        # Displacement Vector (Line 297)
        dv = self.calculate_vector_difference(point, cpoint)
        # Correct for safe feedrate
        af = self.get_safe_feedrate(dv, mf, f) #Assuming return of mm/min
        dvSteps = self.multiply_vector(dv, spm)
        la = self.find_longest_axis(dvSteps)
        vm = self.calculate_vector_magnitude(dv)
        if vm != 0:
            ff = af * (float(abs(dv[la])) / vm) #Assuming af in mm/min
            dda = self.calc_dda(ff, abs(spm[la])) #Assuming ff in mm/min
        else:
            dda = 0
        return dda
    
    def calculate_vector_difference(self, point, cpoint):
        """
        Given two 5d vectors represented as lists, calculates their
        difference (point - cpoint)

        @param list point: 5D vector to be subtracted from
        @param list cpoint: 5D vector to subtract from the minuend
        @return list difference
        """
        difference = []
        for m, s in zip(point, cpoint):
            difference.append(m - s)
        return difference
       
    def get_safe_feedrate(self, dv, mf, tf):
        """
        Given a displacement vector and target feedrate, calculates the fastest safe feedrate

        @param list dv: 5d Displacement vector to consider, in mm
        @param list mf: Maximum feedrates for each axis, in mm (per min?)
        @param float tf: Target feedrate for the move, in mm/s (TODO: Is this correct???? mm/min?)
        @return float actF: Achievable movement feedrate, in mm/s
        """
        magnitude = self.calculate_vector_magnitude(dv)
        actF = tf #Assuming tf in mm/min
        for d, m in zip(dv, mf): #Assuming mf in mm/min
            if (magnitude != 0) & (d != 0):
                af = float(tf) / magnitude * abs(d)
                if af > m:
                    actF = float(m) / abs(d) * magnitude #Use of m in mm/min, scaled by d*m
        return actF
        
    def multiply_vector(self, dv, spm):
        """
        Given two 5d vectors represented as lists, calculates their product.

        @param list dv: 5D vector
        @param list spm: 5D vector
        @return list product
        """
        product = []
        for a, b in zip(dv, spm):
            product.append(a * b)
        return product
        
    def find_longest_axis(self, vector):
        """
        Determine the index of the longest axis in a 5D vector.

        @param list vector: A 5D vector
        @return int: The index of the longest vector
        """
        max_value_index = 0
        for i in range(1, 5):
            if abs(vector[i]) > abs(vector[max_value_index]):
                max_value_index = i
        return max_value_index
        
    def calculate_vector_magnitude(self, vector):
        """
        Given a 5D vector represented as a list, calculate its magnitude

        @param list vector: A 5D vector
        @return magnitude of the vector
        """
        magnitude_squared = 0
        for d in vector:
            magnitude_squared += pow(d, 2)
    
        magnitude = pow(magnitude_squared, .5)

        return magnitude 
        
    def calc_dda(self, feedrate, spm):
        """
        Given a feedrate in mm/min, and SPM in steps/mm, calculate its DDA
        speed, in microSeconds/step.

        @param int feedrate: The desired movement speed in mm/min
        @param float spm: The steps per mm we use to get the DDA speed
        @return float dda: The dda speed we use
        """

        second_const = 60
        micro_second_const = 1000000
        #dda = micro_second_const / (feedrate * spm)
        dda = second_const * micro_second_const / (feedrate * spm) #Assuming feedrate in mm/min
        return dda
            
    def get_distance(self, point, cpoint):
        """
        Given two points of the same dimension, calculates their
        euclidean distance

        @param list point: 5D vector to be subtracted from
        @param list cpoint: 5D vector to subtract from the minuend
        @return int distance: Distance between the two points
        """
        distance = 0.0
        for m, s in zip(point, cpoint):
            distance += pow(m - s, 2)
        distance = math.sqrt(distance)
        return distance
