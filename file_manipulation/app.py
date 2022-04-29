# generates 1.txt file with number column ranging (1, 20)]
one = open("1.txt", "w")
one.write('\n'.join(str(i) for i in range(1, 20 + 1)))
one.close()

# generates 2.txt file with number column ranging (-20, -1)
two = open("2.txt", "w")
two.write('\n'.join(str(i) for i in range(-20, -1 + 1)))
two.close()

# merge 1.txt and 2.txt into 1+2.txt
one = open("1.txt", "r")
two = open("2.txt", "r")

one_two = open("1+2.txt", "w")
one_two.write(two.read() + "\n" + one.read())

one_two.close()
one.close()
two.close()

#########################################################################




#########################################################################




#########################################################################
