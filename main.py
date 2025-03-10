import pandas as pd
from anom_detection.cluster.dbscan import SeqDBSCAN
from capturing import capture
from processing.processing_thread import ProcessingPool
from queue import Queue
from anom_detection.data_structs.procdata_queue import ProcDataQueue
import time
from threading import Thread
import threading

if __name__ == "__main__":
    capture_queue = Queue()
    captureflag = threading.Event()
    def stop_flag():
        return captureflag.is_set()
    capture_thread = Thread(target=capture.capture_packets, args=(capture_queue,"Wi-Fi",captureflag,))
    capture_thread.start()

    time.sleep(5)
    print("Done capturing")
    captureflag.set()
    capture_thread.join()

    print(list(capture_queue.queue))

    print("Initializing processing data queue")

    procdataqueue = ProcDataQueue()

    print("Initializing DBSCAN")

    seq_dbscan = SeqDBSCAN(eps=0.5, min_samples=5)

    print("Initializing processing pool")

    pool_thread = ProcessingPool(seq_dbscan, capture_queue, procdataqueue, 2)
    print("Processing")
    time.sleep(5)
    print("Done processing")
    pool_thread.kill()

    points = []

    while procdataqueue.qsize() > 0:
        points.append(procdataqueue.get())

    print("Points: ", points)

    
    # Tune eps and min_samples based on your data characteristics
    seq_dbscan.process_data(points)
    seq_dbscan.plot_clusters()
    anoms = seq_dbscan.get_anomalies()
    print(anoms)
    print("Number of anomalies:", len(anoms))


