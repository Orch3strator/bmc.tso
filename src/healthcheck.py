import sys
import os
import datetime
import time
import re
import glob
from optparse import OptionParser
import sqlite3
from mako.template import Template
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.font_manager import FontProperties

global DATE_TIME_FORMAT
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class HealthThreshold:
    def __init__(self, display_name, stat, gt, value):
        self.display_name = display_name
        self.stat = stat
        self.gt = gt
        self.value = value
        self.count = 0
    def exceeded_by(self, value):
        int_val = int(value)
        if self.gt:
            ret_val = (int_val > self.value)
        else:
            ret_val = (int_val < self.value)
        if ret_val:
            self.count += 1
        return ret_val

class NoticedException:
    def __init__(self, display_name, pattern):
        self.display_name = display_name
        self.pattern = re.compile(pattern)
        self.count = 0
    def check(self, line):
        if self.pattern.search(line):
            print "Noticed exception:", self.display_name
            self.count += 1

health_thresholds = (
    HealthThreshold("High thread count", "NUMBER_OF_THREADS", True, 900),
    HealthThreshold("Elections", "COUNT_OF_TOTAL_ELECTIONS", True, 0),
    HealthThreshold("Low free memory", "FREE_MEMORY", False, 100)
)

noticed_exceptions = (
    NoticedException("Out of memory (native thread)", r"unable to create new native thread"),
    NoticedException("Out of memory (PermGen)", r"OutOfMemoryError.*PermGen"),
    NoticedException("Out of memory (java heap)", r"OutOfMemoryError.*Java heap"),
    NoticedException("Port in use", "JVM_Bind"),
    NoticedException("Remedy exception", "ADAPTER_MANAGER.+Remedy exception"),
    NoticedException("Adapter health query failed", "StateQueryFailedException"),
    NoticedException("Job timeout", "concurrent.TimeoutException: The jobs with IDs"),
    NoticedException("Grid framework timeout", "gridframework.TimeoutException"),
    NoticedException("Missed heartbeat warning", "since hearing a master heartbeat"),
    NoticedException("Workflow: missing required parameter", "activityprocessor.parameter.ParameterNotFoundException")
)

parser = OptionParser(description='Process grid logs and health stats.')
parser.add_option('-t', '--tag', dest='tag', action='store',
                   help='tag name for report title and directory')
options, args = parser.parse_args()

if options.tag is None:
    print "tag is required, specify with -t or --tag"
    sys.exit(1)

BASE_DIR = "./" + options.tag + "/"
IMG_FONT = FontProperties(size=8)

grid_logs = sorted(glob.glob("grid.log*"), reverse=True)
#print grid_logs

health_pattern = re.compile(r"HEALTH_STAT")

# Open the in-memory database
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("create table stats (timestamp text, source text, stat text, value text, source_type text, timestamp_real real)")


for grid_log in grid_logs:
    print "Processing", grid_log, "..."
    with open(grid_log, "r") as fp:
        for line in fp:
            match = health_pattern.match(line)
            if match:
                fields = line.split(", ")
                # 10/01/2010 08:46:42
                timet = time.mktime(time.strptime(fields[1], DATE_TIME_FORMAT))
                stat = fields[3]
                val = fields[4]

                cur.execute("insert into stats values (?,?,?,?,?,?)",
                    (fields[1], fields[2], stat, val, fields[2][0], timet))
                # Also check thresholds
                for ht in health_thresholds:
                    if stat == ht.stat:
                        if ht.exceeded_by(val):
                            print "Threshold exceeded:", ht.display_name, val
            else:
                for ne in noticed_exceptions:
                    ne.check(line)
conn.commit()

cur.execute("select distinct source from stats where source_type='A'")
adapters = cur.fetchall()

cur.execute("select distinct source from stats where source_type='P'")
peers = [row[0] for row in cur]

# Generate images
def format_data(x, pos):
    #print "format_data called", x, pos
    return time.ctime(x)

my_formatter = FuncFormatter(format_data)

def per_peer_image(sources, query, title, filename):
    fig = plt.gcf()
    fig.clear()
    for source in sources:
        x = []
        y = []
        cur.execute(query, (source,))
        for row in cur:
            x.append(row[0])
            y.append(row[1])
        plt.plot(x, y)
    plt.legend(sources)
    plt.grid(True, which='major')
    plt.grid(True, which='minor')
    fig.subplots_adjust(bottom=0.4)
    axes = plt.gca()
    ax = axes.get_xaxis()
    plt.title(title)
    locs, labels = plt.xticks()
    for label in labels:
        label.set_rotation(90)
    ax.set_major_formatter(my_formatter)
    plt.savefig(filename)

global_images = []

