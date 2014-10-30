# -*- coding: utf-8 -*-
"""
Created on Wed Sep 03 10:25:36 2014

@author: Jason
"""

from x3gparams import params
import Utils as ut

xp = params('Replicator2')
spm = xp.spm
mf = xp.mf
pl = xp.pl

def test_get_homing_dda():
    mut = ut.calculate_homing_DDA_speed(2000, mf, spm)
    nut = xp.get_homing_dda(2000, mf, spm)
    assert (mut == nut)

def test_get_movement_dda():
    mut = ut.calculate_DDA_speed([100,200,100,0,0], [0,0,30,0,0], 20000, mf, spm)
    nut = xp.get_movement_dda([100,200,100,0,0], [0,0,30,0,0], 20000, mf, spm)
    assert (mut == nut)

def test_calculate_vector_difference():
    mut = ut.calculate_vector_difference([100,200,100,0,0], [0,0,30,0,0])
    nut = xp.calculate_vector_difference([100,200,100,0,0], [0,0,30,0,0])
    assert (mut == nut)
   
def test_get_safe_feedrate():
    mut = ut.get_safe_feedrate([100, 200, 0, 0, 0],mf,20000)
    nut = xp.get_safe_feedrate([100, 200, 0, 0, 0],mf,20000)
    assert (mut == nut)
    
def test_multiply_vector():
    mut = ut.multiply_vector([100, 200, 70, 0, 0],spm)
    nut = xp.multiply_vector([100, 200, 70, 0, 0],spm)
    assert (mut == nut)
    
def test_find_longest_axis():
    mut = ut.find_longest_axis([8857.3186, 17714.6372, 28000, -0.0, 0])
    nut = xp.find_longest_axis([8857.3186, 17714.6372, 28000, -0.0, 0])
    assert (mut == nut)
    
def test_calculate_vector_magnitude():
    mut = ut.calculate_vector_magnitude([100, 200, 70, 0, 0])
    nut = xp.calculate_vector_magnitude([100, 200, 70, 0, 0])
    assert (mut == nut)
    
def test_calc_dda():
    mut = ut.compute_DDA_speed(20000,spm[1])
    nut = xp.calc_dda(20000,spm[1])
    assert (mut == nut)
        
def test_get_distance():
    mut = ut.calculate_euclidean_distance([100,200,100,0,0], [0,0,30,0,0])
    nut = xp.get_distance([100,200,100,0,0], [0,0,30,0,0])
    assert (mut == nut)