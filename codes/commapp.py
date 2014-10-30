import makerbot_comm
import time
import bottle
import multiprocessing

p_pipe, c_pipe = multiprocessing.Pipe()

def commloop(w_pipe):
    mb = makerbot_comm.makerbot()
    p = 0
    gcodequeue = []
    gcn = 0
    printing = False
    bfs = 512
    tflag = False

    while(not tflag):
        try:
            if w_pipe.poll():
                message = w_pipe.recv()
                print message
                if message[0] == 'terminate':
                    mb.r.abort_immediately()
                    mb.close()
                    tflag = True
                if message[0] == 'cancel':
                    mb.r.abort_immediately()
                    gcodequeue = []
                    gcn = 0
                    printing = False
                    bfs = 512
                elif message[0] == 'percent':
                    w_pipe.send(p)
                elif message[0] == 'temp':
                    temp = mb.r.get_toolhead_temperature(0)
                    w_pipe.send(temp)
                elif message[0] == 'buffer':
                    w_pipe.send(bfs)
                elif message[0] == 'filename':
                    w_pipe.send(mb.buildname)
                elif message[0] == 'loadfile':
                    f = open(message[1]+'.gcode')
                    mb.buildname = message[1]
                    for line in f:
                        gcodequeue.append(line)
                    gcn = 0
                elif message[0] == 'print':
                    printing = True
                    print printing
            elif printing == True:
                if gcn < len(gcodequeue):
                    bfs = mb.r.get_available_buffer_size()
                    if bfs > 50:
                        call, args = mb.gcode_to_command(gcodequeue[gcn])
                        if call == 'set_build_percent':
                            p = args[0]
                        mb.execute_inter_command(call, args)
                        gcn += 1
                    else:
                        time.sleep(0.1)
                else:
                    gcodequeue = []
                    gcn = 0
                    printing = False
                    bfs = 512

        except KeyboardInterrupt:
            mb.close()
            tflag = True

@bottle.route('/')
def feedback():
    p_pipe.send(['temp'])
    t = '%d' % int(p_pipe.recv())
    t = t + u'\u2103'
    p_pipe.send(['percent'])
    p = '%d %%' % int(p_pipe.recv())
    p_pipe.send(['buffer'])
    bfs = p_pipe.recv()
    p_pipe.send(['filename'])
    fn = p_pipe.recv()
    return {'temp': t, 'percent': p, 'bfs': bfs, 'fn':fn}

@bottle.route('/file/<filename>')
def feedback(filename):
    p_pipe.send(['loadfile',filename])
    return filename + ' loaded to server'

@bottle.route('/print')
def feedback():
    p_pipe.send(['print'])
    return 'Printing!'

@bottle.route('/cancel')
def feedback():
    p_pipe.send(['cancel'])
    return 'Print Cancelled'

@bottle.route('/terminate')
def feedback():
    p_pipe.send(['terminate'])
    return 'Terminated'

if __name__ == '__main__':
    pcontrol_process = multiprocessing.Process(target=commloop, args=(c_pipe, ))
    pcontrol_process.start()

    bottle.run(host='0.0.0.0',port=5600)
    pcontrol_process.join()
