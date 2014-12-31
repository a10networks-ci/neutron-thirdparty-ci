#!/bin/bash

# JClouds leaves droppings. Clean them up.

if [ -z "$LOCKED" ]; then
    # Only one of us gets to run at a time
    (
        flock -n 9 || exit 1
        export LOCKED=1
        exec $0 $*
    ) 9>/tmp/cleanup-ec2.lock

elif [ -n "$CRON_RUN" ]; then
    # Cron environment setup foo
    export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games

    mv /tmp/cleanup-ec2.out /tmp/cleanup-ec2.out.old
    exec >/tmp/cleanup-ec2.out 2>&1

    set -x
fi

# Is the given host a Jenkins slave?
is_slave() {
    ip=$1
    ssh -o StrictHostKeyChecking=no ubuntu@$ip ps auxww > $t.2
    if [ -z "$t.2" ]; then
        # Empty means we got no results; something went wrong
        return 0
    fi
    n=$(cat $t.2 | grep slave | grep -v grep | wc -l)
    if [ $n -eq 0 ]; then
        return 1
    else
        return 0
    fi
}

t=/tmp/.cleanup-ec2.$$

instances=$(aws ec2 describe-instances --filter Name=instance-type,Values=m3.medium | egrep InstanceId | perl -ne '/"InstanceId": "(.*?)",/ && print "$1\n";')

for i in $instances; do
    aws ec2 describe-instances --instance-ids $i > $t

    # If this is not a jclouds instance, skip it
    jclouds=$(grep -c jcloud $t)
    if [ $jclouds -eq 0 ]; then
        continue
    fi

    ip=$(grep PublicIpAddress $t | head -1 | perl -ne '/"PublicIpAddress": "(.*?)",/ && print "$1\n";')

    if [ -z "$ip" ]; then
        continue
    fi

    # Check if the instance is a Jenkins slave
    if ! is_slave $ip; then
        # Not a slave; give it a few seconds to become one
        sleep 10

        # Last chance; if still not a slave, toast it
        if ! is_slave $ip; then
            echo aws ec2 terminate-instances --instance-ids $i
        fi
    fi
done

rm -f $t $t.2
exit 0
