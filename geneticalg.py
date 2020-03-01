from random import random, randint
import copy
generation = 0 

#Input
dim = 20
p = 6
recomb = 0.25
mut = 0.05
etape = 50
f_dom = [-1,2]
coef = [-1,1,2]
#End input

#Output file
F = open("rez1.txt","w")

def binary_search(v,s,f,el):
    if s <= f:
        mid = s + (f-s) // 2

        if el >= v[mid] and el < v[mid + 1]:
            return mid + 1
        elif el > v[mid]:
            return binary_search(v,mid +1,f,el)
        else:
            return binary_search(v,s,mid - 1,el)
    
    return -1
        

def gen_bin(l):
    binary = []
    for i in range(l):
        if random() <= 0.5:
            binary.append('0')
        else:
            binary.append('1')
    return ''.join(binary)


class Chromosome:

    def __init__(self, length = None):
       self.length = length
       self._binary = gen_bin(self.length)


    @property
    def binary(self):
        return self._binary

    @binary.setter
    def binary(self,value):
        self._binary = value
    
    @property
    def selection_prob(self):
        return self._selection_prob

    @selection_prob.setter
    def selection_prob(self,value):
        self._selection_prob = value

    def decode_bin(self, func_dom, prec):
        decimal = 0
        for i in range(self.length):
            if self.binary[self.length - i - 1] == '1':
                decimal += 2**i

        return round(decimal * (func_dom[1] - func_dom[0]) / 
        (2**self.length -1) + func_dom[0],prec)    
        


def c_len(f_dom, prec):
    x = (f_dom[1] - f_dom[0])  * 10**prec

    len = 1

    while 2**len < x:
        len += 1

    return len

def get_fx(x,coef):
    return (coef[0]*x**2 + coef[1]*x + coef[2])


def prob_selectie(population, f_dom, prec, coef):
    if generation == 0:
        F.write("\nProb selectie\n")

    
    i = 0 
    for chrom in population:

        bin = chrom.decode_bin(f_dom,p)

        fx = get_fx(bin,coef)

         #suma f(x)-urilor
        sum = 0.0
        for c in population:
            b = c.decode_bin(f_dom,p)
            f_x = get_fx(b,coef)
            sum += f_x

        chrom.selection_prob = fx / sum

        if generation == 0:
            F.write("chromosome {a}, prob {b} \n".format(a = i+1, b = chrom.selection_prob))
            i+=1


    selection_interval = [0,population[0].selection_prob]

    for chrom in population[1:]:
        selection_interval.append(selection_interval[-1] + chrom.selection_prob)

    if generation == 0:
        F.write("\nSelection Interval\n")
        for interval in selection_interval:
            F.write(str(interval))
            F.write("\n")
       
    
    return selection_interval

def rearanjare(selection_interval, population, f_dom,p,coef):

    new_pop = []

    for i in range(len(population)):
        prob = random()

        index = binary_search(selection_interval,0,len(population)-1,prob)

        if generation == 0:
            F.write("u= {a}, selectam {b}\n".format(a = prob, b = index))

        new_pop.append(copy.deepcopy(population[index - 1]))

    return new_pop

def crossover(c1,c2):
    c_bar = randint(0,c1.length -1)

    b1 = list(c1.binary)
    b2 = list(c2.binary)

    if generation == 0:
        F.write("{a}  {b} bariera {c}\n".format(a=c1.binary,b=c2.binary,c=c_bar))

    for i in range(c_bar):
        temp = b1[i]
        b1[i] = b2[i]
        b2[i] = temp

    c1.binary = ''.join(b1)
    c2.binary = ''.join(b2)

    if generation == 0:
        F.write("Rezultat: {a}  {b}\n".format(a = c1.binary,b=c2.binary))



def crossover_select(population, recomb):
    if generation == 0:
        F.write("Probabilitate crossover: {a}\n".format(a = recomb))

    chrom_select = []
    chrom_select_index = []

    i = 0 
    for chrom in population:
        probability = random()

        if generation == 0:
            F.write("{a}: {b}, u = {c}\n".format(a=i+1,b=chrom.binary, c=probability))


        if probability < recomb:
            chrom_select.append(chrom)
            chrom_select_index.append(i+1)
            if generation == 0:
                F.write(" < {a} participa\n".format(a=recomb))  

        i+=1
    
    if len(chrom_select) % 2:
        chrom_select = chrom_select[:-1]
    
    for i in range(0,len(chrom_select)-1,2):
        if generation == 0:
            F.write("\nCrossover intre cromozomii {a} si {b}\n".format(a = chrom_select_index[i],b=chrom_select_index[i+1]))

        crossover(chrom_select[i],chrom_select[i+1])  

def mutation(c):
    b = list(c.binary)
    num = randint(0,c.length - 1)
    for i in range(num):
        if b[i] == '0':
            b[i] = '1'
        else:
            b[i] = '0'

    c.binary=''.join(b)

def mutation_select(population,mut):
    if generation == 0:
        F.write("\nProbabilitate mutatie {a}".format(a = mut))
        F.write("\nUrmatorii cromozomi au suferit mutatii: \n")

    i = 0
    for chrom in population:
        probability = random()

        if probability < mut:
            if generation == 0:
                F.write("{a}, ".format(a = i+1))
                mutation(chrom)



def max_in_pop(population, f_dom, coef, prec):
    maxim = -999999999
    for i in population:
        if get_fx(i.decode_bin(f_dom, prec),coef) > maxim:
            maxim = get_fx(i.decode_bin(f_dom, prec),coef)
    return maxim

def av_in_pop(population,f_dom,coef,prec):
    sum = 0
    for c in population:
        sum += get_fx(c.decode_bin(f_dom,p),coef)
    return sum/len(population)

#Initial population
population = []

chrom_length = c_len(f_dom,p)

for i in range(dim):
    c = Chromosome(chrom_length)
    population.append(c)
    #print(c.decode_bin(f_dom,p))
    F.write("{a}: {b} x={c} f={d}\n".format(a=i+1, b=c.binary, c=c.decode_bin(f_dom,p),d=get_fx(c.decode_bin(f_dom,p),coef)))
    
#End initial population
max_val = []
av_val = []
while generation < etape:
    
    max_val.append(max_in_pop(population,f_dom,coef,p))
    av_val.append(av_in_pop(population,f_dom,coef,p))
    
    selection_interval = prob_selectie(population,f_dom,p,coef)

    population = rearanjare(selection_interval,population,f_dom,p,coef)

    if generation == 0:
        F.write("\n Dupa selectie: \n")
        i = 0
        for c in population:
            F.write("{a}: {b} x= {c} f={d}\n".format(a=i+1,b=c.binary,c=c.decode_bin(f_dom,p),d=get_fx(c.decode_bin(f_dom,p),coef)))
            i += 1

    crossover_select(population,recomb)

    mutation_select(population,mut)

    
    generation += 1

max_val.append(max_in_pop(population, f_dom, coef, p))
av_val.append(av_in_pop(population,f_dom,coef,p))
F.write("\naverage evo:\n")
for i in av_val:
    F.write("{a}\n".format(a=i))
F.write("\nMax val evo:\n")
for i in max_val:
    F.write("{a}\n".format(a = i))
