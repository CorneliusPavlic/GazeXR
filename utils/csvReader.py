import csv

def read(file): 
    with open(file) as file_ob:
        reader_obj = csv.reader(file_ob)

        result = []
        iter = 0
        for row in reader_obj:
            if iter != 0 :
                result.append(row)
            iter += 1        
        return result