#2.853 Final Project - Drew, Irma - Simulation V0
import os;
import random;
import time;
import numpy;
percentileGoal = 0.95
st = time.time()
totalcost = 0
name = os.path.basename(__file__)
path = __file__[:-len(name)]
batchno = 17
outputpath = path + "Batch" + str(batchno) + "/"
optimizationCycles = 10
simulationCycles = 40
hoursoperational = 16 #how many hours per day is it operational?
workertype = 0
duration = hoursoperational*60 #operational minutes
operationalDays = 1 #How many days of operation
productiongoal = int(round(1000000*(operationalDays*480/120000),0))
viable = []
targets = [12, 8, 8, 22, 1, 10, 116, 9999, 9999, 9999, 9999, 9999, 9999]
lasttargets=[]
samples = [1,1,1,1,1,1]
for i in range(len(samples)*2):
    lasttargets.append([0,0,0,0,0,0,0,0, 0, 0, 0, 0, 0])

lasttargets[0] = targets
switch = True
stepnum = 0
teststeps = [1]

breakchecker = True

    

for z in range(optimizationCycles):
    interim = []
    interim.extend(samples)
    interim.extend(samples)
    teststeps.extend(interim)

#Stages of production: Inner Core   - 0:Injection molder ------------------------------------>6: Assembly
#                      Outer Core   - 1:Injection molder -------------------------------------^
#                      Spinner Base - 2: Injection molder -------------------------------------^
#                      Spinner Face - 3:Plastic Printer -> 4:Thermoformer -> 5:Die Puncher ^

#Class definitions:

#20,000.00 per 100,000 injection molding pieces -> added in as 20cent use cost

class Machine:
    def __init__(self, name, type):
        self.name = name 
        self.type = type
        types = [["Injection Molder - Body", (64200.00), ((.1961/60)*15.5 + 0.2), True, False, 3, 0.00002, 0.0667, 4, 9], #45 seconds to make 1 part, each part is 9g
                 ["Injection Molder - Cover", (64200.00), ((.1961/60)*15.5 + 0.2), True, False, 1, 0.00002, 0.0667, 2, 10], #30 seconds each part is 10g
                 ["Injection Molder - Spinner", (64200.00), ((.1961/60)*15.5 + 0.2), True, False, 1, 0.00002, 0.0667, 2, 5], #30 seconds each part is 10g
                 ["Printer", 24320.00, ((.1961/60)*6), True, False, 20, 0.0000347, 0.1, 15, 1], #stock is 1 sheet
                 ["Thermoformer", 22500.00, ((.1961/60)*31 + 0.2), True, False, 1, 0.00002, 0.0667, (72*2), 1], #30 seconds per batch 1 sheet
                 ["Die Puncher", (3462.00 + 184.00), ((.1961/60)*5 + 0.2), True, False, 1, 0.00002, 0.0667, 3, 1]] #20 seconds per 1 sheet

        [self.typename, self.cost, self.usecost, self.status, self.wip, self.duration, self.failprob, self.repaprob,self.batch,self.stocky] = types[self.type]
        self.counter = 0
        self.progress = 0


    def __str__(self):
        letter = "Machine Name: " + str(self.name) + "\n"
        letter += " Machine Type: " + str(self.typename) + "\n"
        letter += " Machine Operational? " + str(self.status) + "\n"
        letter += " Machine Holding WIP? " + str(self.wip) + " for " + str(self.counter) + " turns, Machine is " + str(self.duration - self.progress) + " steps from completion\n"
        letter += " Initial Cost: " + str(self.cost) + "\n"
        letter += " Failure Probability: " + str(self.failprob) + "\n"
        letter += " Repair Probability: " + str(self.repaprob) + "\n"
        letter += " Batch Size: " + str(self.batch) + "\n"
        return letter
    
    def available(self):
        if self.status == True and self.wip == False:
            return True
        else:
            return False
        
    def load(self):
        if self.status == True and self.wip == False:
            self.wip = True
            self.counter = 0
            return [-self.batch,-self.stocky]
        else:
            return [0,0]

    def run(self, exitspace):
        if exitspace == True:
            self.counter += 1
            if self.status == True and self.wip == True:
                self.progress += 1
                global totalcost
                totalcost += self.usecost

                if random.random() <= self.failprob:
                    self.status = False
                    self.counter = 0
                

            if self.status == False and random.random() <= self.repaprob:
                self.status = True
                self.counter = 0

            if self.progress >= self.duration:
                self.wip = False
                self.progress = 0
                self.counter = 0
                return self.batch
            else:
                return 0
        else:
            return 0
        
