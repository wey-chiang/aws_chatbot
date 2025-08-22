import json
import boto3
from moto import mock_aws

from aws_chatbot.executor import SafeCodeExecutor


class TestAWSIntegration:
    def test_s3_list_buckets(self):
        """Test listing S3 buckets"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json
s3 = boto3.client('s3', region_name='us-east-1')
response = s3.list_buckets()
buckets = [b['Name'] for b in response['Buckets']]
print(json.dumps({'buckets': buckets, 'count': len(buckets)}))
"""
        with mock_aws():
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="test-bucket-1")
            s3.create_bucket(Bucket="test-bucket-2")

            output = executor.execute(code)
        result = json.loads(output)
        assert result["count"] == 2
        assert "test-bucket-1" in result["buckets"]
        assert "test-bucket-2" in result["buckets"]

    def test_s3_check_public_buckets(self):
        """Test checking for public S3 buckets"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json

s3 = boto3.client('s3', region_name='us-east-1')
buckets = s3.list_buckets()
public_buckets = []

for bucket in buckets['Buckets']:
    bucket_name = bucket['Name']
    try:
        acl = s3.get_bucket_acl(Bucket=bucket_name)
        for grant in acl['Grants']:
            grantee = grant.get('Grantee', {})
            if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                public_buckets.append(bucket_name)
                break
    except Exception as e:
        pass

result = {
    'total_buckets': len(buckets['Buckets']),
    'public_buckets': public_buckets,
    'public_count': len(public_buckets)
}
print(json.dumps(result))
        """
        with mock_aws():
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="public-bucket")
            s3.create_bucket(Bucket="private-bucket")

            # Make one bucket public
            s3.put_bucket_acl(Bucket="public-bucket", ACL="public-read")

            output = executor.execute(code)
        result = json.loads(output)

        assert result["total_buckets"] == 2
        assert result["public_count"] == 1
        assert "public-bucket" in result["public_buckets"]

    def test_s3_list_bucket_objects(self):
        """Test listing objects in an S3 bucket"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json

s3 = boto3.client('s3', region_name='us-east-1')
response = s3.list_objects_v2(Bucket='data-bucket')
objects = []
total_size = 0

for obj in response.get('Contents', []):
    objects.append({
        'key': obj['Key'],
        'size': obj['Size']
    })
    total_size += obj['Size']

result = {
    'bucket': 'data-bucket',
    'object_count': len(objects),
    'total_size': total_size,
    'objects': objects
}
print(json.dumps(result))
"""
        with mock_aws():
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="data-bucket")
            s3.put_object(Bucket="data-bucket", Key="file1.txt", Body=b"content1")
            s3.put_object(Bucket="data-bucket", Key="file2.json", Body=b'{"test": "data"}')

            output = executor.execute(code)
        result = json.loads(output)

        assert result["bucket"] == "data-bucket"
        assert result["object_count"] == 2
        assert any(obj["key"] == "file1.txt" for obj in result["objects"])
        assert any(obj["key"] == "file2.json" for obj in result["objects"])

    @mock_aws
    def test_ec2_describe_instances(self):
        """Test describing EC2 instances"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json

ec2 = boto3.client('ec2', region_name='us-east-1')
response = ec2.describe_instances()
instances = []

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instances.append({
            'id': instance['InstanceId'],
            'type': instance['InstanceType'],
            'state': instance['State']['Name']
        })

result = {
    'total_instances': len(instances),
    'instances': instances
}
print(json.dumps(result))
        """
        with mock_aws():
            ec2 = boto3.client("ec2", region_name="us-east-1")
            response = ec2.run_instances(ImageId="ami-12345678", MinCount=2, MaxCount=2, InstanceType="t2.micro")
            output = executor.execute(code)
            result = json.loads(output)

        assert result["total_instances"] == 2
        assert all(inst["type"] == "t2.micro" for inst in result["instances"])

    @mock_aws
    def test_iam_list_users(self):
        """Test listing IAM users"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json

iam = boto3.client('iam', region_name='us-east-1')
response = iam.list_users()
users = [user['UserName'] for user in response['Users']]

result = {
    'total_users': len(users),
    'users': users
}
print(json.dumps(result))
        """
        with mock_aws():
            iam = boto3.client("iam", region_name="us-east-1")
            iam.create_user(UserName="test-user-1")
            iam.create_user(UserName="test-user-2")
            output = executor.execute(code)
        result = json.loads(output)

        assert result["total_users"] == 2
        assert "test-user-1" in result["users"]
        assert "test-user-2" in result["users"]

    @mock_aws
    def test_iam_user_permissions(self):
        """Test getting IAM user permissions"""
        executor = SafeCodeExecutor()
        code = """
import boto3
import json

iam = boto3.client('iam')
username = 'developer-john'

user_policies = iam.list_user_policies(UserName=username)
groups = iam.list_groups_for_user(UserName=username)

result = {
    'user': username,
    'inline_policies': user_policies.get('PolicyNames', []),
    'groups': [g['GroupName'] for g in groups.get('Groups', [])]
}
print(json.dumps(result))
"""
        with mock_aws():
            iam = boto3.client("iam", region_name="us-east-1")
            iam.create_user(UserName="developer-john")
            iam.create_group(GroupName="developers")
            iam.add_user_to_group(GroupName="developers", UserName="developer-john")

            # Create and attach inline policy
            policy_doc = {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}],
            }
            iam.put_user_policy(UserName="developer-john", PolicyName="S3Access", PolicyDocument=json.dumps(policy_doc))
            output = executor.execute(code)
        result = json.loads(output)

        assert result["user"] == "developer-john"
        assert "S3Access" in result["inline_policies"]
        assert "developers" in result["groups"]
