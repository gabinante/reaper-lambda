#### WARNING ####
# This script iterates through all the specified regions and terminates any instances
# which do not have an expiration_date tag, or any instances wherein the expiration_date
# tag is before the current epoch. If you're not using epoch time, or if you haven't
# tagged your instances, this will blow up your whole AWS account.
# Consider this fair warning!

import boto3
import logging
import time

# Boto logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This might need to be split across multiple regions if your AWS account is huge.
regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2', 'eu-west-1', 'eu-west-2', 'ap-northeast-1', 'ap-southeast-2']

def lambda_handler(event, context):

    for each in regions:

        ec2client = boto3.client('ec2', region_name='{}'.format(region))

        # Create empty arrays to avoid TypeErrors if any regions return empty
        all_instances = []
        all_instances.extend(grab_all_instances(each))

        expired_instances = []
        expired_instances.extend(check_expired_instances(each, all_instances))

        tagged_instances = []
        tagged_instances.extend(list_instances_by_tag('expiration_date', each))

        # Make an array of all untagged & expired instances
        instances_to_delete = []
        instances_to_delete.extend(all_instances)

        # Remove instances that are properly tagged for expiration
        print 'comparing expired instances: {} to all instances tagged for expiration: {}'.format(expired_instances, tagged_instances)
        for each in tagged_instances:
            if each not in expired_instances:
                instances_to_delete.remove(each)

        # Iterate over instances_to_delete and terminate each one of them
        print "instances to delete: {}".format(instances_to_delete)
        for instance in instances_to_delete:
            # TEST THIS FIRST! Uncomment the stop command if you're ready to go!
            print "terminating {}".format(instance)
            #ec2client.terminate_instances(InstanceIds=[''.format(instance)])



def grab_all_instances(region):
    # Snags ID of all instances in a region
    ec2client = boto3.client('ec2', region_name='{}'.format(region))
    all_ec2_instances = []

    response = ec2client.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            all_ec2_instances.append(str(instance["InstanceId"]))
    print 'got all instances for {}: {}'.format(region, all_ec2_instances)
    return all_ec2_instances

def list_instances_by_tag(tagkey, region):
    # When passed a tag key, this will return a list of InstanceIDs that were found.

    ec2client = boto3.client('ec2', region_name='{}'.format(region))

    response = ec2client.describe_instances(Filters=[{'Name': 'tag:'+tagkey, 'Values': ['*']}])
    instancelist_from_tag = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist_from_tag.append(instance["InstanceId"])
    print 'got tagged instance list for {}: {}'.format(region, instancelist_from_tag)
    return instancelist_from_tag

def check_expired_instances(region, instances_to_check):
    # When passed a region and list of instance IDs, this will return a list of
    # InstanceIDs that were found to be past their expiration date

    ec2client = boto3.client('ec2', region_name='{}'.format(region))
    expired_list = []
    epoch_time = int(time.time())
    if instances_to_check:
        print 'checking following instances for expiration_date: {}'.format(instances_to_check)
        for instanceID in instances_to_check:
            try:
                ec2instance = ec2client.describe_instances(InstanceIds=['{}'.format(instanceID)])
                for reservation in ec2instance["Reservations"]:
                    for instance in reservation["Instances"]:
                        for tags in instance["Tags"]:
                            print "found tags for {}:{}".format(instanceID, tags)
                            if tags["Key"] == 'expiration_date':
                                if tags["Value"] != 'never':
                                    expiration_date = int(tags["Value"])
                                    print 'checking expiration date {} versus current epoch: {}'.format(expiration_date, epoch_time)
                                    if expiration_date < epoch_time:
                                        expired_list.append(instanceID)

            except Exception as e:
                print "Failed to retrieve info for {}: {}".format(instanceID, e)
        print 'got expired instances for {}: {}'.format(region, expired_list)
        return expired_list

