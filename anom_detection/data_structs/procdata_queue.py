from queue import Queue

class ProcDataQueue(Queue):

    def __init__(self):
        super().__init__()
        self.keyflag = False
        self.curr_thread = -1

    def current_working(self):
        return self.curr_thread

    def is_working(self):
        return self.keyflag
    
    def ask_perms(self, threadid: int = -1) -> bool:
        if self.keyflag == False:
            self.keyflag = True
            self.curr_thread = threadid
            return True

        return False
    
    def release(self):
        self.keyflag = False

