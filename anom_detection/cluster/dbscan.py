import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

class SeqDBSCAN:
    def __init__(self, eps=0.5, min_samples=2):
        self.eps = eps
        self.min_samples = min_samples
        self.points = []
        self.labels = {}
        self.clusters = {}
        self.next_cid = 0
        
    def region_query(self, p):
        neighbors = []
        p_arr = np.array(p, dtype=float)
        for point in self.points:
            point_arr = np.array(point, dtype=float)
            if np.linalg.norm(p_arr - point_arr) <= self.eps:
                neighbors.append(point)
        return neighbors

    
    def update_clustering(self, p):

        p_tuple = tuple(p)
        neighbors = self.region_query(p_tuple)
        if p_tuple not in neighbors:
            neighbors.append(p_tuple)
        

        if len(neighbors) >= self.min_samples:
            neighbor_labels = set()
            for n in neighbors:
                if n in self.labels and self.labels[n] is not None and self.labels[n] != -1:
                    neighbor_labels.add(self.labels[n])
                    
            if neighbor_labels:
                assigned_cluster = min(neighbor_labels)
                self.labels[p_tuple] = assigned_cluster
                self.clusters[assigned_cluster].add(p_tuple)
                for other_label in neighbor_labels:
                    if other_label != assigned_cluster:
                        for point in self.clusters[other_label]:
                            self.labels[point] = assigned_cluster
                        self.clusters[assigned_cluster].update(self.clusters[other_label])
                        del self.clusters[other_label]
            else:
                new_cluster_id = self.next_cid
                self.next_cid += 1
                self.labels[p_tuple] = new_cluster_id
                self.clusters[new_cluster_id] = {p_tuple}
            
            current_cluster = self.labels[p_tuple]
            for n in neighbors:
                if n not in self.labels or self.labels[n] == -1:
                    self.labels[n] = current_cluster
                    self.clusters[current_cluster].add(n)
        else:
            assigned = False
            for n in neighbors:
                if n in self.labels and self.labels[n] is not None and self.labels[n] != -1:
                    self.labels[p_tuple] = self.labels[n]
                    self.clusters[self.labels[n]].add(p_tuple)
                    assigned = True
                    break
            if not assigned:
                self.labels[p_tuple] = -1

        self.points.append(p_tuple)
        
    def process_data(self, data):
        for p in data:
            self.update_clustering(p)
            
    def get_clusters(self):
        return [list(points) for cid, points in self.clusters.items()]
    
    def get_anomalies(self):
        anomalies = []
        for point, label in self.labels.items():
            if label == -1:
                neighbors = self.region_query(point)
                anomalies.append({
                    "point": point,
                    "neighbor_count": len(neighbors)
                })
        return anomalies

    def plot_clusters(self):
        points = []
        labels = []
        noise = []
        for point, label in self.labels.items():
            if label == -1:
                noise.append(point)
            else:
                points.append(point)
                labels.append(label)
        if len(points) == 0 and len(noise) == 0:
            print("No points to plot!")
            return
        
        if points:
            X = np.array(points, dtype=float)
        else:
            X = np.empty((0, len(self.all_points[0])))
            
        if X.shape[1] != 2:
            pca = PCA(n_components=2)
            X_reduced = pca.fit_transform(X)
        else:
            X_reduced = X

        plt.figure()
        plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=labels, cmap='viridis', marker='o', label="Clustered")
        
        if noise:
            noise_arr = np.array(noise, dtype=float)
            if noise_arr.shape[1] != 2:
                noise_reduced = pca.transform(noise_arr)
            else:
                noise_reduced = noise_arr
            plt.scatter(noise_reduced[:, 0], noise_reduced[:, 1], c='red', marker='x', label="Noise")
        
        plt.title("Sequential DBSCAN Clusters (PCA-reduced)")
        plt.xlabel("Component 1")
        plt.ylabel("Component 2")
        plt.legend()
        plt.show()

