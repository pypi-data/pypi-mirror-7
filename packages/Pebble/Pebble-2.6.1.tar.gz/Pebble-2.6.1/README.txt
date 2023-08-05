Pebble
======


Description
-----------

Pebble provides a neat API to manage threads and processes within an application.


  .. note::

     Since Pebble 2.5 it is possible to decorate instance methods.


Examples
--------

Launch a task in a thread and wait for its results::

    from pebble import thread


    @thread
    def do_job(foo, bar=0):
    	return foo + bar


    if __name__ == "__main__":
        task = do_job(1, bar=2)
	print task.get()

Launch five tasks in separate processes and handle their results in a callback::

    from pebble import process


    def task_done(task):
    	print "Task %s returned %d" % (task.id,
                                       task.get())


    @process(callback=task_done)
    def do_job(foo, bar=0):
    	return foo + bar


    if __name__ == "__main__":
        for i in range(0, 5):
            do_job(i)

	raw_input("Press return to exit.")

Callbacks can be dynamically (re)assigned, useful to set instance methods as callback::

    import time
    from pebble import process


    class Foo(object):
	def __init__(self):
	    self.counter = 0
	    self.errors = 0
	    self.do_job.callback = self.task_done

	def task_done(self, task):
            try:
                self.counter += task.get()
            except:  # exception are raised by get()
                self.errors += 1

	@process
	def do_job(self):
	    return 1

	@process
	def do_wrong_job(self):
	    raise Exception("Ops!")


    if __name__ == "__main__":
	foo = Foo()
	tasks = []

	for i in range(0, 5):
	    task = foo.do_job()
	    tasks.append(task)
	    task = foo.do_wrong_job()
	    tasks.append(task)

        time.sleep(1)

	print foo.counter
	print foo.errors

Pools allow to execute several tasks without the need of spawning a new worker for each task::

    from threading import current_thread
    from pebble import ThreadPool


    def task_done(task):
        results, thread_id = task.get()
    	print "Task %s returned %d from thread %s" % (task.id,
                                                      results,
                                                      thread_id)


    def do_job(foo, bar=0):
    	return foo + bar, current_thread().ident


    if __name__ == "__main__":
        with ThreadPool(workers=5) as tp:
            for i in range(0, 10):
                tp.schedule(do_job, args=(i, ), callback=task_done)
