"""
statistical analysis
"""
import sys
import matplotlib.pyplot as plt
import randomModeGenerateService
import subprocess
import os
import math
import config as cfg

rmgs = randomModeGenerateService.RandomModeGenerateService(0.7, 1.2, 3.6, 2.1, 2.8, 4.1, 0.9, 0.91, 1.27,  # config 4
                                                           5000) # time_end. len(service_time) = 3 * time_end

def draw_histogram(data, bins, title='histogram', xlabel='x', ylabel='frequency'):
    plt.hist(data, bins=bins, edgecolor='black')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(bins)
    plt.show()

def interarrival_time():
    interarrival_time_list = rmgs.generate_interarrival_time(10000)
    bins = (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16)
    draw_histogram(interarrival_time_list, bins, 'Histogram of 10000 inter-arrival time distributed with test case 4', 'inter-arrival time')

def service_time():
    service_time_and_group = rmgs.generate_service_time()[1]
    service_time_list = [list(), list()]
    for time, group in service_time_and_group:
        service_time_list[group].append(time)
    print(max(service_time_list[0]))
    print(min(service_time_list[0]))
    print(max(service_time_list[1]))
    print(min(service_time_list[1]))
    bins0 = (1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6)
    draw_histogram(service_time_list[0], bins0, 'group 0: Histogram of service time distributed with test case 4', 'service time')
    bins1 = (2.8, 3, 3.2, 3.4, 3.6, 3.8, 4, 4.2, 4.4, 4.6, 4.8, 5, 5.2, 5.4, 5.6, 5.8, 6, 6.2, 6.4, 6.6, 6.8, 6.9)
    draw_histogram(service_time_list[1], bins1, 'group 1: Histogram of service time distributed with test case 4', 'service time')

def simulation_reproducible():
    repetitions = 100
    cmd = ('sh', 'run_test.sh', '4')
    mrt_output_path = os.path.join('output', 'mrt_4.txt')
    mean_response_time0_list = list()
    mean_response_time1_list = list()

    for i in range(repetitions):
        print('[info] {}th simulation'.format(i + 1))
        subprocess.run(cmd)
        with open(mrt_output_path) as f:
            line = f.read().strip().split()
            mean_response_time0_list.append(line[0])
            mean_response_time1_list.append(line[1])

    x = range(1, len(mean_response_time0_list) + 1)
    plt.plot(x, mean_response_time0_list, label='0')
    plt.plot(x, mean_response_time1_list, label='1')
    plt.title('mean response time 100 simulations with same seed')
    plt.xlabel('sequence')
    plt.ylabel('mean response time')
    plt.legend()
    plt.show()

def service_group():
    service_time_and_group = rmgs.generate_service_time()[1]
    service_group_counter = [0, 0]
    for _, group in service_time_and_group:
        service_group_counter[group] += 1
    print('group 0: {}, group 1: {}, group 0 / (group 0 + group1) = {}' \
          .format(service_group_counter[0], service_group_counter[1],
            service_group_counter[0] / (service_group_counter[0] + service_group_counter[1])))

def draw_mrtofk(response_time_list):
    for group in (0, 1):
        x = range(1, len(response_time_list[group]) + 1)
        y = list()
        for i in range(len(response_time_list[group])):
            y.append(sum(response_time_list[group][0:i+1]) / (i + 1))
        plt.plot(x, y, label=str(group))
    plt.ylabel('mean response time of first k jobs')
    plt.xlabel('k')
    plt.axhline(1.725, color='red', linestyle='--')
    plt.axhline(3.24, color='red', linestyle='--')
    plt.axvline(start_idx, color='red', linestyle='--')
    plt.legend()
    plt.show()

def modify_file(filename, line, str):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines[line] = str
    with open(filename, 'w') as f:
        f.writelines(lines)

para_path = os.path.join('config', 'para_10.txt')
start_idx = 1250
cmd = 'sh ./run_test.sh 10'
sampling_frequency = 30
n = 10 # total server
time_end = 10000

