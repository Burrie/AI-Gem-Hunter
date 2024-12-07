from pysat.formula import CNF
from pysat.solvers import Solver
import csv
import time #To check time complexity

start = time.time()

height = 0
width = 0

#2D-character array
map = []

#All of CNF clauses generated
CNFs = CNF()

test_file_size = '6x6'
inputFile = "testcases/input" + test_file_size + ".csv"
outputFile = "testcases/output" + test_file_size + ".csv"

#----------------------------------------------------------------------------------

#void funtion
def input(filepath: str):
    global height
    global width
    global map

    #Used to mark logical variable - Gem or Trap
    #Start from 10 because a cell just 8 cells surrond -> maximum number can be used to indicate traps around is 8
    mark = 10
    
    #Read csv file and generate map
    with open(filepath, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            height += 1
            width = len(row)
            tmp_list = row # character list
            for i in range(0, len(tmp_list)):
                if(tmp_list[i] == '_'):
                    tmp_list[i] = str(mark)
                    mark += 1
            map.append(tmp_list)


#return 2D-int array: Positions of elements in mark_array
def get_position_to_generate_DNF(start: int, num_trap: int, len_mark_array: int):
    position_mark_array = []

    for i in range(start, len_mark_array):
        if(num_trap > 1):
            if(i + num_trap > len_mark_array): #Still need atom but run out of element in the mark_array
                break
            
            tmp_position_array = get_position_to_generate_DNF(start= i + 1, num_trap= num_trap - 1, len_mark_array= len_mark_array)
            
            #Everything is ok -> Position array to 2D-array
            for array in tmp_position_array:
                array.append(i)
                position_mark_array.append(array)        
        else:
            tmp_position_array = [i]
            position_mark_array.append(tmp_position_array)
    
    return position_mark_array


#return 2D-int array: Each array in DNF_array is a clause in DNF form (Disjunctive Normal Form) - literals in a clause are connected via Conjunction
def generate_DNF(mark_array: list, num_trap_on_map: int):
    #2D-int array of positions in mark_array to convert array's elements into DNF form -> then CNF 
    position_mark_array = []
    DNF_array = []

    position_mark_array = get_position_to_generate_DNF(start= 0, num_trap= num_trap_on_map, len_mark_array= len(mark_array))

    #Get all clauses in DNF form (Disjunctive Normal Form)
    for i in range(0, len(position_mark_array)):
        clause = []
        for j in range(0, len(mark_array)):
            clause.append(-mark_array[j])
        for j in position_mark_array[i]: #position_mark_array is a 2D-int array contains positions of elements in mark_array
            clause[j] = -clause[j]
        DNF_array.append(clause) #DNF_array now contains clauses in DNF form (Disjunctive Normal Form) - literals in a clause are connected via Conjunction
     
    return DNF_array
        

#return 2D-int array: Each array in CNF_array is a clause in CNF form (Conjunctive Normal Form) - literals in a clause are connected via Disjunction
def convert_DNF_to_CNF(current_DNF_clause: int, DNF_array: list):
    CNF_array = []
  
    if current_DNF_clause < len(DNF_array) - 1:
        for literal in DNF_array[current_DNF_clause]:
            CNF_clauses = convert_DNF_to_CNF(current_DNF_clause= current_DNF_clause+ 1, DNF_array= DNF_array)
            for clause in CNF_clauses:
                if(clause.__contains__(-literal)): #Literal Or negation of it -> Give 1 -> 1 Or 1/0 -> Give 1
                    continue #Because of CNF, we can ignore the clause always gives 1
                if (clause.__contains__(literal) == False): #Just add the literal to the clause only when it doesn't appear in the clause.
                    clause.append(literal)
                CNF_array.append(clause)
    else:
        for literal in DNF_array[current_DNF_clause]:
            clause = [literal]
            CNF_array.append(clause) #2D array
            
    return CNF_array

#void function: Generate CNF clauses and add to global variable CNFs
def generate_cnf(mark_array: list, num_trap_on_map: int):
    global CNFs
    if num_trap_on_map == 0: #No trap surronds -> All variables are False
        for variable in mark_array:
            if(CNFs.clauses.__contains__([-variable]) == False): #Check if the sorted clause appeared before
                CNFs.append([-variable])
        return
    
    if num_trap_on_map == len(mark_array): #Number of traps == number of variables surrounding -> All variables are True
        for variable in mark_array:
            if(CNFs.clauses.__contains__([variable]) == False): #Check if the sorted clause appeared before
                CNFs.append([variable])
        return

    DNF = generate_DNF(mark_array= mark_array, num_trap_on_map= num_trap_on_map)
    if(len(DNF) == 0):
        return
    CNF = convert_DNF_to_CNF(DNF_array= DNF, current_DNF_clause= 0)
    for clause in CNF:
        clause.sort() #Clause is a list of integer -> Sorting facilitates checking afterwards
        if(CNFs.clauses.__contains__(clause) == False): #Check if the sorted clause appeared before
            CNFs.append(clause)
    
    
#void function: Look at cells surround the cell with a number in it to generate CNF clauses      
def look_around(h : int, w : int):
    global height
    global width
    global map

    #Cells surround the cell with a number in it
    mark_array = []

    for y in range(-1, 2):
        if y + h < 0 or y + h >= height:
            continue
        for x in range(-1, 2):
            if x + w < 0 or x + w >= width:
                continue
            #Found cells with marks (logical variables)
            if int(map[y + h][x + w]) >= 10:
                mark_array.append( int(map[y + h][x + w]) )
                
    #Number of variables around is less than number of traps surround -> Error
    if len(mark_array) < int(map[h][w]):
        return
    
    generate_cnf(mark_array= mark_array, num_trap_on_map= int(map[h][w]))
    
    
#void function
def read_map():
    global height
    global width
    global map

    for h in range(0, height):
        for w in range(0, width):
            if int(map[h][w]) < 10: #Found cell with number indicating number of traps surround
                look_around(h= h, w= w)

#Boolean, list function: Check satisfiabilty of formula + Find value for each logical variable if the formula is satisfiable
def infer_result_from_CNFs():
    global CNFs

    s = Solver(bootstrap_with= CNFs)
    isSatisfiable = s.solve()
    values = s.get_model()
    s.delete()

    if(isSatisfiable == True): #If the formula is satisfiable -> Ignore first 9 variables, because the program started from 10
        values = values[9:]
    return isSatisfiable, values

#Write Output to file
def output(filename: str, variables_values: list):
    global height
    global width
    global map

    count = 0
    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        for h in range(0, height):
            for w in range(0, width):
                if( int(map[h][w]) >= 10): #Cell is a logical varible with mark
                    if(variables_values[count] > 0): #Trap
                        map[h][w] = 'T'
                    else: #Gem
                        map[h][w] = 'G'
                    count += 1 #Because variables_values is a sorted array
        csv_writer.writerows(map)
                
#------------------------------------------------------------------------------------------------------------

input(inputFile)

read_map()

isSatisfiable, variables_values = infer_result_from_CNFs()

output(filename= outputFile, variables_values= variables_values)

end = time.time()

print('Time consumed: ' + str(end - start) + ' (Seconds)')