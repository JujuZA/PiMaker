__author__ = 'Jason'

import spidev
import RPi.GPIO as gpio
import time
import numpy
import json
import bottle

def get_pot_val(spi, chip):
    val = 0
    spi.open(0,chip)

    for x in range(100):
        resp = spi.xfer2([0x00, 0x00])
        msb = (resp[0] & 31) << 7
        lsb = (resp[1] & 254) >> 1
        res = msb + lsb
        val += res
        time.sleep(0.001)

    spi.close()

    return val/100.0

def get_sls_val(pin):
    return gpio.input(pin)

def get_filament_present(pin):
    d = ['No', 'Yes']
    f = get_sls_val(pin)
    return d[f]

def get_lever_angle(spi):
    zval = 574.9
    nval = 3058.2
    dval = nval - zval
    val = get_pot_val(spi, 0) - zval
    theta = val * (180.0/dval)
    return theta

def get_roll_radius(spi):
    """
    Z and phi have been hard coded so that they are not recalculated every time,
    and they were calculated as follows:
    vd = 143.0
    hd = 48.0

    z = numpy.hypot(vd,hd)

    c = 180.0/numpy.pi
    phi = numpy.arctan(48.0/143.0)*c
    """
    theta = get_lever_angle(spi)
    z = 150.8409758653132
    phi = 18.555065585131956
    c = 57.29577951308232
    y = z * numpy.sin((theta - phi)/c)
    af = 13
    return (y - af)

def get_length_by_layer(spi):
    y = get_roll_radius(spi)
    i = 44.5 #Inner radius of filament roll
    m = int((y-i)/1.75) #Layers of filament on roll, rounded down
    #Formula for this part in workbook
    l = 29.75*(m**2) + 3026*m
    mval = 103389.75
    l = (l/mval)*100

    if l < 0:
        l = 0
    elif l > 100:
        l = 100

    return l

def get_roller_angle(spi):
    zval = 15
    mval = 3733
    dval = mval - zval
    val = get_pot_val(spi, 1) - zval
    theta = val * (359.0/dval)
    return theta

def has_roller_moved(spi):
    value = get_roller_angle(spi)
    ti = time.time()

    f = open('roll.json','r+')
    d = json.loads(f.readline())
    f.close()

    pt = d['time'][0]
    pv = d['value'][0]

    nd = {}
    nd['time'] = d['time'][1:]
    nd['time'].append(ti)
    nd['value'] = d['value'][1:]
    nd['value'].append(value)

    f = open('roll.json','w+')
    f.write(json.dumps(nd))
    f.close()

    dl = []

    vd =  nd['value'][0] - nd['value'][-1:][0]
    td =  nd['time'][0] - nd['time'][-1:][0]

    resp = 'No'
    delta = 0.0
    if td != 0:
        delta = abs(vd/td)

    if delta > 0.2:
        resp = 'Yes'
    return resp, delta

pin = 18
spi = spidev.SpiDev()
gpio.setmode(gpio.BOARD)
gpio.setup(pin,gpio.IN)
rv = 5
v = numpy.ones(rv)*get_roller_angle(spi)
t = numpy.ones(rv)*time.time() + numpy.arange(rv)
d = {'time':list(t),'value':list(v)}
f = open('roll.json','w+')
f.write(json.dumps(d))
f.close()

@bottle.route('/')
def index():
    sensors = {}
    sensors['amount'] = '%.2f %%' % get_length_by_layer(spi)
    r,d = has_roller_moved(spi)
    sensors['roller'] = r + ('(%.2f)' % d)
    sensors['filament'] = get_filament_present(pin)
    return sensors

bottle.run(host='0.0.0.0',port=5700)