def mean_response_time_of_first_k():
    # time_end = 15000, n0 = 5 in para_10.txt
    modify_file(para_path, 1, '5\n')
    modify_file(para_path, 3, '15000\n')

    subprocess.run(cmd, shell=True)

    response_time_list = [list(), list()]
    with open('response_time_0.txt', 'r') as f:
        for rt in f:
            response_time_list[0].append(float(rt.strip()))
    with open('response_time_1.txt', 'r') as f:
        for rt in f:
            response_time_list[1].append(float(rt.strip()))
    for group in (0, 1):
        steady_mean_respones_time = sum(response_time_list[group][start_idx:]) / (len(response_time_list[group]) - start_idx)
        print('group {}: {}'.format(group, steady_mean_respones_time))
    draw_mrtofk(response_time_list)

def sample_standard_deviation(x, mean_value):
    S = 0
    for i in range(len(x)):
        S += (mean_value - x[i])**2
        return math.sqrt(S / ( len(x) - 1 ))
    
def confidence_interval(ssd, mv):
    lower_value = cfg.decimal_float_str(mv - 2 * ssd / math.sqrt(sampling_frequency))
    upper_value = cfg.decimal_float_str(mv + 2 * ssd / math.sqrt(sampling_frequency))
    
    return (lower_value, upper_value)

def determining_n0():
    mean = lambda x: sum(x) / len(x)

    modify_file(para_path, 3, '{}\n'.format(time_end))
    for n0 in range(1, n):
        modify_file(para_path, 1, '{}\n'.format(n0)) # n0 = 1,2,...,9. (n = 10)
        with open('n0_{}_wmrt.txt'.format(n0), 'w') as wmrt:
            for seed in range(sampling_frequency):
                print('[info] current: n0={}, seed={}'.format(n0, seed))
                response_time0 = []
                response_time1 = []
                service_time0 = []
                service_time1 = []
                modify_file('config.py', 0, 'random_seed = {}\n'.format(seed)) # use different random seeds for each sampling
                subprocess.run(cmd, shell=True)
                with open('response_time_0.txt', 'r') as f:
                    for line in f:
                        rt, t = line.strip().split()
                        response_time0.append(float(rt))
                        service_time0.append(float(t))
                with open('response_time_1.txt', 'r') as f:
                    for line in f:
                        rt, t = line.strip().split()
                        response_time1.append(float(rt))
                        service_time1.append(float(t))
                response_time0 = response_time0[start_idx:]
                response_time1 = response_time1[start_idx:]
                service_time0 = service_time0[start_idx:]
                service_time1 = service_time1[start_idx:]
                group0_percent = len(response_time0) / (len(response_time0) + len(response_time1))
                group1_percent = 1 - group0_percent
                w0 = group0_percent / mean(service_time0)
                w1 = group1_percent / mean(service_time1)
                mrt0 = mean(response_time0)
                mrt1 = mean(response_time1)
                wmrt.write('{}\n'.format(mrt0 * w0 + mrt1 * w1))

    print('-' * 100)
    print('n0\t|\tconfidence interval (group 0 | group 1)')
    for n0 in range(1, n):
        wrt_list = list()
        with open('n0_{}_wmrt.txt'.format(n0), 'r') as wmrt:
            for line in wmrt:
                wmrt_values = float(line.strip())
                wrt_list.append(wmrt_values)

        wmrt = mean(wrt_list)
        ssd = sample_standard_deviation(wrt_list, wmrt)
        ci = confidence_interval(ssd, wmrt)
        print('{}\t|\t{}'.format(n0, ci))

def main():
    if len(sys.argv) < 2:
        print('python3 data_process.py [item]')
        print('items:')
        print('\t0\tsimulation reproducible')
        print('\t1\tinter-arrival time')
        print('\t2\tservice group')
        print('\t3\tservice time')
        print('\t4\tmean response time of first k')
        print('\t5\tdetermining n0')
        exit(0)

    item = sys.argv[1]
    if item == '0':
        simulation_reproducible()
    elif item == '1':
        interarrival_time()
    elif item == '2':
        service_group()
    elif item == '3':
        service_time()
    elif item == '4':
        mean_response_time_of_first_k()
    elif item == '5':
        determining_n0()

if __name__ == '__main__':
    main()