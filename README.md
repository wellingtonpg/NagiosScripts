# Nagios Scripts

Examples of Nagios commands for **nagios_simple_checks.py**:

#### All Disks Check

```
define command {
    command_name    check_all_disks
    command_line    $USER1$/check_by_ssh -H $HOSTADDRESS$ -l $USER3$ -C "python /path/to/nagios_simple_checks.py --alldisk $ARG1$,$ARG2$"
}
```

#### Local Disk Check

Note: You don't need to run a local disk check if you are already checking all disks.

```
define command {
    command_name    check_local_disk
    command_line    $USER1$/check_by_ssh -H $HOSTADDRESS$ -l $USER3$ -C "python /path/to/nagios_simple_checks.py --localdisk $ARG1$,$ARG2$"
}
```

#### Memory Check

```
define command {
    command_name    check_memory
    command_line    $USER1$/check_by_ssh -H $HOSTADDRESS$ -l $USER3$ -C "python /path/to/nagios_simple_checks.py --memory $ARG1$,$ARG2$"
}
```

#### CPU Check

```
define command {
    command_name    check_cpu
    command_line    $USER1$/check_by_ssh -H $HOSTADDRESS$ -l $USER3$ -C "python /path/to/nagios_simple_checks.py --cpu $ARG1$,$ARG2$"
}
```

Examples of Nagios services:

#### All Disks Check

```
define service {
        use                             local-service
        service_description             All Disks
        normal_check_interval           1
        hostgroup_name                  common
        check_command                   check_all_disks!90!95
}
```

#### Local Disk Check

Note: You don't need to run a local disk check if you are already checking all disks.

```
define service {
        use                             local-service
        service_description             Local Disk
        normal_check_interval           1
        hostgroup_name                  common
        check_command                   check_local_disk!90!95
}
```

#### Memory Check

```
define service {
        use                             local-service
        service_description             Memory
        normal_check_interval           1
        hostgroup_name                  common
        check_command                   check_memory!90!95
}
```

#### CPU Check

```
define service {
        use                             local-service
        service_description             CPU
        normal_check_interval           1
        hostgroup_name                  common
        check_command                   check_cpu!90!95
}
```
