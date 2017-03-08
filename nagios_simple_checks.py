"""
Script used by Nagios to check a host's disk, memory and CPU usage.
"""
import sys
import argparse
import re
import psutil
import time
import os

# Exit codes expected by Nagios
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3

def parse_limits(limits):
    """
    Parses a string like '90,95' and returns each number
    """
    limits = limits.split(",")
    warning = int(limits[0])
    critical = int(limits[1])
    return warning, critical

def check_disk(limits):
    """
    Check disk usage
    """
    print("Checking Disk...")

    ret = STATUS_OK

    try:
        warning, critical = parse_limits(limits)
        for part in psutil.disk_partitions(all=False):
            print("- Checking device: {}".format(part.device))
            try:
                usage = psutil.disk_usage(part.mountpoint)
                usage_percentage = usage.percent
            except OSError as e:
                # The device is not accessible. Ignoring...
                print("-- Ignoring OSError exception: {}".format(e.strerror))
                continue
            print("-- Disk usage percentage: {}".format(usage_percentage))
            if usage_percentage >= warning:
                ret = STATUS_WARNING
            if usage_percentage >= critical:
                ret = STATUS_CRITICAL
                break
    except Exception as e:
        print("- Error: {}".format(e.message))
        ret = STATUS_UNKNOWN

    print("- Returning code {}".format(ret))

    return ret


def check_memory(limits):
    """
    Check memory usage
    """
    print("Checking Memory...")

    ret = STATUS_OK

    try:
        warning, critical = parse_limits(limits)
        memory_information = psutil.virtual_memory()
        usage_percentage = memory_information.percent
        print("- Memory information: {}".format(memory_information))
        print("-- Memory usage percentage: {}".format(usage_percentage))
        if usage_percentage >= warning:
            ret = STATUS_WARNING
        if usage_percentage >= critical:
            ret = STATUS_CRITICAL
    except Exception as e:
        print("- Error: {}".format(e.message))
        ret = STATUS_UNKNOWN

    print("- Returning code {}".format(ret))

    return ret

def check_cpu(limits):
    """
    Check CPU usage
    """
    print("Checking CPU...")

    ret = STATUS_OK

    try:
        warning, critical = parse_limits(limits)
        usage_percentages = []
        for i in range(0, 5):
            usage_percentage = psutil.cpu_percent(interval=1)
            print("{} - CPU usage: {}".format(i, usage_percentage))
            usage_percentages.append(usage_percentage)

        # Calculate the average usage
        average_usage_percentage = sum(usage_percentages) / len(usage_percentages)
        print("- Average CPU usage: {}".format(average_usage_percentage))
        if average_usage_percentage >= warning:
            ret = STATUS_WARNING
        if average_usage_percentage >= critical:
            ret = STATUS_CRITICAL
    except Exception as e:
        print("- Error: {}".format(e.message))
        ret = STATUS_UNKNOWN

    print("- Returning code {}".format(ret))

    return ret

def special_string(value):
    """
    Define special string type for the parameters
    """
    if re.match("^([0-9]+),([0-9]+)$", value):
        return value
    else:
        raise argparse.ArgumentTypeError("String '{}' does not match required format <warning>,<critical>".format(value))

def main():
    """
    Main routine
    """

    script_description = "Script intended to be used by Nagios' services. Example: {} --disk 90,95".format(os.path.basename(__file__))
    parser = argparse.ArgumentParser(description=script_description)

    parser.add_argument("-d", "--disk", type=special_string, help="Enable disk check specifying warning and critical values (e.g. 90,95)")
    parser.add_argument("-m", "--memory", type=special_string, help="Enable memory check specifying warning and critical values (e.g. 90,95)")
    parser.add_argument("-c", "--cpu", type=special_string, help="Enable CPU check specifying warning and critical values (e.g. 90,95)")

    args = parser.parse_args()

    print("Parameters provided:")
    print("-" * 20)
    print("Disk: {}".format(args.disk))
    print("Memory: {}".format(args.memory))
    print("CPU: {}".format(args.cpu))
    print("-" * 20)

    ret = STATUS_OK

    # Check disk
    if args.disk:
        ret = check_disk(args.disk)

    # Check memory
    if (ret != STATUS_CRITICAL) and (args.memory):
        memory_ret = check_memory(args.memory)
        if memory_ret != STATUS_OK:
            ret = memory_ret

    # Check CPU
    if (ret != STATUS_CRITICAL) and (args.cpu):
        cpu_ret = check_cpu(args.cpu)
        if cpu_ret != STATUS_OK:
            ret = cpu_ret

    print("Exiting with code {}".format(ret))

    sys.exit(ret)

if __name__ == "__main__":
    main()
