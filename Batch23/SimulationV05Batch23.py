#2.853 Final Project - Drew, Irma
import os;
import random;
import time;
import numpy;
import math;
st = time.time()

#Stages of production: 
# Inner Core   - 0:Injection molder ------------------------------------>6: Assembly
# Outer Core   - 1:Injection molder -------------------------------------^
# Spinner Base - 2: Injection molder -------------------------------------^
# Spinner Face - 3:Plastic Printer -> 4:Thermoformer -> 5:Die Puncher ^

optimizationCycles = 10
simulationCycles = 20
percentileGoal = 0.95
hoursoperational = 16 #How many hours per day is it operational?
workertype = 0 #What type of worker assembly process is in use?
targets = [12, 8, 8, 22, 1, 33, 148, 9999, 9999, 9999, 9999, 9999, 9999] #Machine Quantities, Worker Quantity, and Max Buffer Sizes
#[0, 1, 2, 3, 4, 5, 6, Buffer 0, Buffer 1, Buffer 2, Buffer 3, Buffer 4, Buffer 5]
samples = range(1,10,2)
includebuffer = 1

totalcost = 0
laborcost = 0 
machinecost = 0
operationalcost = 0
stockcost = 0
overbuffercost = 0
name = os.path.basename(__file__)
path = __file__[:-len(name)]
batchno = 23
outputpath = path + "Batch" + str(batchno) + "/"
duration = hoursoperational*60 #operational minutes
otherpartcost = 0.278*6 + 0.4285*2 + 0.02398*3 + 0.2912*1 + 0.0636*2 + 0.13*1
operationalDays = 1
productiongoal = int(round(1000000*(operationalDays*480/120000),0))
yearlongmultiplier = int(250/operationalDays)
viable = []
testingTargets = [True,True,True,True,True,True,True,False,False,False,False,False,False]
lasttargets=[]
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

class Machine:
    def __init__(self, name, type):
        self.name = name 
        self.type = type 
        types = [["Injection Molder - Body", (64200.00), ((.1961/60)*15.5), True, False, 3, 0.00002, 0.0667, 4, 9, True], #45 seconds to make 1 part, each part is 9g
                 ["Injection Molder - Cover", (64200.00), ((.1961/60)*15.5), True, False, 1, 0.00002, 0.0667, 2, 10, True], #30 seconds each part is 10g
                 ["Injection Molder - Spinner", (64200.00), ((.1961/60)*15.5), True, False, 1, 0.00002, 0.0667, 2, 5, True], #30 seconds each part is 10g
                 ["Printer", 24320.00, ((.1961/60)*6), True, False, 20, 0.00208333333, 0.1, 15, 1, False], #stock is 1 sheet
                 ["Thermoformer", 229999.00, ((.1961/60)*31), True, False, 1, 0.00002, 0.0667, (72*2), 1, False], #30 seconds per batch 1 sheet
                 ["Die Puncher", (3462.00), ((.1961/60)*5), True, False, 1, 0.00002, 0.0667, 3, 1, False]] #20 seconds per 1 sheet

        [self.typename, self.cost, self.usecost, self.status, self.wip, self.duration, self.failprob, self.repaprob,self.batch,self.stocky, self.moldy] = types[self.type]
        self.counter = 0
        self.progress = 0


    def __str__(self):
        letter = "Machine Name: " + str(self.name) + "\n"
        letter += " Machine Type: " + str(self.typename) + "\n"
        letter += " Machine Operational? " + str(self.status) + "\n"
        letter += " Machine Holding WIP? " + str(self.wip) + ", Machine is " + str(self.duration - self.progress) + " steps from completion\n"
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
            return [-self.batch,-self.stocky]
        else:
            return [0,0]

    def run(self, exitspace):
        if exitspace == True:
            if self.status == True and self.wip == True:
                self.progress += 1
                global operationalcost
                operationalcost += self.usecost

                if random.random() <= self.failprob:
                    self.status = False
                

            if self.status == False and random.random() <= self.repaprob:
                self.status = True

            if self.progress >= self.duration:
                self.wip = False
                self.progress = 0
                self.counter += self.batch
                return self.batch
            else:
                return 0
        else:
            return 0
        
    def moldcosting(self):
        if self.moldy == True:
            moldsused = math.ceil(self.counter/100000)
        else:
            moldsused = 0
        return moldsused
            
        
