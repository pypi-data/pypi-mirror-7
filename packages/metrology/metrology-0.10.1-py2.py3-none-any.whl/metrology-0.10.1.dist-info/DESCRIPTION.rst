Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: =========
        Metrology
        =========
        
        A library to easily measure what's going on in your python.
        
        Metrology allows you to add instruments to your python code and hook them to external reporting tools like Graphite so as to better understand what's going on in your running python program.
        
        Installing
        ==========
        
        To install : ::
        
            pip install metrology
        
        API
        ===
        
        Gauge
        -----
        
        A gauge is an instantaneous measurement of a value
        
        .. code-block:: python
        
            class JobGauge(metrology.instruments.Gauge):
                def value(self):
                    return len(queue)
            gauge = Metrology.gauge('pending-jobs', JobGauge())
        
        
        Counters
        --------
        
        A counter is like a gauge, but you can increment or decrement its value
        
        .. code-block:: python
        
            counter = Metrology.counter('pending-jobs')
            counter.increment()
            counter.decrement()
            counter.count
        
        Meters
        ------
        
        A meter measures the rate of events over time (e.g., "requests per second").
        In addition to the mean rate, you can also track 1, 5 and 15 minutes moving averages
        
        .. code-block:: python
        
            meter = Metrology.meter('requests')
            meter.mark()
            meter.count
        
        Timers
        ------
        
        A timer measures both the rate that a particular piece of code is called and the distribution of its duration
        
        .. code-block:: python
        
            timer = Metrology.timer('responses')
            with timer:
                do_something()
        
        
        Utilization Timer
        -----------------
        
        A specialized timer that calculates the percentage of wall-clock time that was spent
        
        .. code-block:: python
        
            utimer = Metrology.utilization_timer('responses')
            with utimer:
              do_something()
        
        Reporters
        =========
        
        Logger Reporter
        ---------------
        
        A logging reporter that write metrics to a logger
        
        .. code-block:: python
        
            reporter = LoggerReporter(level=logging.INFO, interval=10)
            reporter.start()
        
        
        Graphite Reporter
        -----------------
        
        A graphite reporter that send metrics to graphite
        
        .. code-block:: python
        
            reporter = GraphiteReporter('graphite.local', 2003)
            reporter.start()
        
        
        Librato Reporter
        ----------------
        
        A librator metric reporter that send metrics to librato API
        
        .. code-block:: python
        
            reporter = LibratoReporter("<email>", "<token>")
            reporter.start()
        
        
        Ganglia Reporter
        ----------------
        
        A ganglia reporter that sends metrics to gmond.
        
        .. code-block:: python
        
            reporter = GangliaReporter("Group Name", "localhost", 8649, "udp", interval=60)
            reporter.start()
        
        
        Acknowledgement
        ===============
        
        This is heavily inspired by the awesome `metrics <https://github.com/codahale/metrics>`_ library.
        
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 3
Classifier: Topic :: Utilities
