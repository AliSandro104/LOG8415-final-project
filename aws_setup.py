import os
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
    
    return sg

def add_inbound_ip_permissions(sg, ip_protocol, from_port, to_port, ip_ranges, other_sg):
    # add an inbound rule to the security group if it doesn't already exist
    try:
        if other_sg is None:
            ec2_client.authorize_security_group_ingress(
                GroupId = sg['GroupId'],
                IpPermissions = [
                    {
                        'IpProtocol': ip_protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'IpRanges': ip_ranges
                    }
                ]
            )
        else:
            ec2_client.authorize_security_group_ingress(
                GroupId = sg['GroupId'],
                IpPermissions = [
                    {
                        'IpProtocol': ip_protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'UserIdGroupPairs': [{'GroupId': other_sg['GroupId']}]
                    }
                ]
            )
    except ClientError as e:
        return

def add_outbound_ip_permissions(sg, ip_protocol, from_port, to_port, ip_ranges, other_sg):
    # add an outbound rule to the security group if it doesn't already exist
    try:
        if other_sg is None:
            ec2_client.authorize_security_group_egress(
                GroupId = sg['GroupId'],
                IpPermissions = [
                    {
                        'IpProtocol': ip_protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'IpRanges': ip_ranges
                    }
                ]
            )
        else:
            ec2_client.authorize_security_group_egress(
                GroupId = sg['GroupId'],
                IpPermissions = [
                    {
                        'IpProtocol': ip_protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'UserIdGroupPairs': [{'GroupId': other_sg['GroupId']}]
                    }
                ]
            )
    except ClientError as e:
        return
    
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

    # add sql queries to be executed in a sql file
    with open('config/initialize_db.sql', 'w') as sql_file:
        sql_file.write("SOURCE /tmp/sakila-db/sakila-schema.sql;\n")
        sql_file.write("SOURCE /tmp/sakila-db/sakila-data.sql;\n")
        sql_file.write("USE sakila;\n")

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

        # add the sql query to the sql script to grant permission to the workers (index = 0 represents the master node)
        if index != 0:
            with open('config/initialize_db.sql', 'a') as sql_file:
                sql_file.write(f"GRANT ALL ON *.* TO 'worker{index}'@'{cluster[index].private_dns_name}' IDENTIFIED BY 'worker{index}';\n")

def create_gatekeeper(zone_name, key_name, subnet_id, sg):
    # create the gatekeeper and start it
    gatekeeper = create_cluster(1, 't2.large', key_name, zone_name, subnet_id, sg)
    
    instance_id =  [ gatekeeper[0].id ]
    ec2_client.start_instances(InstanceIds = instance_id)
    
    # wait for the instance to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instance_id)

    return gatekeeper

def create_trusted_host(zone_name, key_name, subnet_id, sg):
    # create the trusted host and start it
    trusted_host = create_cluster(1, 't2.large', key_name, zone_name, subnet_id, sg)
    instance_id =  [ trusted_host[0].id ]
    ec2_client.start_instances(InstanceIds = instance_id)
    
    # wait for the instance to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instance_id)

    return trusted_host

def create_proxy(zone_name, key_name, subnet_id, sg):
    # create the proxy and start it
    proxy = create_cluster(1, 't2.large', key_name, zone_name, subnet_id, sg)
    instance_id =  [ proxy[0].id ]
    ec2_client.start_instances(InstanceIds = instance_id)
    
    # wait for the instance to be running before proceeding
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instance_id)

    return proxy

