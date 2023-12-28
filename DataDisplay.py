import os;
name = os.path.basename(__file__)
path = __file__[:-len(name)]
f = open(path + "filewriter.py", 'r')
filewriter = f.read()
f.close()
splitwriter = filewriter.split("\n")
batchno = int(splitwriter[1][-2:])
firstbatchno = 15
numfiles = 12
letter = ""

#Format and compile 
for k in range(numfiles):
    letter += "-----File No: " + str(k+1) + "-----\n"
    outputpath = path + "Batch" + str(firstbatchno) + "/"
    keypath = outputpath + "keydata0" + str(k+1) + ".txt"
    if os.path.isfile(keypath) == True:
        keyf = open(keypath, 'r')
        key = keyf.read()
        keyf.close()
        formattedkey = key.split("break")
        letter += "Hours worked: " + str(formattedkey[5]) + "\n"
        letter += "Worker type: " + str(formattedkey[6]) + "\n"

    letter += "\n"

    for i in range(1+(batchno-firstbatchno)):
        j = i+firstbatchno
        outputpath = path + "Batch" + str(j) + "/"
        keypath = outputpath + "keydata0" + str(k+1) + ".txt"
        if os.path.isfile(keypath) == True:
            keyf = open(keypath, 'r')
            key = keyf.read()
            keyf.close()
            formattedkey = key.split("break")
            letter += "Batch " + str(j) + " Data\n"
            letter += "Runtime: " + str(round(float(formattedkey[1]),0)) + " seconds\n"
            if formattedkey[2]  == 'N':
                letter += "<Cost Error>\n"
            else:
                letter += "Cost: $" + str(round(float(formattedkey[2]),2)) + "\n"
            letter += "Products Made: " + str((formattedkey[3])) + "\n"
            letter += "Numbers of Machines and Buffer Sizes: " +  str((formattedkey[4])) + "\n"
            if len(formattedkey) > 7:
                letter += "Labor, Machine, Operational, Stock, and Buffer Costs (Respectively): " + str((formattedkey[7])) + "\n"
            letter +="\n"

    letter += "\n\n"
            
output = open(path + "DataDisplay.txt", 'w')
output.write(letter)
output.close()
print(letter)
