import numpy as np

P = np.array([[4,1,2],[9,1,3],[2,7,1]])
np.savetxt('test.txt', (P), fmt='%i')
M = np.loadtxt('test.txt', unpack=True)
print(M)