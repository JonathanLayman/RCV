listofthings = ['A', 'B', 'C', 'A', 'B', 'A', 'D', 'E', 'C']
votes = [3, 3, 3, 3]
names = ['a', 'b', 'c']
#
# def allSame(list):
#     return all(x == list[0] for x in list)

# f = all(x == votes[0] for x in votes)
# print(f)


class Candidate:
    def __init__(self, name):
        self.votes = 5
        self.name = name
        self.status = 'In the Running'

people = []
for name in names:
    people.append(Candidate(name))

dict = {}

dict['Choice'] = 1
for person in people:
    dict[person.name] = person.votes

for key, value in dict.items():
    print(key, value)

votes[0] = 'shflksdjflksdjfsldkj'
print(votes[0])
