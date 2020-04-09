import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.decomposition import PCA




n_data = 1
target = [(0,0),(0,10),(4,10)]
#target = [(4,3)]
sample = []
all_x  =[]
all_y = []
for coord in target:
    for n in range(n_data):
        x = coord[0] + np.random.random_sample()*0.1
        y = coord[1] + np.random.random_sample()*0.1
        all_x.append(x)
        all_y.append(y)
        sample.append([x,y])


pca = PCA(n_components=2)
pca.fit(sample)


# plot data
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(all_x,all_y,alpha = 0.2)
for length, vector in zip(pca.explained_variance_, pca.components_):
    v = vector*np.sqrt(length)

    pt1 = pca.mean_
    ax.scatter(pt1[0],pt1[1])
    pt2 = pca.mean_+v
    ax.scatter(pt2[0],pt2[1])

plt.axis('equal')
plt.grid()
fig.show()
plt.show()


