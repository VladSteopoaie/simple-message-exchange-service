# used chatGPT for a quick overview of the threading API (very useful for locks and condition variables)
import threading
from queue import Queue

MAX_THREADS = 64
MAX_QUEUE_SIZE = 4096

class ThreadPool:
    def __init__(self, num_threads):
        if num_threads > MAX_THREADS:
            raise Exception(f"The maximum number of threads is {MAX_THREADS}, you introduced {num_threads}.")

        # the queue is already synchronized so I won't need locks
        self.task_queue = Queue(maxsize=MAX_QUEUE_SIZE) # the task will be tuples: (function, arguments)
        # creating the threads
        self.threads = [threading.Thread(target=self.start_thread) for _ in range(num_threads)]
        self.stop_flag = False

    def start_thread(self):
        while self.stop_flag != True:
            #     task_function, task_arguments = self.get_task()
            task_function, task_arguments = self.task_queue.get()
            # releasing the lock and executing the task
            task_function(task_arguments)


    def add_task(self, task):
        self.task_queue.put(task)

    def start(self):
        for thread in self.threads:
            thread.start()
    
    def join(self):
        self.stop_flag = True
        for thread in self.threads:
            thread.join()
