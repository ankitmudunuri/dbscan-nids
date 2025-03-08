import numpy as np
import matplotlib.pyplot as plt

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
        for point in self.points:
            if np.linalg.norm(np.array(p) - np.array(point)) <= self.eps:
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
    
    def plot_clusters(self):
        cluster_points = []
        cluster_labels = []
        noise_points = []
        
        for point, label in self.labels.items():
            if label == -1:
                noise_points.append(point)
            else:
                cluster_points.append(point)
                cluster_labels.append(label)
                
        if len(cluster_points) == 0 and len(noise_points) == 0:
            print("No points!")
            return
        
        if cluster_points:
            cluster_points_arr = np.array(cluster_points, dtype=float)
            # Temporarily just so I could test 2D dummy data
            if cluster_points_arr.ndim != 2 or cluster_points_arr.shape[1] != 2:
                print("Invalid Data format")
                return
        else:
            cluster_points_arr = np.empty((0, 2))
        
        plt.figure()
        if cluster_points:
            plt.scatter(cluster_points_arr[:, 0], cluster_points_arr[:, 1],
                        c=cluster_labels, cmap='viridis', marker='o', label="Clustered Points")
        if noise_points:
            noise_arr = np.array(noise_points, dtype=float)
            if noise_arr.ndim == 2 and noise_arr.shape[1] == 2:
                plt.scatter(noise_arr[:, 0], noise_arr[:, 1],
                            c='red', marker='x', label="Anomaly")
        plt.title("Network Traffic Anomaly Detection Clusters")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.show()

