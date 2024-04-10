import random
import config as cfg

class RandomModeGenerateService:
    def __init__(self, p0, alpha0, beta0, eta0, alpha1, eta1, lambd, alpha2l, alpha2u, time_end):
        self.p0 = p0
        self.alpha0 = alpha0
        self.beta0 = beta0
        self.eta0 = eta0
        self.alpha1 = alpha1
        self.eta1 = eta1
        self.lambd = lambd
        self.alpha2l = alpha2l
        self.alpha2u = alpha2u
        self.time_end = time_end

        random.seed(cfg.random_seed)

        # service group
        self.choice = [0, 1]
        self.weights = [self.p0, 1 - self.p0]

    def generate_service_time(self):
        interarrival_time_list = self.generate_interarrival_time(3 * self.time_end)

        gamma0 = self.alpha0**(-self.eta0) - self.beta0*(-self.eta0)
        gamma1 = self.alpha1**(-self.eta1)

        service_time_and_group_list = list()

        g0 = lambda x: self.eta0 / (gamma0 * x**(self.eta0 + 1))
        g1 = lambda x: self.eta1 / (gamma1 * x**(self.eta1 + 1))

        for _ in interarrival_time_list:
            service_group = random.choices(self.choice, self.weights)[0]
            
            if service_group == 0:
                while True:
                    random_t0 = (self.beta0 - self.alpha0) * random.uniform(0, 1) + self.alpha0
                    random_g0 = random.uniform(0, 1)
                    if random_g0 <= g0(random_t0):
                        service_time_and_group_list.append((random_t0, service_group))
                        break
            elif service_group == 1:
                while True:
                    random_t1 = self.alpha1 + random.expovariate(1)
                    random_g1 = random.uniform(0, 1)
                    if random_g1 <= g1(random_t1):
                        service_time_and_group_list.append((random_t1, service_group))
                        break
        return (interarrival_time_list, service_time_and_group_list)
                
    def generate_interarrival_time(self, size):
        a1_sequence = [random.expovariate(self.lambd) for _ in range(size)]
        a2_sequence = [random.uniform(self.alpha2l, self.alpha2u) for _ in range(size)]
        return [a1 * a2 for a1, a2 in zip(a1_sequence, a2_sequence)]