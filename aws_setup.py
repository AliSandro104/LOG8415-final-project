import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

def get_subnet_id(zone):
    # get the subnet_id based on the availability-zone
    subnetId = ec2_client.describe_subnets(
        Filters = [
        {
            'Name': 'availability-zone',
            'Values': [
                 zone
            ]
        },
        ])['Subnets'][0]['SubnetId']
    return subnetId
    
def create_key_pair(name):
    # if key_pair does not exist, create one
    try:
        ec2_client.describe_key_pairs(KeyNames=[name])
    except ClientError as e:
        ec2.create_key_pair(KeyName=name)
    return ec2_client.describe_key_pairs(KeyNames=[name], IncludePublicKey=True)['KeyPairs'][0]['PublicKey']

def create_security_group(name, desc, vpc_id):
    # if security group does not exist, create one
    try:
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]
    except ClientError as e:
        ec2.create_security_group(GroupName=name, Description = desc, VpcId=vpc_id)
    
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]

        # add rules for security
        ec2_client.authorize_security_group_ingress(
            GroupId = sg['GroupId'],
            IpPermissions = [
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 1186,
                'ToPort': 1186,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
            ]) 
    return sg
    
def create_cluster(count, instance_type, key_name, zone, subnet, security_group):        
    # create the cluster
    cluster = ec2.create_instances(
        ImageId = 'ami-0fc5d935ebf8bc3bc',
        MinCount = count,
        MaxCount = count,
        InstanceType = instance_type,
        KeyName = key_name,
        Placement = {
            'AvailabilityZone': zone
        },     
        SubnetId = subnet,
        SecurityGroupIds = [ security_group['GroupId'] ]           
    )
        
    return cluster

def allocate_elastic_ip_to_instances(cluster, config_file1, config_file2):
    # put the instances id in a list
    instances =  [instance.id for instance in cluster]

    for index, instance_id in enumerate(instances):
        # allocate Elastic IP
        allocation_response = ec2_client.allocate_address(
            Domain='vpc',
        )

        # associate Elastic IP to the instance
        ec2_client.associate_address(
            AllocationId = allocation_response['AllocationId'],
            InstanceId = instance_id,
        )

        # reload the instance attributes
        cluster[index].reload()

        # write DNS name of the instance to a file
        config_file1.write(f"{cluster[index].public_dns_name}\n")
        config_file2.write(f"{cluster[index].private_dns_name}\n")

def create_gatekeeper():
    KEY_NAME = 'ms_kp_pem'
    SECURITY_GROUP_NAME = 'gatekeeper'
    ZONE_NAME = 'us-east-1a'

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME) 

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME)  

    return

def create_proxy():
    KEY_NAME = 'ms_kp_pem'
    SECURITY_GROUP_NAME = 'proxy'
    ZONE_NAME = 'us-east-1a'

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME) 

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME)  

    return

def create_trusted_host():
    KEY_NAME = 'ms_kp_pem'
    SECURITY_GROUP_NAME = 'trusted host'
    ZONE_NAME = 'us-east-1a'

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME) 

    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME)  

    return


def main():
    KEY_NAME = 'ms_kp_pem'
    SECURITY_GROUP_NAME = 'cluster'
    ZONE_NAME = 'us-east-1a'

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']
    
    # create security group
    security_group = create_security_group(name = SECURITY_GROUP_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    
    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME)        
    
    # create the single instance and start it
    cluster1 = create_cluster(1, 't2.micro', KEY_NAME, ZONE_NAME, zone_subnet_id, security_group)
    instances1 =  [instance.id for instance in cluster1]
    ec2_client.start_instances(InstanceIds = instances1)
    
    # wait for the instance to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instances1)

    # create file that will contain the keypair name and dns name of each instance
    key_pair_name = key_pair.split()[2]
    config_file1 = open('instances.txt', 'w')
    config_file2 = open('instances_private.txt', 'w')
    config_file1.write(f"{key_pair_name}.pem\n")

    # allocate ip address to the instance
    allocate_elastic_ip_to_instances(cluster1, config_file1, config_file2)

    # create the cluster of instances and start them
    cluster2 = create_cluster(4, 't2.micro', KEY_NAME, ZONE_NAME, zone_subnet_id, security_group)
    instances2 =  [instance.id for instance in cluster2]
    ec2_client.start_instances(InstanceIds = instances2)
    
    # wait for the instance to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instances2)
    
    # allocate ip address to the instance
    allocate_elastic_ip_to_instances(cluster2, config_file1, config_file2)

    # close config file
    config_file1.close()
    config_file2.close()


if __name__ == "__main__":
    main()