import matplotlib.pyplot as plt
import numpy as np
import math
import random
from sklearn.decomposition import PCA




n_data = 1
target = [(0,0),(10,0),(5,10)]
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


pca = PCA(n_components=2,svd_solver="full")
pca.fit(sample)

# plot data
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(all_x,all_y,alpha = 0.8)

eigen_vector = pca.components_
eigen_value_ = pca.explained_variance_
eigen_value_ratio = pca.explained_variance_ratio_

if eigen_value_[0] < eigen_value_[1]:
   vector_min = eigen_vector[0]
   vector_max = eigen_vector[1]
   lambda_min_ratio = eigen_value_ratio[0]
   lambda_max_ratio = eigen_value_ratio[1]
else:
   vector_min = eigen_vector[1]
   vector_max = eigen_vector[0]
   lambda_min_ratio = eigen_value_ratio[1]
   lambda_max_ratio = eigen_value_ratio[0]

angle_min = math.atan2(vector_min[1],vector_min[0])
angle_max = math.atan2(vector_max[1],vector_max[0])

angle = angle_min


for length, vector in zip(pca.explained_variance_, pca.components_):
    v = vector*np.sqrt(length)

    pt1 = pca.mean_
    ax.scatter(pt1[0],pt1[1])
    pt2 = pca.mean_+v
    ax.scatter(pt2[0],pt2[1])

ax.scatter(pca.mean_[0]+math.cos(angle),pca.mean_[1]+math.sin(angle))
ax.scatter(pca.mean_[0]+math.cos(angle_min),pca.mean_[1]+math.sin(angle_min))
ax.scatter(pca.mean_[0]+math.cos(angle_max),pca.mean_[1]+math.sin(angle_max))

plt.axis('equal')
plt.grid()
fig.show()
plt.show()


