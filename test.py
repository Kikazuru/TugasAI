import itertools
x = [i for i in range(1, 6)]
print(list(itertools.combinations(x,2)))

temp = []
for i in range(1,6):
    for j in range(i + 1, 6):
        temp.append((i,j))
print(temp)