from threading import Thread, Event
from queue import Queue
from anom_detection.preprocessing.feature_extraction import extract_features
from anom_detection.preprocessing.data_preprocess import preprocess_packet_features
from anom_detection.data_structs.procdata_queue import ProcDataQueue

class ProcessingPool:

    def __init__(self, dbscan, inputqueue: Queue, outputqueue: ProcDataQueue, num_threads=0):
        self.num_threads = num_threads
        self.workers: list[WorkerThread] = []
        self.idx = 0

        self.inputqueue = inputqueue
        self.outputqueue = outputqueue
        
        self.prep_workers()

        self.flagbool = Event()

        self.feeder_thread = Thread(target=self.feed_data)
        self.feeder_thread.start()


    def prep_workers(self):
        for x in range(self.num_threads):
            flagbool = Event()
            thread = WorkerThread(inputqueue = self.inputqueue, outputqueue=self.outputqueue, thread_id=x, flagbool=flagbool)
            self.workers.append([thread, flagbool])

    def feed_data(self):
        while self.flagbool.is_set() is False:
            try:
                if self.inputqueue.empty() is False:
                    if self.workers[self.idx][0].get_working_flag() == True:
                        self.idx += 1
                        if self.idx == self.num_threads:
                            self.idx = 0
                    else:
                        self.workers[self.idx][0].set_enqueue_perms()

            except:
                self.idx = 0
                continue

    def kill(self):
        for x in self.workers:
            x[1].set()
            x[0].stop()

        self.flagbool.set()
        self.feeder_thread.join()
        

class WorkerThread:

    def __init__(self, inputqueue: Queue, outputqueue: ProcDataQueue, flagbool: Event, thread_id: int=-1,):
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue
        self.thread_id = thread_id
        self.working_flag = False
        self.flagbool = flagbool
        self.thread = Thread(target=self.run)
        self.thread.start()

    def get_working_flag(self):
        return self.working_flag
    
    def set_enqueue_perms(self):
        self.working_flag = True

    def stop(self):
        self.flagbool.set()
        if self.outputqueue.current_working() == self.thread_id:
            self.outputqueue.release()
        self.working_flag = False
        self.thread.join()

    def run(self):
        while self.flagbool.is_set() is False:
            try:
                if self.working_flag == True and self.inputqueue.empty() is False:
                    data = self.inputqueue.get()
                    feature_data = extract_features(data)
                    preprocessed_data = preprocess_packet_features(feature_data)


                    while self.outputqueue.is_working() == True:
                        perms = self.outputqueue.ask_perms(self.thread_id)
                        if perms == True:
                            break
                    self.outputqueue.put(preprocessed_data)
                    self.outputqueue.release()
                    self.working_flag = False

            except:
                if self.outputqueue.current_working() == self.thread_id:
                    self.outputqueue.release()
                self.working_flag = False
                continue