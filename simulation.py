import baseInputOutput
import decimal
import config as cfg

class Dispatcher:
    def __init__(self, test_number):
        self.bio = baseInputOutput.BaseInputOutput(test_number)
        bio_config = self.bio.get_config()
        self.mode = bio_config[0][0]
        if self.mode == 'random':
            self.time_end = bio_config[0][1]
        n = bio_config[1]
        n0 = bio_config[2]
        t_limit = bio_config[3]
        self.arrival_time_list = bio_config[4]
        self.service_time_and_group_list = bio_config[5]

        self.queue = [list(), list()] # group 0 and group 1 queue

        self.service = Server(n, n0, t_limit)

        # print('[debug] mode, time_end = ', bio_config[0])
        # print('[debug] n = ', n)
        # print('[debug] n0 = ', n0)
        # print('[debug] t_limit = ', t_limit)
        # print('[debug] arrival_time_list length = ', len(self.arrival_time_list))
        # print('[debug] service_time_and_group_list length = ',len(self.service_time_and_group_list))
        # print('[debug] arrival_time_list = ', self.arrival_time_list)
        # print('[debug] service_time_and_group_list = ', self.service_time_and_group_list)
        # print('[debug] service_time_and_group_list type: ({}, {})'.format(type(self.service_time_and_group_list[0][0]), type(self.service_time_and_group_list[0][1])))
        # exit(1)

    def run(self):
        master_clock = decimal.Decimal('0')
        time_increment = decimal.Decimal(str(cfg.generate_decimal()))

        list_empty = False
        queue_empty = [False, False]

        while True:
            departure_service = self.service.check_departure(master_clock)
            if departure_service is not None:
                if departure_service[2] == 'ok':
                    # print('[debug] completed: master_clock={}, arrival_time={}, departure_time={}, service_group={}'.format(master_clock, departure_service[0][0], departure_service[0][1], departure_service[1]))
                    self.bio.generate_output(departure_service[0][0], departure_service[0][1], departure_service[0][2], departure_service[1])
                elif departure_service[2] == 're_circ':
                    
                    # print('[debug] killed -> service group 1 completed: master_clock={}, arrival_time={}, departure_time={}'.format(master_clock, departure_service[0][0], departure_service[0][1]))
                    self.bio.generate_output(departure_service[0][0], departure_service[0][1],departure_service[0][2], 'r0')
                elif departure_service[2] == 'timeout':
                    
                    # print('[debug] killed: master_clock={}, arrival_time={}, service_time={}'.format(master_clock, departure_service[0][0], departure_service[0][2]))
                    if self.service.check_idle(1)[0]:
                        
                        # print('[debug] killed -> service group 1')
                        self.service.add_service(departure_service[0][0], departure_service[0][2], 1, master_clock, True)
                    else:
                        
                        # print('[debug] killed -> queue 1')
                        self.queue[1].append((departure_service[0][0], departure_service[0][2], 0))

            for group in (0, 1):
                if len(self.queue[group]) != 0:
                    if self.service.check_idle(group)[0]:
                        arrival_time = self.queue[group][0][0]
                        service_time = self.queue[group][0][1]
                        service_group = self.queue[group][0][2]

                        if group == 1 and service_group == 0:
                            # print('[debug] (killed -> queue 1) -> service griup 1: master_clock={}, arrival_time={}, service_time={}'.format(master_clock, arrival_time, service_time))
                            self.service.add_service(arrival_time, service_time, 1, master_clock, True)
                        else:
                            # print('[debug] queue -> service: master_clock={}, arrival_time={}, service_time={}, service_group={}'.format(master_clock, arrival_time, service_time, service_group))
                            self.service.add_service(arrival_time, service_time, group, master_clock)
                        self.queue[group].pop(0)
                    
                    queue_empty[group] = False
                else:
                    queue_empty[group] = True
            
            # if float(master_clock).is_integer(): # debug
                # print('[info] **time** = {}'.format(master_clock))
                # self.service.get_status()
            
            if not list_empty:
                try:
                    arrival_time = self.arrival_time_list[0]
                    service_time, service_group = self.service_time_and_group_list[0]
                except IndexError:
                    list_empty = True
                    # print('[debug] list empty', master_clock)
                    # exit(1)
                else:
                    if self.mode == 'random' and master_clock > self.time_end - service_group:
                        list_empty = True
                    elif master_clock >= arrival_time:
                        # print('[debug] arrival event: maste_clock={}, arrival_time={}, service_time={}, service_group={}'.format(master_clock, arrival_time, service_time, service_group))
                        if self.service.check_idle(service_group)[0]:
                            # print('[debug] add service')
                            self.service.add_service(arrival_time, service_time, service_group, master_clock)
                        else:
                            
                            # print('[debug] add queue')
                            self.queue[service_group].append((arrival_time, service_time, service_group))
                        
                        self.arrival_time_list.pop(0)
                        self.service_time_and_group_list.pop(0)
                        
            if list_empty and queue_empty[0] and queue_empty[1] and self.service.check_idle(0)[1] and self.service.check_idle(1)[1]:
                self.bio.end()
                break

            master_clock += time_increment
            
