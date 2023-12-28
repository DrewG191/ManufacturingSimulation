import os;
batchno = 24 #Set which Batch Number the files will output to
numfiles = 12 #Set how many files to generate


#Set file names and output paths
name = os.path.basename(__file__)
path = __file__[:-len(name)]
f = open(path + "SimulationV0M.py", 'r')
file = f.read()
f.close()
file = file.replace("batchno = 99", ("batchno = " + str(batchno)))
outputpath = path + "Batch" + str(batchno-1) + "/"


#Go through different files and write them with desired variations in mind
for i in range(numfiles):
    j = i+1
    ifile = file

    #Set how many hours per day the factory is operational
    if i == 0 or i == 1 or i == 6 or i == 7:
        ifile = ifile.replace("hoursoperational = 9", "hoursoperational = 8")
    elif i == 2 or i == 3 or i == 8 or i == 9:
        ifile = ifile.replace("hoursoperational = 9", "hoursoperational = 16")
    elif i == 4 or i == 5 or i == 10 or i == 11:
        ifile = ifile.replace("hoursoperational = 9", "hoursoperational = 24")

    #Set which kind of worker setup the file will have
    if (i % 2) == 0:
        ifile = ifile.replace("workertype = 2", "workertype = 0")
    else:
        ifile = ifile.replace("workertype = 2", "workertype = 1")

    #Set whether or not to include equivalent buffer costs in the simulation
    if i > 5:
        ifile = ifile.replace("includebuffer = 2", "includebuffer = 0")
    else:
        ifile = ifile.replace("includebuffer = 2", "includebuffer = 1")

    #Record previous file to last batch's folder for debugging, without overwriting any existing files
    oldpath = outputpath + "SimulationV0" +  str(j) + "Batch" + str(batchno-1) + '.py'
    if os.path.isfile(oldpath) == False:
        ReadSimulationfile = open(path + "SimulationV0" +  str(j) + '.py', 'r')
        OldSimulationFile = open(oldpath, 'w')
        
        old = ReadSimulationfile.read()
        OldSimulationFile.write(old)

        OldSimulationFile.close()  
        ReadSimulationfile.close()
        print("OldFileSaved")
    else:
        print("Old File Detected, No Overwrite Saved")

    #Accessing previous keydata from previous file to set targets for new file, or if no file exists it checks the matching file from the first 6 iterations
    keypath = outputpath + "keydata0" + str(j) + ".txt"
    if os.path.isfile(keypath) == True:
        OldKey = open(keypath, 'r')
        key = OldKey.read()
        OldKey.close()
        formattedkey = key.split("break")
        ifile = ifile.replace("targets = [20, 10, 10, 30, 10, 10, 100, 9999, 9999, 9999, 9999, 9999, 9999]", "targets = " + formattedkey[4])
    else:
        keypath = outputpath + "keydata0" + str(j-6) + ".txt"
        OldKey = open(keypath, 'r')
        key = OldKey.read()
        OldKey.close()
        formattedkey = key.split("break")
        ifile = ifile.replace("targets = [20, 10, 10, 30, 10, 10, 100, 9999, 9999, 9999, 9999, 9999, 9999]", "targets = " + formattedkey[4])

    Simulationfile = open(path + "SimulationV0" +  str(j) + '.py', 'w')
    Simulationfile.write(ifile)
    Simulationfile.close()



print("Files completed")