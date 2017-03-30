"""
Script used by Nagios to check a host's disk, memory and CPU usage.
"""
import sys
import argparse
import re
import psutil

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

def check_disk(limits, all):
    """
    Check disk usage
    """
    print("Checking Disk...")

    ret = STATUS_OK

    # Store problems to print a summary
    problems_summary = []

    try:
        warning_limit, critical_limit = parse_limits(limits)
        for part in psutil.disk_partitions(all):
            print("- Checking device: {} (mounted on {})".format(part.device, part.mountpoint))
            try:
                usage = psutil.disk_usage(part.mountpoint)
                usage_percentage = usage.percent
            except OSError as e:
                # The device is not accessible. Ignoring...
                print("-- Ignoring OSError exception: {}".format(e.strerror))
                continue
            print("-- Disk usage percentage: {}".format(usage_percentage))
            if usage_percentage >= critical_limit:
                problems_summary.append((part.device, part.mountpoint, usage_percentage))
                ret = STATUS_CRITICAL
            elif usage_percentage >= warning_limit:
                # Do not add to summary list if already added by critical check above
                if usage_percentage < critical_limit:
                    problems_summary.append((part.device, part.mountpoint, usage_percentage))
                if ret == STATUS_OK:
                    ret = STATUS_WARNING
    except Exception as e:
        print("- Error: {}".format(e.message))
        ret = STATUS_UNKNOWN

    # Print a summary of problems
    if len(problems_summary) > 0:
        print("")
        print("Summary:")
        print("-" * 20)
        for summary in problems_summary:
            device, mountpoint, usage_percentage = summary
            print('{:8} alert for {} (mounted on {}) - {}% is equal or greater than {}%'.format("CRITICAL" if usage_percentage >= critical_limit else "WARNING",
                device, mountpoint, usage_percentage, critical_limit if usage_percentage >= critical_limit else warning_limit))
        print("-" * 20)
        print("")

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

    parser = argparse.ArgumentParser(description="Script intended to be used by Nagios' services")

    parser.add_argument("-a", "--alldisk", type=special_string, help="Enable all disks check and specify warning and critical values (e.g. 90,95)")
    parser.add_argument("-l", "--localdisk", type=special_string, help="Enable local disk check and specify warning and critical values (e.g. 90,95)")
    parser.add_argument("-m", "--memory", type=special_string, help="Enable memory check and specify warning and critical values (e.g. 90,95)")
    parser.add_argument("-c", "--cpu", type=special_string, help="Enable CPU check and specify warning and critical values (e.g. 90,95)")

    args = parser.parse_args()

    print("Parameters provided:")
    print("-" * 20)
    print("All Disk: {}".format(args.alldisk))
    print("Local Disk: {}".format(args.localdisk))
    print("Memory: {}".format(args.memory))
    print("CPU: {}".format(args.cpu))
    print("-" * 20)

    ret = STATUS_OK

    # Check all disks
    if args.alldisk:
        ret = check_disk(args.alldisk, True)

    # Check local disk
    if (ret != STATUS_CRITICAL) and (args.localdisk):
        if args.alldisk:
            print("Skipping local disk check as all disk check is enabled...")
        else:
            disk_ret = check_disk(args.localdisk, False)
            if disk_ret != STATUS_OK:
                ret = disk_ret

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
