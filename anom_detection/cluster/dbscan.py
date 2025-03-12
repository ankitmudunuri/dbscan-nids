import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from sklearn.decomposition import PCA
from sklearn.neighbors import KDTree
from collections import defaultdict

class SeqDBSCAN:
    def __init__(self, eps=0.75, min_samples=3):
        self.eps = eps
        self.min_samples = min_samples
        self.points = []  
        self.labels = {}  
        self.clusters = {} 
        self.next_cid = 0
        
    def region_query(self, p):
        if len(self.points) == 0:
            return []

        tree = KDTree(np.array(self.points, dtype=float))
        p_arr = np.array(p, dtype=float).reshape(1, -1)
        indices = tree.query_radius(p_arr, r=self.eps)[0]
        neighbors = [self.points[i] for i in indices]
        return neighbors

    def update_clustering(self, p):
        p_tuple = tuple(p)
        neighbors = self.region_query(p_tuple)
        if p_tuple not in neighbors:
            neighbors.append(p_tuple)

        if len(neighbors) >= self.min_samples:
            neighbor_labels = set()
            for n in neighbors:
                if n in self.labels and self.labels[n] != -1:
                    neighbor_labels.add(self.labels[n])
            if neighbor_labels:
                assigned_cluster = min(neighbor_labels)
                self.labels[p_tuple] = assigned_cluster
                self.clusters[assigned_cluster].add(p_tuple)
                for other_label in list(neighbor_labels):
                    if other_label != assigned_cluster:
                        for pt in self.clusters[other_label]:
                            self.labels[pt] = assigned_cluster
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
                if n in self.labels and self.labels[n] != -1:
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
        return [list(pts) for cid, pts in self.clusters.items()]

    def get_anomalies(self):
        return [pt for pt, lbl in self.labels.items() if lbl == -1]

    def compute_anomaly_scores(self, k=5, threshold=2.0):
        suspicious_points = []
        for cluster_id, cluster_points in list(self.clusters.items()):
            if cluster_id < 0:
                continue
            cluster_list = list(cluster_points)
            if len(cluster_list) < 2:
                continue
            cluster_array = np.array(cluster_list, dtype=float)
            n_points = len(cluster_array)
            kth_distances = []
            for i, p in enumerate(cluster_array):
                dists = np.linalg.norm(cluster_array - p, axis=1)
                sorted_dists = np.sort(dists)
                kth_dist = sorted_dists[k] if k < n_points else sorted_dists[-1]
                kth_distances.append(kth_dist)
            cluster_kth_avg = np.mean(kth_distances)
            for i, p in enumerate(cluster_array):
                score = 0 if cluster_kth_avg == 0 else kth_distances[i] / cluster_kth_avg
                if score > threshold:
                    suspicious_points.append((tuple(p), cluster_id, score))
        return suspicious_points


    def _gather_cluster_data(self):
        clustered_pts = []
        clustered_labels = []
        noise_pts = []
        for point, label in self.labels.items():
            if label == -1:
                noise_pts.append(point)
            else:
                clustered_pts.append(point)
                clustered_labels.append(label)
        if len(clustered_pts) > 0:
            X = np.array(clustered_pts, dtype=float)
        else:
            X = np.empty((0, 2))
        pca = None
        cluster_points_2d = X
        if X.shape[0] > 0 and X.shape[1] != 2:
            pca = PCA(n_components=2)
            cluster_points_2d = pca.fit_transform(X)
        cluster_labels_arr = np.array(clustered_labels, dtype=int) if len(clustered_labels) > 0 else np.array([])
        if len(noise_pts) > 0:
            noise_arr = np.array(noise_pts, dtype=float)
            if noise_arr.shape[1] != 2:
                if pca is not None:
                    noise_2d = pca.transform(noise_arr)
                else:
                    noise_2d = noise_arr
            else:
                noise_2d = noise_arr
        else:
            noise_2d = np.empty((0, 2))
        return cluster_points_2d, cluster_labels_arr, noise_2d, pca

    def _draw_plot(self, ax, k=5, threshold=2.0, min_suspicious_points=3):
        cluster_points, cluster_labels, noise_reduced, _ = self._gather_cluster_data()

        if cluster_points.size > 0:
            ax.scatter(cluster_points[:, 0], cluster_points[:, 1],
                    c=cluster_labels, cmap='viridis', marker='o', label="Clustered")
  
        if noise_reduced.size > 0:
            ax.scatter(noise_reduced[:, 0], noise_reduced[:, 1],
                    c='red', marker='x', label="Noise")
        
        suspicious_points = self.compute_anomaly_scores(k=k, threshold=threshold)
        
        suspicious_map = defaultdict(list)
        for (pt, cid, score) in suspicious_points:
            suspicious_map[cid].append(pt)

        cluster_coords_map = {}
        for i, lbl in enumerate(cluster_labels):
            cluster_coords_map.setdefault(lbl, []).append(cluster_points[i])

        for cid, suspicious_pts in suspicious_map.items():
            if cid not in cluster_coords_map:
                continue
            if len(suspicious_pts) < min_suspicious_points:
                continue

            coords = np.array(cluster_coords_map[cid])
            x_min, y_min = coords.min(axis=0)
            x_max, y_max = coords.max(axis=0)
            rect = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                            linewidth=2, edgecolor='r', facecolor='none', linestyle='--')
            ax.add_patch(rect)
            ax.text(x_min, y_min, f"Suspicious {cid}", color='r')
        
        all_points = []
        if cluster_points.size > 0:
            all_points.append(cluster_points)
        if noise_reduced.size > 0:
            all_points.append(noise_reduced)
        if all_points:
            combined = np.vstack(all_points)
            data_min = combined.min(axis=0)
            data_max = combined.max(axis=0)
            margin = 0.1 * (data_max - data_min)
            x_min_bound, y_min_bound = data_min - margin
            x_max_bound, y_max_bound = data_max + margin
            ax.set_xlim(x_min_bound, x_max_bound)
            ax.set_ylim(y_min_bound, y_max_bound)
        else:
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
        
        ax.set_title("DBSCAN Clusters with Anomaly Bounds")
        ax.set_xlabel("Component 1")
        ax.set_ylabel("Component 2")

        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels)





    def plot_clusters(self, k=5, threshold=2.0, animated=False, interval=100):
        if not animated:
            fig, ax = plt.subplots()
            self._draw_plot(ax, k, threshold)
            plt.show()
        else:
            fig, ax = plt.subplots()
            def update(frame):
                ax.clear()
                self._draw_plot(ax, k, threshold)
            anim = FuncAnimation(fig, update, interval=interval)
            plt.show()
