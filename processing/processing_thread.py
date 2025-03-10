from threading import Thread
from queue import Queue


class ProcessingPool:

    def __init__(self, dbscan, inputqueue: Queue, outputqueue: Queue, num_threads=0):
        self.num_threads = num_threads
        self.workers = []
        self.idx = 0
        self.dbscan = dbscan

        self.inputqueue = inputqueue
        self.outputqueue = outputqueue

    def prep_workers(self):
        for x in range(self.num_threads):
            thread = WorkerThread(inputqueue = self.inputqueue, outputqueue=self.outputqueue, thread_id=x)
            self.workers.append(thread)

class WorkerThread:

    def __init__(self, inputqueue: Queue, outputqueue: Queue, thread_id: int=-1):
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue
        self.thread_id = thread_id
        self.working_flag = False
        self.thread = Thread(target=self.run)
        self.thread.start()

    def get_working_flag(self):
        return self.working_flag
    
    def set_enqueue_perms(self):
        self.working_flag = True

    def run(self):
        while True:
            try:
                if self.working_flag == True and self.inputqueue.qsize > 0:
                    data = self.inputqueue.get()

            except:
                self.working_flag = False