class Server:
    def __init__(self, n, n0, t_limit):
        # [[idle/busy, (arrival time, departure time, service time), service group], ...]
        service_group0_status = [['idle', 'inf', -1] for _ in range(n0)]
        service_group1_status = [['idle', 'inf', -1] for _ in range(n - n0)]
        self.service_status = (service_group0_status, service_group1_status)
        self.t_limit = t_limit

    def check_idle(self, service_group):
        idle = False
        all_idle = True
        for sg in self.service_status[service_group]:
            if sg[0] == 'idle':
                idle = True
            elif sg[0] == 'busy':
                all_idle = False
        return (idle, all_idle)
        
    def check_departure(self, master_clock):
        master_clock = float(master_clock)
        for group in (0, 1):
            for sg in self.service_status[group]:
                if sg[0] == 'busy' and sg[1][1] <= master_clock: # depart
                    if group == 0 and sg[1][2] > self.t_limit:
                        departure_service = ((sg[1][0], sg[1][1], sg[1][2]), sg[2], 'timeout') # ((arrival time, departure time, service time), service group, 'timeout')
                    else:
                        if group == 1 and sg[2] == 0:
                            departure_service = ((sg[1][0], sg[1][1], sg[1][2]), sg[2], 're_circ')
                        else:
                            departure_service = ((sg[1][0], sg[1][1], sg[1][2]), sg[2], 'ok') # ((arrival time, departure time), service group, 'ok') 
                    sg[0] = 'idle'
                    return departure_service
        return None
                
    def add_service(self, arrival_time, service_time, service_group, master_clock, re_circ=False):
        # print('[debug] add_service function: master_clock={}, arrival_time={}, service_time={}, service_group={}, re_circ={}'.format(master_clock, arrival_time, service_time, service_group, re_circ))

        if re_circ:
            service_group = 1

        master_clock = float(master_clock)
        for sg in self.service_status[service_group]:
            if sg[0] == 'idle':
                sg[0] = 'busy'
                if service_group == 0 and service_time > self.t_limit:
                    sg[1] = (arrival_time, master_clock + self.t_limit, service_time)
                    sg[2] = service_group
                else:
                    sg[1] = (arrival_time, master_clock + service_time, service_time)
                    if re_circ:
                        sg[2] = 0
                    else:
                        sg[2] = service_group
                break

    def get_status(self):
        """ debug
        """
        print('-----------------------------------------------------------------------------------------------')
        for group in (0, 1):
            idx = 0
            for sg in self.service_status[group]:
                print('[debug] {} service status: [{}, {}, {}] {}'.format(idx, sg[0], sg[1], sg[2], group))
                idx += 1
        print('-----------------------------------------------------------------------------------------------')