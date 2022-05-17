import sys

# generates 1.txt file with number column ranging (1, 20)]
with open("1.txt", "w") as one:
    one.write('\n'.join(str(i) for i in range(1, 20 + 1)))

# generates 2.txt file with number column ranging (-20, -1)
with open("2.txt", "w") as two:
    two.write('\n'.join(str(i) for i in range(-20, -1 + 1)))

# merge 1.txt and 2.txt into 1+2.txt
with open("1.txt", "r") as one:
    one_content = one.read()
    one_content = one_content.split()

with open("2.txt", "r") as two: 
    two_content = two.read()
    two_content = two_content.split()

with open("1+2.txt", "w") as one_two:
    merge = [str(two_content[i] + " " + one_content[i]) for i in range(20)]

    one_two.write('\n'.join(merge))


#########################################################################

# gets size in bytes of the content until value
def bytes_until(value):
    cont = 0
    value_occ = 0

    for i in merge:
        cont += 1

        if(i == value):
            print("Tamanho ateh o valor: " + str(sys.getsizeof(merge[0:cont])))
            value_occ = cont
        else:
            print(i)
    
    print("Tamanho depois do valor: " + str(sys.getsizeof(merge[value_occ:-1])))

bytes_until("-15 6")

#########################################################################

