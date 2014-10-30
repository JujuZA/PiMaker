from x3gparams import params

p = params('Replicator2')
    
def test_G1():
    comArgs = ['X100','Y200','Z300','F400']
    newArgs = [[8857.3186, 17714.6372, 120000.0, 0, 0],380.07324109027525, [], 121623.43714888809, 400.0]
    assert (p.get_queue_extended_point_args(comArgs) == newArgs)
   
def test_G4():
    comArgs = ['P100']
    newArgs = [100.0]
    assert (p.get_delay_args(comArgs) == newArgs)

def test_G92():
    comArgs = ['X100','Y200','Z300']
    newArgs = [[8857.3186, 17714.6372, 120000.0, 0, 0]]
    assert (p.get_set_extended_position_args(comArgs) == newArgs)

def test_G130():
    comArgs = ['X100','Y200','Z300','A400','B500'] 
    newArgs = [['y', 'x', 'b', 'z', 'a'], [200.0, 100.0, 500.0, 300.0, 400.0]]
    assert (p.get_set_potentiometer_value_args(comArgs) == newArgs)

def test_G161():
    comArgs = ['X','Y','F400']
    newArgs = [['x', 'y'], 1693.5147844856795]
    assert (p.get_find_axes_minimums_args(comArgs) == newArgs)

def test_G162():
    comArgs = ['Z','F400']
    newArgs = [['z'], 1693.5147844856795]
    assert (p.get_find_axes_maximums_args(comArgs) == newArgs)

def test_M18():
    comArgs = ['X', 'Z', 'B']
    newArgs = [['x', 'z', 'b'], False]
    assert (p.get_toggle_axes_args(comArgs) == newArgs)

def test_M70():
    comArgs = ['P20']
    comment = "We love making things!"
    newArgs = [20.0, 'We love making things!']
    assert (p.get_display_message_args(comArgs, comment) == newArgs)

def test_M72():
    comArgs = ['P7']
    newArgs = [7.0]
    assert (p.get_queue_song_args(comArgs) == newArgs)

def test_M73():
    comArgs = ['P75']
    newArgs = [75.0]
    assert (p.get_set_build_percent_args(comArgs) == newArgs)

def test_M104():
    comArgs = ['S230', 'T0']
    newArgs = [230.0, 0.0]
    assert (p.get_set_toolhead_temperature_args(comArgs) == newArgs)

def test_M109():
    comArgs = ['S90', 'T0']
    newArgs = [90.0, 0.0]
    assert (p.get_set_platform_temperature_args(comArgs) == newArgs)

def test_M126():
    comArgs = ['T0']
    newArgs = [0.0]
    assert (p.get_toggle_extra_output_args(comArgs) == newArgs)

def test_M127():
    comArgs = ['T0']
    newArgs = [0.0]
    assert (p.get_toggle_extra_output_args(comArgs) == newArgs)

def test_M132():
    comArgs = ['X', 'Z', 'B']
    newArgs = [['x', 'z', 'b']]
    assert (p.get_recall_home_positions_args(comArgs) == newArgs)

def test_M133():
    comArgs = ['T230','P50']
    newArgs = [230.0, 100, 50.0]
    assert (p.get_wait_for_tool_ready_args(comArgs) == newArgs)

def test_M134():
    comArgs = ['T90','P50']
    newArgs = [90.0, 100, 50.0]
    assert (p.get_wait_for_platform_ready_args(comArgs) == newArgs)

def test_M135():
    comArgs = ['T1']
    newArgs = [1.0]
    assert (p.get_change_tool_args(comArgs) == newArgs)

    