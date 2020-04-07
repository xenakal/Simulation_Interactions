import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.decomposition import PCA

n_data = 2
target = [(4,3),(10,4),(0,10)]
#target = [(4,3)]
sample = []
all_x  =[]
all_y = []
for coord in target:
    for n in range(n_data):
        x = coord[0]+ np.random.random_sample()
        y = coord[1]+ np.random.random_sample()
        all_x.append(x)
        all_y.append(y)
        sample.append([x,y])

pca = PCA(n_components=2)
pca.fit(sample)
pca.fit_transform(sample)


fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(all_x,all_y)
x1 = pca.components_[0][0]
y1 = pca.components_[0][1]
x2 = pca.components_[1][0]
y2 = pca.components_[1][1]

l1 = pca.explained_variance_ratio_[0]
l2 = pca.explained_variance_ratio_[1]
print(l1)
print(l2)

X = np.array((np.mean(all_x),np.mean(all_x)))
Y = np.array((np.mean(all_y),np.mean(all_y)))
U = np.array((x1*l1,x2*l2))
V = np.array((y1*l1,y2*l2))
q = ax.quiver(X, Y, U, V,scale=0.5)

plt.grid()



fig.show()
plt.show()