class Worker:
    def __init__(self, name, type):
        self.name = name
        global duration
        types = [[.25, True, False, 7, int(round(duration*(2/480),0)),1],
                 [.75, True, False, 18, int(round(duration*(2/480),0)),5],
                 [.25, True, False, 7, int(round(duration*(2/480),0)),1]]
        [self.wage, self.status, self.wip, self.duration, self.rest, self.batch] = types[type]
        self.counter = 0
        self.progress = 0
        self.fatigue = 0
        self.restcount = 0

    def __str__(self):
        letter = "Worker ID: " + str(self.name) + "\n"
        letter += " Worker Holding WIP? " + str(self.wip) + " for " + str(self.counter) + " turns, Worker is " + str(self.duration - self.progress) + " steps from completion\n"
        letter += " Worker Wage: " + str(self.wage) + "\n"
        letter += " Worker Breaks Remaining: " + str(self.rest) + "\n"
        letter += " Active? " + str(self.status) + "\n"
        return letter
    
    def available(self):
        if self.wip == False:
            return True
        else:
            return False
        
    def load(self):         
        if self.status == True and self.wip == False:
            self.wip = True
            self.counter = 0
            return -self.batch*2 #2 parts per yoyo
        else:
            return 0

    def run(self):
        global totalcost
        if self.rest > 0: #Simulates random worker fatigue for when they want to utilize their self.rest x 30 minute unpaid breaks
            self.fatigue += random.randint(0,2)

        if self.fatigue >= 120:
            self.status = False
            self.restcount += 1

        if self.restcount >= 30:
            self.restcount = 0
            self.status = True
            self.fatigue = 0
            if self.rest > 0:
                self.rest += -1

        if self.status == True:
            
            totalcost += self.wage
            
            self.counter += 1         

            if self.wip == True:
                self.progress += 1
                

            if self.progress >= self.duration:
                self.wip = False
                self.progress = 0
                self.counter = 0
                return self.batch
            else:
                return 0
        else:
            return 0


        

def loadmachines(type, feeder,factory):
    for i in range(len(factory)):
        machine = factory[i]
        if machine.type == type:
            if machine.available() == True and feeder >= machine.batch:
                [letter,throwaway] = machine.load()
                feeder += letter
    return feeder

def loadworkers(staff,feeders):
    for i in range(len(staff)):
        worker = staff[i]
        condition = True
        for j in range(len(feeders)):
            if feeders[j] >= (worker.batch*2) and condition == True:
                condition = True
            else:
                condition = False

        if worker.available() == True and condition == True:
            letter = worker.load()
            for j in range(len(feeders)):
                feeders[j] += letter
            #("loaded" + str(buffer))
            #(machine)
    return feeders

def runsupply(type, imsupply, fltsupply,factory):
    for i in range(len(factory)):
        machine = factory[i]
        throwaway = 0
        if machine.type == type:
            if machine.available() == True and machine.type == 0 or 1 or 2:
                [throwaway, letter] = machine.load()
                imsupply += letter
                #("loaded" + str(buffer))
                #(machine)
            elif machine.available() == True and machine.type == 3:
                [throwaway, letter] = machine.load() #4"x4" tablets
                fltsupply += letter
                #("loaded" + str(buffer))
                #(machine)
    return imsupply, fltsupply
                 
def runmachines(type, reci, recimax, factory):
    for i in range(len(factory)):
        machine = factory[i]
        if machine.type == type:
            reci += machine.run(reci < recimax)
    return reci

def runworkers(staff):
    output = 0
    for i in range(len(staff)):
        worker = staff[i]
        output += worker.run()
    return output

def setupcombinations(targets,lasttargets,step):
    brackets = []
    output = []
    
    for i in range(7):
        target = targets[i]
        condition = True
        for j in range(len(lasttargets)-1):
            if lasttargets[j][i] != lasttargets[j+1][i]:
                condition = False

        global switch

        if condition == True:
            brackets.append([target])
        elif switch == True: 
            brackets.append([target - step, target])
        else:
            brackets.append([target, target + step])

    """if switch == True:
        switch = False
    else:
        switch = True"""
            
    for j in range(len(targets)-7):
        i = j+7
        brackets.append([targets[i]])


    global breakchecker
    for i in brackets:
        if len(i) == 1 and breakchecker == True:
            breakchecker = True
        else:
            breakchecker = False
    for a in brackets[0]:
        for b in brackets[1]:
            for c in brackets[2]:
                for d in brackets[3]:
                    for e in brackets[4]:
                        for f in brackets[5]:
                            for g in brackets[6]:
                                for h in brackets[7]:
                                    for i in brackets[8]:
                                        for j in brackets[9]:
                                            for k in brackets[10]:
                                                for l in brackets[11]:
                                                    for m in brackets[12]:
                                                        output.append([a,b,c,d,e,f,g,h,i,j,k,l,m])
    return output
                 
                 

#Running area:


print(teststeps)