class Worker:
    def __init__(self, name, type):
        self.name = name
        global duration
        types = [[.25, True, False, 7, int(round(duration*(2/480),0)),1],
                 [.75, True, False, 18, int(round(duration*(2/480),0)),5],
                 [1.00, True, False, 2, int(round(duration*(2/480),0)),1]]
        [self.wage, self.status, self.wip, self.duration, self.rest, self.batch] = types[type]
        self.progress = 0
        self.fatigue = 0
        self.restcount = 0

    def __str__(self):
        letter = "Worker ID: " + str(self.name) + "\n"
        letter += " Worker Holding WIP? " + str(self.wip) + " for " + ", Worker is " + str(self.duration - self.progress) + " steps from completion\n"
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
            return -self.batch*2 #2 parts per yoyo
        else:
            return 0

    def run(self):
        global laborcost
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
            
            laborcost += self.wage       

            if self.wip == True:
                self.progress += 1
                

            if self.progress >= self.duration:
                self.wip = False
                self.progress = 0
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
            reci += machine.run((reci + machine.batch) < recimax)
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

    global testingTargets
    
    for i in range(len(targets)):
        target = targets[i]
        checktarget = testingTargets[i]
        condition = True
        for j in range(len(lasttargets)-1):
            if lasttargets[j][i] != lasttargets[j+1][i]:
                condition = False

        global switch

        if condition == True or checktarget == False:
            brackets.append([target])
        elif switch == True: 
            brackets.append([target - step, target])
        else:
            brackets.append([target, target + step])

    if switch == True:
        switch = False
    else:
        switch = True


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
            laborcost = 0
            machinecost = 0
            operationalcost = 0
            stockcost = 0
            overbuffercost = 0
            products = 0
            
            #(numMac)
            #(bufferMax)

            factory = []
            for mach in range(len(numMac)):
                for this in range(numMac[mach]):
                    factory.append(Machine((str(mach) + "." + str(this)), mach))
            
            for mach in factory:
                machinecost += mach.cost

            staff = []
            for mach in range(numWork):
                staff.append(Worker(str(6) + "." + str(mach),workertype))

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
                    overbuffercost += buffercost[j]*buffers[j]

                #Run Supply Log if imsupply has changed and Buffer Log if Buffers have changed
                if imsupply != 0:
                    
                    supplylog.append([i,-imsupply])
                if not (buffers == lastbuffer):
                    bufferlog.append([i,buffers.copy()])
  
                stockcost += -imsupply * imstockcost
                
                stockcost += -fltsupply * fltstockcost

                imsupply = 0
                fltsupply = 0

            stockcost += products*otherpartcost
            totalcost = machinecost + (laborcost + operationalcost + stockcost + overbuffercost*includebuffer)*yearlongmultiplier
            means.append([products,totalcost,laborcost*yearlongmultiplier,machinecost,operationalcost*yearlongmultiplier,stockcost*yearlongmultiplier,overbuffercost*yearlongmultiplier])

        means.sort()

        means = means[0:int(simulationCycles*percentileGoal)]

        products = [means[i][0] for i in range(len(means))]
        costs = [means[i][1] for i in range(len(means))]
        laborcosts = [means[i][2] for i in range(len(means))]
        machinecosts = [means[i][3] for i in range(len(means))]
        operationalcosts = [means[i][4] for i in range(len(means))]
        stockcosts = [means[i][5] for i in range(len(means))]
        overbuffercosts = [means[i][6] for i in range(len(means))]
        meanProducts = numpy.sum(products)//len(products)
        meanCost = round(numpy.sum(costs)/len(products),2)
        meanLaborCost = round(numpy.sum(laborcosts)/len(products),2)
        meanMachineCost = round(numpy.sum(machinecosts)/len(products),2)
        meanOperationalCost = round(numpy.sum(operationalcosts)/len(products),2)
        meanStockCost = round(numpy.sum(stockcosts)/len(products),2)
        meanBufferCost = round(numpy.sum(overbuffercosts)/len(products),2)
        if meanProducts >= productiongoal:
            package = []
            package.extend(numMac)
            package.extend([numWork])
            package.extend(bufferMax)

            moneyz = []
            moneyz.extend([meanLaborCost])
            moneyz.extend([meanMachineCost])
            moneyz.extend([meanOperationalCost])
            moneyz.extend([meanStockCost])
            moneyz.extend([meanBufferCost])
            
            viable.append([round(meanCost,2),products,package,moneyz])

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
        targets = viable[0][2]

    if breakchecker:
        print("\nBreak\nBreak\n")
        break

et = time.time()
key = name[-5:-3]
key += "break" + str(round(et-st,0))
key += "break" + str(optimal[0])
key += "break" + str(optimal[1])
key += "break" + str(optimal[2])
key += "break" + str(hoursoperational)
key += "break" + str(workertype)
key += "break" + str(optimal[3])

print(key)
keynote = open(outputpath + "keydata" +  name[-5:-3]  + '.txt', 'w')
keynote.write(key)
keynote.close()
