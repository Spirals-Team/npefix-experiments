import os
from os.path import isdir, isfile, join
import json
import datetime

def avg(lst):
    return sum(lst)/float(len(lst))
def med(lst):
    lst = sorted(lst)
    if len(lst) < 1:
        return None
    if len(lst) %2 == 1:
        return lst[((len(lst)+1)/2)-1]
    else:
        return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0
def formatTime(time):
    return str(datetime.timedelta(milliseconds=time)).partition(".")[0]

currentDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "results", "current")
dirs = [f for f in os.listdir(currentDir) if isdir(join(currentDir, f))]
collectObjects={}
projectNames=[]
for directory in dirs:
    if directory in ["www", "log"] :
        continue
    selector = {
        "name": directory,
        "projects": []
    }

    if directory not in ["Template", "MonoExplorerSelector"]:
        continue

    collectObject = {
        "diff": [],
        "patch": [],
        "valid": [],
        "patchSec": [],
        "init": [],
        "run": [],
        "firstPatch": [],
        "total": []
    }
    print "# " + directory
    print " {0:15} & {1:8} & {2:8} & {3:9} & {4:9}\\\\".format(
        "Bug ID",
        "\# Patch",
        "\# Valid",
        "First Patch",
        "Total Time")
    projects = sorted([f for f in os.listdir(join(currentDir, directory)) if isdir(join(join(currentDir, directory), f))])
    for p in projects:
        project = {
            "name": p,
            "versions": []
        }
        max_version = None
        versions = [f for f in os.listdir(join(currentDir, directory, p)) if isfile(join(join(currentDir, directory, p), f))]
        for version in versions:
            version = os.path.splitext(version)[0]
            if max_version is None:
                max_version = version
                continue
            if version > max_version:
                max_version = version
        # no execution found
        if max_version is None:
            continue
        if project['name'] not in projectNames:
            projectNames += [project["name"]]
        executionPath = join(currentDir, directory, p, max_version + ".json")
        executionData = json.load(open(executionPath))
        countValid = 0
        for execution in executionData['executions']:
            if 'decisions' not in execution:
                continue
            if execution['result']['success']:
                countValid += 1
        executionTime = 1
        if 'end' in executionData:
            executionTime = executionData['end'] - executionData['start']
        collectObject["total"] += [executionTime]
        collectObject["valid"] += [countValid]

        executionInitTime = 1
        if 'endInit' in executionData:
            executionInitTime = executionData['endInit'] - executionData['start']
        collectObject["init"] += [executionInitTime]
        collectObject["run"] += [executionTime - executionInitTime]

        diffs = []
        executions = executionData['executions']
        for execution in executions:
            if 'decisions' not in execution or not execution['decisions'][0]['used']:
                executions.remove(execution)
            elif 'diff' in execution and execution['result']['success']:
                diff = execution['diff']
                diff = "\n".join(diff.split("\n")[2:])
                diffs += [diff]
        collectObject["diff"] += [diffs]
        searchSpaceSize = len(executions)
        collectObject["patch"] += [searchSpaceSize]

        patchPerSecond = float(searchSpaceSize) / executionTime * 1000
        collectObject["patchSec"] += [patchPerSecond]

        firstPatch = executionInitTime
        for execution in executions:
            firstPatch += execution['endDate'] - execution['startDate']
            if execution['result']['success']:
                break

        collectObject["firstPatch"] += [firstPatch]

        print " {0:15} & {1:8} & {2:8} & {3:9} & {4:9} \\\\".format(project['name'],
                                                                        searchSpaceSize,
                                                                        countValid,
                                                                        formatTime(firstPatch),
                                                                        formatTime(executionTime))
    collectObjects[selector['name']] = collectObject
    print "\hline"
    print " {0:15} & {1:8} & {2:8} & {3:9} & {4:9}\\\\".format("Total",
                                                                    sum(collectObject["patch"]),
                                                                    sum(collectObject["valid"]),
                                                                    formatTime(sum(collectObject["firstPatch"])),
                                                                    formatTime(sum(collectObject["total"])))
    print " {0:15} & {1:8} & {2:8} & {3:9} & {4:9}\\\\".format("Average",
                                                                    "%.2f" % avg(collectObject["patch"]),
                                                                    "%.2f" % avg(collectObject["valid"]),
                                                                    formatTime(avg(collectObject["firstPatch"])),
                                                                    formatTime(avg(collectObject["total"])))
    print " {0:15} & {1:8} & {2:8} & {3:9} & {4:9}\\\\".format("Median",
                                                                    "%.2f" % med(collectObject["patch"]),
                                                                    "%.2f" % med(collectObject["valid"]),
                                                                    formatTime(med(collectObject["firstPatch"])),
                                                                    formatTime(med(collectObject["total"])))

    print " {0:15} & {1:9} & {2:9} & {3:12} & {4:12} & {5:12} & {6:12}\\\\".format("Project",
                                                   "\# Patch Template",
                                                   "\# Patch NPEFix",
                                                   "\# Correct Template",
                                                   "\# Correct NPEFix",
                                                   "Execution Template",
                                                   "Execution NPEFix")

cout = 0
for idx, project in enumerate(projectNames):
    cout += len([x for x in collectObjects['MonoExplorerSelector']['diff'][idx] if x not in collectObjects['Template']['diff'][idx]])

    print " {0:15} & {1:9} & {2:9} & {3:12} & {4:12} & {5:12} & {6:12}\\\\".format(project,
            collectObjects['Template']['patch'][idx],
            collectObjects['MonoExplorerSelector']['patch'][idx],
            collectObjects['Template']['valid'][idx],
            collectObjects['MonoExplorerSelector']['valid'][idx],
            formatTime(collectObjects['Template']["total"][idx]),
            formatTime(collectObjects['MonoExplorerSelector']["total"][idx]))
print "\hline"
if 'Template' in collectObjects and 'MonoExplorerSelector' in collectObjects:
    print " {0:15} & {1:9} & {2:9} & {3:12} & {4:12} & {5:12} & {6:12}\\\\".format("Total",
                                               sum(collectObjects['Template']['patch']),
                                               sum(collectObjects['MonoExplorerSelector']['patch']),
                                               sum(collectObjects['Template']['valid']),
                                               sum(collectObjects['MonoExplorerSelector']['valid']),
                                               formatTime(sum(collectObjects['Template']["total"])),
                                               formatTime(sum(collectObjects['MonoExplorerSelector']["total"])))

    print " {0:15} & {1:9} & {2:9} & {3:12} & {4:12} & {5:12} & {6:12}\\\\".format("Average",
            "%.2f" % avg(collectObjects['Template']['patch']),
            "%.2f" % avg(collectObjects['MonoExplorerSelector']['patch']),
            "%.2f" % avg(collectObjects['Template']['valid']),
            "%.2f" % avg(collectObjects['MonoExplorerSelector']['valid']),
            formatTime(avg(collectObjects['Template']["total"])),
            formatTime(avg(collectObjects['MonoExplorerSelector']["total"])))
    print " {0:15} & {1:9} & {2:9} & {3:12} & {4:12} & {5:12} & {6:12}\\\ \hline".format("Median",
            "%.2f" % med(collectObjects['Template']['patch']),
            "%.2f" % med(collectObjects['MonoExplorerSelector']['patch']),
            "%.2f" % med(collectObjects['Template']['valid']),
            "%.2f" % med(collectObjects['MonoExplorerSelector']['valid']),
            formatTime(med(collectObjects['Template']["total"])),
            formatTime(med(collectObjects['MonoExplorerSelector']["total"])))