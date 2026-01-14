import math

class StegaLCG:
    ''' Linear Congruent Generator '''

    def __init__(self, m, password):
        self.m = m[0] * m[1] if isinstance(m, tuple) else m
        self.size = [m[0], m[1]] if isinstance(m, tuple) else None
        self.state = self._generate_seed(password)
        self.count = 0

        self.c, self.a = self._get_parameters()
    
    def _generate_seed(self, password):

        return sum(ord(char) for char in password) % self.m

    def _get_parameters(self):
        # 1. Choose 'c': The simplest way is to find a large prime 
        # We'll find the smallest prime > m/2.
        c = 0
        candidate = self.m // 2 | 1 # Ensure it's odd
        while math.gcd(candidate, self.m) != 1:
            candidate += 2
        c = candidate

        # 2. Choose 'a': Find prime factors of m
        factors = set()
        temp_m = self.m
        d = 2
        while d * d <= temp_m:
            while temp_m % d == 0:
                factors.add(d)
                temp_m //= d
            d += 1
        if temp_m > 1:
            factors.add(temp_m)

        # a-1 must be a multiple of the product of all prime factors
        product_of_factors = 1
        for f in factors:
            product_of_factors *= f

        # Requirement 3: If m is multiple of 4, a-1 must be multiple of 4
        if self.m % 4 == 0:
            if product_of_factors % 4 != 0:
                product_of_factors *= (4 // math.gcd(product_of_factors, 4))

        # We want a to be reasonably large for better "randomness"
        # 'a' will be (k * product_of_factors) + 1
        a = product_of_factors + 1

        return a, c

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.count >= self.m:
            raise StopIteration
        
        self.state = (self.a * self.state + self.c) % self.m
        self.count += 1
        

        if not self.size:
            return self.state
        else:
            x = self.state % self.size[0]
            y = self.state // self.size[0]
            return (x, y)