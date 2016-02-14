What's this
===========

This is a demo repo to see how I would build an application that is scalable.

The final solution would involve kubernetes for deployment and consul for 
configuration, instead of docker-compose.


Work time
---------

Until now I have worked 9 hours:

 * Development of the solution 4 hours:
    * 1 hour lost with python 2 / 3 compatibility
 * Docker, environment and testing environment setup, learning docker-compose
  and testing 1.5 hours
 * Documentation 45 mins
 * Python envionment for testing, coverage, travis, etc. + tests 2 hours.


TODOs and Improvements
----------------------

As I don't know how much effort is expected from this work, I have worked to
have a MVP, although I wouldn't deploy it in production. The following things
need to be improved to be 100% production ready:

  * Separate progress update from html (now it just reloads the page)
  * Abstract the progress instead of passing strings
  * Web interface not to reload when processing has been completed
  * Deploy with nginx reverse proxy
  * Business decision for cancelled tasks, as redis with current
   implementation would get filled with cancelled tasks.
   
### WebSockets

If this wanted to be done using websockets, I would substitute redis with a
rabbitmq to allow realtime feedback from the backend to the frontend, creating
one queue to listen to events from the worker.
 
If you really really want to make it super error redundant, I would add a redis
for the workers to save the progress in it between sleep and sleep. That way a
worker could die in the middle of the process and another worker would be able
to continue where it was left, making processing not need to start again.

Having this last improvement implemented has the danger of overloading and
crashing all the workers if software bug exists. Therefore rabbitmq backend
should be configured for max retries.