def per_peer_image2(sources, stats, title, **kwds):
    fig = plt.gcf()
    fig.clear()
    legends = []

    try:
        plot_types = kwds["plot_types"]
    except:
        plot_types = ["default" for s in stats]

    try:
        filename = kwds["filename"]
    except:
        filename = stats[0] + ".png"

    # Not currently used, was going to try log scaled charts
    max_exceeded = False

    for source in sources:
        stat_idx = -1
        for stat in stats:
            stat_idx += 1
            x = []
            y = []

            # Check for any non-zero values; if none, don't display
            query = "select count(value) from stats where source=? and stat=? and trim(value) <> '0'"
            cur.execute(query, (source, stat))

            row = cur.fetchone()
            if int(row[0]) == 0:
                print "Not graphing empty series:", source, stat
                continue

            # If we made it this far, we'll have data, so add to the legend
            legend = source
            if len(stats) > 1:
                legend += ("-" + stat)
            if plot_types[stat_idx] != "default":
                legend += ("-" + plot_types[stat_idx])
            legends.append(legend)

            if plot_types[stat_idx] == "rate":
                query = 'select a.timestamp_real,(a.value/(b.value/72000)) from stats a, stats b where a.source=? and a.stat=? and b.stat=\'UPTIME\' and a.source=b.source and a.timestamp_real=b.timestamp_real order by a.timestamp_real'
            else:
                query = "select timestamp_real,value from stats where source=? and stat=? order by timestamp_real"
            cur.execute(query, (source, stat))

            first_row = True
            for row in cur:
                x.append(row[0])
                if plot_types[stat_idx] == "delta":
                    if first_row:
                        val = None
                    else:
                        val = int(row[1].strip()) - last_val
                        if val < 0:
                            val = 0
                else:
                    val = row[1]

                last_val = int(row[1])
                y.append(val)
                first_row = False
            plt.plot(x, y)
    if len(legends) == 0:
        return
    plt.legend(legends, prop=IMG_FONT)
    plt.grid(True, which='major')
    plt.grid(True, which='minor')
    fig.subplots_adjust(bottom=0.4)
    axes = plt.gca()
    if max_exceeded:
        axes.set_yscale("log")
    ax = axes.get_xaxis()
    plt.title(title)
    locs, labels = plt.xticks()
    for label in labels:
        label.set_rotation(90)
    ax.set_major_formatter(my_formatter)
    plt.savefig(BASE_DIR + filename)
    global_images.append(filename)

# Make report/image directory
try:
  os.mkdir(options.tag)
except OSError as e:
  if e.errno != 17: #File exists
    raise

print "Generating charts..."

per_peer_image2(peers, ("NUMBER_OF_THREADS",), "Threads")
per_peer_image2(peers, ("FREE_MEMORY",), "Free Memory")
per_peer_image2(peers, ("COUNT_OF_ACTOR_ADAPTER_CALLS",), "Actor Adapter Calls")
per_peer_image2(peers, ("COUNT_OF_MONITOR_ADAPTER_EVENTS",), "Monitor Adapter Events")
per_peer_image2(peers, ("COUNT_OF_TOTAL_ELECTIONS",), "Total Elections")
per_peer_image2(peers, ("NUMBER_OF_LINK_FAILURES",), "Link Failures")
per_peer_image2(peers, ("COUNT_OF_SHARED_RESOURCES_LOCKS_ACQUIRED",), "Shared Resource Locks Acquired")
per_peer_image2(peers, ("COUNT_OF_SHARED_RESOURCES_LOCKS_ACQUIRED",), "Delta Shared Resource Locks Acquired",
    plot_types=("delta",), filename="delta_locks.png")
per_peer_image2(peers, ("COUNT_OF_SCHEDULES_FIRED",), "Schedules Fired")
per_peer_image2(("G",), ("NUMBER_OF_QUEUED_WORKFLOWS",), "Queued Workflows")
per_peer_image2(peers, ("COUNT_OF_STARTED_PROCESSES", "COUNT_OF_COMPLETED_PROCESSES"), "Started/Completed Processes", filename="completed_processes.png")
per_peer_image2(peers, ("COUNT_OF_STARTED_PROCESSES", "COUNT_OF_COMPLETED_PROCESSES"), "Delta Started/Completed Processes",
    plot_types=("delta", "delta"), filename="delta_completed_processes.png")
per_peer_image2(peers, ("COUNT_OF_FAILED_PROCESSES",), "Failed Processes")
per_peer_image2(peers, ("COUNT_OF_FAILED_PROCESSES",), "Delta Failed Processes", plot_types=("delta",), filename="delta_failed_processes.png")
per_peer_image2(peers, ("COUNT_OF_FAILED_PROCESSES",), "Rate of Failed Processes",
    plot_types=("rate",), filename="rate_failed_processes.png")
per_peer_image2(peers, ("NUMBER_OF_RUNNING_PROCESSES", "NUMBER_OF_RUNNING_PROCESSES_DELAYED_5_MINUTES", "NUMBER_OF_RUNNING_PROCESSES_DELAYED_15_MINUTES"),
                "Running Processes", filename="running_processes.png")

# Write report
report_template = Template(filename=sys.path[0] + "/template.mako")
with open(BASE_DIR + "report.html", "w") as report_fp:
    report_fp.write(report_template.render(adapters=adapters, peers=peers,
        health_thresholds=health_thresholds, noticed_exceptions=noticed_exceptions,
        tag=options.tag, image_list=global_images))
