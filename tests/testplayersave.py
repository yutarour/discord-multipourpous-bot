import json as js

name = input("Player name: ")
points = int(input("Points: "))

name1 = input("Player name: ")
points1 = int(input("Points: "))

data = {}

data[name] = []
data[name].append({
    'points':points
})

data[name1] = []
data[name1].append({
    'points':points1
})



with open('mydata.json', 'w') as f:
    js.dump(data, f)
    f.close()

f = open('mydata.json')
team = js.load(f)

#print(team[name])
print(team)
print(team[name][0]['points'])


# when finished, close the file
f.close()

