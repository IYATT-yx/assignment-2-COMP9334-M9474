"""
Read the test case file and save the output file.
"""
import os
import randomModeGenerateService
import config as cfg

class BaseInputOutput:
    def __init__(self, test_number):
        config_path = 'config'
        output_path = 'output'
        mode_prefix = 'mode_'
        para_prefix = 'para_'
        interarrival_prefix = 'interarrival_'
        service_prefix = 'service_'
        dep_prefix = 'dep_'
        mrt_prefix = 'mrt_'
        suffix = '.txt'
        self.test_number = str(test_number)

        mode_file_path = os.path.join(config_path, mode_prefix + self.test_number + suffix)
        para_file_path = os.path.join(config_path, para_prefix + self.test_number + suffix)
        interarrival_file_path = os.path.join(config_path, interarrival_prefix + self.test_number + suffix)
        service_file_path = os.path.join(config_path, service_prefix + self.test_number + suffix)
        dep_file_path = os.path.join(output_path, dep_prefix + self.test_number + suffix)
        mrt_file_path = os.path.join(output_path, mrt_prefix + self.test_number + suffix)

        # read mode_*.txt
        with open(mode_file_path, 'r') as mode_file:
            self.mode = mode_file.read().strip()

        # read para_*.txt
        with open(para_file_path, 'r') as para_file:
            self.total_number_of_services = int(para_file.readline().strip())
            self.number_of_group0_services = int(para_file.readline().strip())
            self.t_limit = float(para_file.readline().strip())
            if self.mode == 'random':
                self.time_end = int(para_file.readline().strip())

        # read interarrival_*.txt
        with open(interarrival_file_path, 'r') as interarrival_file:
            if self.mode == 'trace':
                self.interarrival_time_list = [float(line.strip()) for line in interarrival_file]
            elif self.mode == 'random':
                paras = interarrival_file.readline().split()
                self.lambd = float(paras[0])
                self.alpha2l = float(paras[1])
                self.alpha2u = float(paras[2])

        # read service_*.txt
        with open(service_file_path, 'r') as service_file:
            if self.mode == 'trace':
                self.service_time_and_group_list = list()
                for line in service_file:
                    service_time_and_group = line.strip().split()
                    service_time = float(service_time_and_group[0])
                    service_group = int(service_time_and_group[1])
                    self.service_time_and_group_list.append((service_time, service_group))
            elif self.mode == 'random':
                self.p0 = float(service_file.readline().strip())
                line2 = service_file.readline().strip().split()
                self.alpha0 = float(line2[0])
                self.beta0 = float(line2[1])
                self.eta0 = float(line2[2])
                line3 = service_file.readline().strip().split()
                self.alpha1 = float(line3[0])
                self.eta1 = float(line3[1])

        # output file
        dep_file = open(dep_file_path, 'w')
        mrt_file = open(mrt_file_path, 'w')
        self.output_file = (dep_file, mrt_file)
        self.response_time = [list(), list()]
        self.output_list = list()
        self.service_time0 = list()
        self.service_time1 = list()

        # print test case parameters
        if self.mode == 'random':
            print('[info] mode={}, n={}, n0={}, T_limit={}, time_end={}, lambda={}, alpha2l={}, alpha2u={}, p0={}, alpha0={}, beta0={}, eta0={}, alpha1={}, eta1={}, seed={}'.format(
                self.mode, self.total_number_of_services, self.number_of_group0_services, self.t_limit, self.time_end, self.lambd, self.alpha2l, self.alpha2u, self.p0, self.alpha0, self.beta0, self.eta0, self.alpha1, self.eta1, cfg.random_seed
            ))
        else:
            print('[info] mode={}, n={}, n0={}, T_limit={}'.format(
                self.mode, self.total_number_of_services, self.number_of_group0_services, self.t_limit
            ))

    def get_config(self):
        """ get test case parameters and test data(contains randomly generated parameters)
        """
        if self.mode == 'random':
            rmgs = randomModeGenerateService.RandomModeGenerateService(self.p0, self.alpha0, self.beta0, self.eta0, self.alpha1, self.eta1, self.lambd, self.alpha2l, self.alpha2u, self.time_end)
            self.interarrival_time_list, self.service_time_and_group_list = rmgs.generate_service_time()
            mode = (self.mode, self.time_end)
        elif self.mode == 'trace':
            mode = (self.mode, None)


        arrival_time = 0
        arrival_time_list = list()
        for t in self.interarrival_time_list:
            arrival_time += t
            # arrival_time_list.append(cfg.decimal_float(arrival_time))
            arrival_time_list.append(arrival_time)

        return (mode,
                self.total_number_of_services,
                self.number_of_group0_services,
                self.t_limit,
                arrival_time_list,
                self.service_time_and_group_list)
    
    def generate_output(self, arrival_time, depart_time, service_time, classification):
        """ write service information into the output file
        """
        self.output_list.append((arrival_time, depart_time, classification))
        
        classification = str(classification)
        # print('[debug] generate_output function: classification={}, type={}'.format(classification, type(classification)))
        # exit(1)

        if classification == '0':
            self.response_time[0].append(depart_time - arrival_time)
            self.service_time0.append(service_time)
        elif classification == '1':
            self.response_time[1].append(depart_time - arrival_time)
            self.service_time1.append(service_time)

    def end(self):
        """ complete file save and close
        """
        for arrival_time, depart_time, classification in self.output_list:
            self.output_file[0].write('{} {} {}\n'.format(cfg.decimal_float_str(arrival_time), cfg.decimal_float_str(depart_time), str(classification)))

        mean_response_time0 = cfg.decimal_float_str(sum(self.response_time[0]) / len(self.response_time[0]))
        mean_response_time1 = cfg.decimal_float_str(sum(self.response_time[1]) / len(self.response_time[1]))
        self.output_file[1].write('{} {}'.format(mean_response_time0, mean_response_time1))

        for f in self.output_file:
            f.close()

        if self.test_number == '10':
            response_time_0 = open('response_time_0.txt', 'w')
            response_time_1 = open('response_time_1.txt', 'w')

            for rt, t in zip(self.response_time[0], self.service_time0):
                response_time_0.write('{} {}\n'.format(rt, t))
            for rt, t in zip(self.response_time[1],self.service_time1):
                response_time_1.write('{} {}\n'.format(rt, t))

            response_time_0.close()
            response_time_1.close()