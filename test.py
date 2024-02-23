import re
fileName = r"C:\Users\Ericw\Desktop\TopScience.gc"
#def GcodeConverter(fileName):

x = []
y = []
counter = 0
with open(fileName, "r", encoding='utf-8-sig') as f:
    lines = f.read()
    lines2 = lines.splitlines()

    for line in lines2:
        match = re.search(r"G1 X(\S*) Y(\S*)|G1 X(\S*)|G1  Y(\S*)", line)

        if match != None:  # if we find a match
            result = match.groups()

            if result[0] != None:
                x_temp = result[0]
                y_temp = (result[1])

                x.append(float(x_temp))
                y.append(float(y_temp))
            elif result[2] != None:
                x_temp = result[2]
                y_temp = y[len(y)-1] # get last input

                x.append(float(x_temp))
                y.append(float(y_temp))

            elif result[3] != None:
                y_temp = result[3]
                x_temp = x[len(x) - 1]  # get last input

                x.append(float(x_temp))
                y.append(float(x_temp))



            print(x_temp)
            #print(y_temp)
            # print(counter)
            # counter = counter+12

#print(*zip(x,y))



    #return x, y

#print(GcodeConverter(r"C:\Users\Ericw\Desktop\TopScience2.txt"))