for step in teststeps:
    print(str(round(100*stepnum/len(teststeps),2)) + "%")
    stepnum += 1
    buffercost = [0.2776591666666667, 0.2806591666666667, 0.26565916666666667, 0.21827666666666665, 0.519595, 0.7359366666666667]
    imstockcost = 0.003 #3 dollars per kg, weight is given in grams
    fltstockcost = 17.88/90 #17.88 for a 10 pack of 12x12 sheets
    options = setupcombinations(targets,lasttargets,step)
    numcycles = len(options)

    
    for a,b,c,d,e,f,g,h,u,o,k,l,m in options:       

        means = []
        for z in range(simulationCycles):
            numMac = [a,b,c,d,e,f] #Set quantities for each machine [0, 1, 2, 3, 4, 5]
            numWork = g
            bufferMax = [h,u,o,k,l,m]#[h,i,j,k,l,m,n] #Set max buffer sizes for each machine (Output buffers)
            buffers = [0,0,0,0,0,0] 
            lastbuffer = buffers 
            bufferlog = []
            imsupply = 0
            fltsupply = 0
            supplylog = []
            totalcost = 0
            products = 0
            
            #(numMac)
            #(bufferMax)

            factory = []
            for mach in range(len(numMac)):
                for this in range(numMac[mach]):
                    factory.append(Machine((str(mach) + "." + str(this)), mach))
            
            for mach in factory:
                totalcost += mach.cost

            staff = []
            for mach in range(numWork):
                staff.append(Worker(str(6) + "." + str(mach),workertype))
            
            #singlemachinetest(factory)
            #machinearraytest(factory)
            #singleworkertest(staff)
            #workerarraytest(staff)

            #Factory simulation
            for i in range(duration):
                #Supply first stage machines
                lastbuffer = buffers.copy()
                
                for j in [0,1,2,3]:
                    imsupply,fltsupply = runsupply(j,imsupply,fltsupply,factory)

                #Load later stage machines if available
                for j in [4,5]:
                    buffers[j-1] = loadmachines(j,buffers[j-1],factory)

                #Run one cycle of machines
                for j in range(6):
                    buffers[j] = runmachines(j,buffers[j], bufferMax[j], factory)

                #Load Workers
                [buffers[0], buffers[1], buffers[2], buffers[5]] = loadworkers(staff,[buffers[0], buffers[1], buffers[2], buffers[5]])

                #Run Worker Cycles
                products += runworkers(staff)

                #Calculate cost of buffers
                for j in range(len(buffercost)):
                    totalcost += buffercost[j]*buffers[j]

                #Run Supply Log if imsupply has changed and Buffer Log if Buffers have changed
                if imsupply != 0:
                    
                    supplylog.append([i,-imsupply])
                if not (buffers == lastbuffer):
                    bufferlog.append([i,buffers.copy()])

                
                totalcost += -imsupply * imstockcost
                
                totalcost += -fltsupply * fltstockcost

                imsupply = 0
                fltsupply = 0
            means.append([products,totalcost])

        means = means[0:int(simulationCycles*percentileGoal)]

        means.sort()

        products = [means[i][0] for i in range(len(means))]
        costs = [means[i][1] for i in range(len(means))]
        meanProducts = numpy.sum(products)//len(products)
        meanCost = round(numpy.sum(costs)/len(products),2)


        if meanProducts >= productiongoal:
            package = []
            package.extend(numMac)
            package.extend([numWork])
            package.extend(bufferMax)
            
            viable.append([round(meanCost,2),products,package])

    viable.sort()

    supplyfile = open(outputpath + "supplylogs" +  name[-5:-3]  + '.txt', 'w')
    bufferfile = open(outputpath + "bufferlogs" +  name[-5:-3]  + '.txt', 'w')
    viableoptions = open(outputpath + "viableoptionslogs" +  name[-5:-3]  + '.txt', 'w')
    bufferfile.write(name)
    supplyfile.write(name)
    viableoptions.write(name)

    for i in bufferlog:
        bufferfile.write(str(i) + "\n")

    for i in supplylog:
        supplyfile.write(str(i) + "\n")

    for i in viable:
        viableoptions.write(str(i) + "\n")

    bufferfile.close()
    supplyfile.close()
    viableoptions.close()
    
    if viable == []:
        optimal = "No optimal found"
    else:
        for i in range((len(lasttargets)-1),0,-1):
            lasttargets[i] = lasttargets[i-1]   
        lasttargets[0] = targets
        optimal = viable[0]
        targets = viable[0][-1]

    if breakchecker:
        print("\nBreak\nBreak\n")
        break

et = time.time()

key = name[-5:-3]
key += "break" + str(et-st)
key += "break" + str(optimal[0])
key += "break" + str(optimal[1])
key += "break" + str(optimal[2])
key += "break" + str(hoursoperational)
key += "break" + str(workertype)

print(key)
keynote = open(outputpath + "keydata" +  name[-5:-3]  + '.txt', 'w')
keynote.write(key)
keynote.close()
