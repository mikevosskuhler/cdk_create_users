from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam
from aws_cdk import aws_cloud9 as c9
import csv
import random
import string
# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

number_of_users = 10
password_length = 25
permissions = ["lambda:*", "event:*", "firehose:*"]

class CdkAppStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        '''
        Create x number of users with a password with x number of random characters. 
        This CDK script can be used to create a number of users for use in workshops or similar. 
        Modify the permissions as needed for your purposes. 
        '''
        bucket = s3.Bucket(self, 
        "MyFirstBucket", 
        versioned=True,)
        statement = iam.PolicyStatement(
            actions = permissions, resources = ["*"])
        group = iam.Group(self, 'test_group', managed_policies = [iam.ManagedPolicy.from_managed_policy_arn(self, 'AWSCloud9User',managed_policy_arn = "arn:aws:iam::aws:policy/AWSCloud9User")])
        group.add_to_policy(statement)
        users = []
        for i in range(number_of_users):
            account = {'password' : get_random_string(password_length), 'user' : f"user-{i}"}
            user = iam.User(self, account['user'], groups = [group], password = cdk.SecretValue.plain_text(account['password']))
            # access_key = iam.CfnAccessKey(self, f"access_key-{i}", user_name = user.user_name)
            # print(type(access_key.attr_secret_access_key))
            cloud9_env = c9.CfnEnvironmentEC2(self, f"cloud9_env_{i}", instance_type = 't2.micro', 
                                                automatic_stop_time_minutes = 30, owner_arn = user.user_arn)
            users.append(account)
            
            
        with open('output.csv', "w") as f:
            dict_writer = csv.DictWriter(f, users[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(users)
            # f.write(json.dumps(users))
            
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str