def main():
    KEY_NAME = 'ms_kp_pem'
    ZONE_NAME = 'us-east-1a'

    STANDALONE_SG_NAME = 'standalone'
    CLUSTER_SG_NAME = 'cluster'
    PROXY_SG_NAME = 'proxy'
    TRUSTED_HOST_SG_NAME = 'trusted host'
    GATEKEEPER_SG_NAME = 'gatekeeper'
    ip_ranges = [{'CidrIp': '0.0.0.0/0'}]

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']

    # create key pair
    key_pair = create_key_pair(KEY_NAME)

    # get subnet id
    zone_subnet_id = get_subnet_id(ZONE_NAME) 
    
    # create the cluster security group and add inbound rules
    standalone_sg = create_security_group(name = STANDALONE_SG_NAME, desc = 'Standalone security group', vpc_id = vpc_id)
    cluster_sg = create_security_group(name = CLUSTER_SG_NAME, desc = 'Cluster security group', vpc_id = vpc_id)
    proxy_sg = create_security_group(name = PROXY_SG_NAME, desc = 'Proxy security group', vpc_id = vpc_id)
    trusted_host_sg = create_security_group(name = TRUSTED_HOST_SG_NAME, desc = 'Trusted host security group', vpc_id = vpc_id)
    gatekeeper_sg = create_security_group(name = GATEKEEPER_SG_NAME, desc = 'Gatekeeper security group', vpc_id = vpc_id)

    # add ip permissions for standalone security group
    add_inbound_ip_permissions(standalone_sg, 'tcp', 22, 22, ip_ranges, None)

    # add ip permissions for cluster security group
    add_inbound_ip_permissions(cluster_sg, 'tcp', 22, 22, ip_ranges, None)
    add_inbound_ip_permissions(cluster_sg, 'tcp', 1186, 1186, ip_ranges, cluster_sg)
    add_inbound_ip_permissions(cluster_sg, 'tcp', 3306, 3306, ip_ranges, cluster_sg)
    add_inbound_ip_permissions(cluster_sg, 'tcp', 8082, 8082, ip_ranges, proxy_sg)
    add_inbound_ip_permissions(cluster_sg, 'icmp', -1, -1, ip_ranges, proxy_sg) # allow the cluster to be ping-ed by the proxy
    add_outbound_ip_permissions(cluster_sg, 'tcp', 1186, 1186, ip_ranges, cluster_sg)
    add_outbound_ip_permissions(cluster_sg, 'tcp', 3306, 3306, ip_ranges, cluster_sg)
    add_outbound_ip_permissions(cluster_sg, 'tcp', 8082, 8082, ip_ranges, proxy_sg)
    add_outbound_ip_permissions(cluster_sg, 'icmp', -1, -1, ip_ranges, proxy_sg) # allow the cluster to respond to the ping

    # add ip permissions for proxy security group
    add_inbound_ip_permissions(proxy_sg, 'tcp', 22, 22, ip_ranges, None)
    add_inbound_ip_permissions(proxy_sg, 'tcp', 8082, 8082, ip_ranges, cluster_sg)
    add_inbound_ip_permissions(proxy_sg, 'tcp', 8081, 8081, ip_ranges, trusted_host_sg)
    add_inbound_ip_permissions(proxy_sg, 'icmp', -1, -1, ip_ranges, cluster_sg) # allow the proxy to receive a response after pinging the cluster
    add_outbound_ip_permissions(proxy_sg, 'tcp', 8082, 8082, ip_ranges, cluster_sg)
    add_outbound_ip_permissions(proxy_sg, 'tcp', 8081, 8081, ip_ranges, trusted_host_sg)
    add_outbound_ip_permissions(proxy_sg, 'icmp', -1, -1, ip_ranges, cluster_sg) # allow the proxy to ping the cluster

    # add ip permissions for trusted host security group
    add_inbound_ip_permissions(trusted_host_sg, 'tcp', 22, 22, ip_ranges, None)
    add_inbound_ip_permissions(trusted_host_sg, 'tcp', 8081, 8081, ip_ranges, proxy_sg)
    add_inbound_ip_permissions(trusted_host_sg, 'tcp', 8080, 8080, ip_ranges, gatekeeper_sg)
    add_outbound_ip_permissions(trusted_host_sg, 'tcp', 8081, 8081, ip_ranges, proxy_sg)
    add_outbound_ip_permissions(trusted_host_sg, 'tcp', 8080, 8080, ip_ranges, gatekeeper_sg)
    
    # add ip permissions for gatekeeper security group
    add_inbound_ip_permissions(gatekeeper_sg, 'tcp', 22, 22, ip_ranges, None)
    add_inbound_ip_permissions(gatekeeper_sg, 'tcp', 80, 80, ip_ranges, None)
    add_inbound_ip_permissions(gatekeeper_sg, 'tcp', 443, 443, ip_ranges, None)
    add_inbound_ip_permissions(gatekeeper_sg, 'tcp', 8080, 8080, ip_ranges, trusted_host_sg)
    add_outbound_ip_permissions(gatekeeper_sg, 'tcp', 8080, 8080, ip_ranges, trusted_host_sg)
    
    # create the single instance and start it
    cluster1 = create_cluster(1, 't2.micro', KEY_NAME, ZONE_NAME, zone_subnet_id, cluster_sg)
    instances1 =  [instance.id for instance in cluster1]
    ec2_client.start_instances(InstanceIds = instances1)
    
    # wait for the instance to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instances1)

    # create file that will contain the keypair name and dns name of each instance
    key_pair_name = key_pair.split()[2]
    config_file1 = open('ip_addresses/cluster_public_ip.txt', 'w')
    config_file2 = open('ip_addresses/cluster_private_ip.txt', 'w')
    config_file1.write(f"{key_pair_name}.pem\n")

    # allocate ip address to the instance
    allocate_elastic_ip_to_instances(cluster1, config_file1, config_file2)

    # create the cluster of instances (for mysql cluster) and start them
    cluster2 = create_cluster(4, 't2.micro', KEY_NAME, ZONE_NAME, zone_subnet_id, cluster_sg)
    instances2 =  [instance.id for instance in cluster2]
    ec2_client.start_instances(InstanceIds = instances2)
    
    # wait for the instances to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instances2)
    
    # allocate ip address to the instance
    allocate_elastic_ip_to_instances(cluster2, config_file1, config_file2)

    # close config file
    config_file1.close()
    config_file2.close()

    # create gatekeeper instance
    gatekeeper = create_gatekeeper(ZONE_NAME, KEY_NAME, zone_subnet_id, gatekeeper_sg)
    gatekeeper[0].reload()

    # create trusted host instance
    trusted_host = create_trusted_host(ZONE_NAME, KEY_NAME, zone_subnet_id, trusted_host_sg)
    trusted_host[0].reload()

    # create proxy instance
    proxy = create_proxy(ZONE_NAME, KEY_NAME, zone_subnet_id, proxy_sg)
    proxy[0].reload()

    # store public ip addresses in file 
    with open('ip_addresses/cloud_pattern_public_ip.txt', 'w') as host_file:
        host_file.write(f"{gatekeeper[0].public_dns_name}\n")
        host_file.write(f"{trusted_host[0].public_dns_name}\n")
        host_file.write(f"{proxy[0].public_dns_name}\n")

    # store private ip addresses in file 
    with open('ip_addresses/cloud_pattern_private_ip.txt', 'w') as host_file:
        host_file.write(f"{gatekeeper[0].private_dns_name}\n")
        host_file.write(f"{trusted_host[0].private_dns_name}\n")
        host_file.write(f"{proxy[0].private_dns_name}\n")
    return

if __name__ == "__main__":
    main()