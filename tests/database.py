import pickle

L=[1,2,3,4,5]

with open('testdb', 'wb') as F:
    # Dump the list to file
    pickle.dump(L, F)
    print("data pickled")

with open ('testdb', 'rb') as F:
    L1 = pickle.load(F)

print(L1)