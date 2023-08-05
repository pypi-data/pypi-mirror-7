Simple Security Groups
======================
Overview
--------

Managing your Amazon Web Services (AWS) Security groups through Cloudformation templates is a great way of handling the creation & updating of all your rules.
But it's a horribly longwinded way of writing out your rules, and get's a bit unwieldy once you hit a certain number.

There are great api's out there (like boto), that let you programatically create your security group objects, but then you then have the headache of writing code to apply them and update tehm, and the inevitable debugging that ensues.  Not to mention the horror you face when you hit the maximum API requests/s.

simplesecuritygroups aim to give you the power and flexibility of python when defining your rules, but rather than directly setting them up, output a familiar Cloudformation template you can use to apply your rules.

1. Define your security groups using simplesecurity groups
2. Output the Cloudformation template
3. Apply using your normal methods!

Installation
------------
Using pip::

    $ pip install simplesecuritygroups

General Things You should Know
------------------------------

1. Most methods support chaining.  i.e. they return the class instance when they're called. This allows for method chaining like you'll see in the methods below.
2. When adding a rule, most parameters can be lists.  This includes ports, protocols, targets.
3. When adding ingress / egress rules outside of a security group, you can suggest a name for the rule.  I say suggest, because if you provide any of the parameters as lists, it's going to ignore it and output a horribly descriptive name :)
4. Port syntax.  simplesecuritygroups don't care if you pass the port as a string or an integer.  It'll still get output as a string in the template.  You can specify a from and to range using the syntax: "8000..8005"

Example Usage
-------------
These examples all assume you're using VPC security groups.  Some old accounts may be using old style EC2 security groups, in which case I'm not sure if this library will work for you!  I hope to test at some point...

**Create a basic security group template with a webserver security group that allows incomming access on http / https ports**

.. code-block:: python

    from simplesecuritygroups.template import SecurityGroups, SecurityGroup

    mytemplate = (
        SecurityGroups("Example Security Group Template")
            .add_resource(
                SecurityGroup("WebserverSecurityGroup", "My Webserver Security Group", "[MyAWSVPCID]")
                    .ingress("tcp", [80, 443])
            )
    )

    print mytemplate

Result:

::

    {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Example Security Group Template",
        "Parameters": {},
        "Resources": {
            "WebserverSecurityGroup": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "My Webserver Security Group",
                    "VpcId": "[MyAWSVPCID]",
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "80",
                            "ToPort": "80",
                            "CidrIp": "0.0.0.0/0"
                        },
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "443",
                            "ToPort": "443",
                            "CidrIp": "0.0.0.0/0"
                        }
                    ]
                }
            }
        }
    }

**Use a Cloudformation template parameter so the template can be re-used for multiple environments**

.. code-block:: python

    from simplesecuritygroups.template import SecurityGroups, SecurityGroup

    mytemplate = (
        SecurityGroups("Example Security Group Template")
            .add_parameter("VPCID", "The ID of your VPC")
            .add_resource(
                SecurityGroup("WebserverSecurityGroup", "My Webserver Security Group", {"Ref": "VPCID"})
                    .ingress("tcp", [80, 443])
            )
    )

    print mytemplate

**Add a rule outside of a Security Group**
(This is often necessary to avoid cirucular dependencies)

.. code-block:: python

    from simplesecuritygroups.template import SecurityGroups, SecurityGroup

    mytemplate = (
        SecurityGroups("Example Security Group Template")
            .add_parameter("VPCID", "The ID of your VPC")
            .add_resource(
                SecurityGroup("WebserverSecurityGroup", "My Webserver Security Group", {"Ref": "VPCID"})
                    .ingress("tcp", [80, 443])
            )
            .add_resource(
                SecurityGroup("LogserverSecurityGroup", "My Logserver Security Group, {"Ref": "VPCID"})
            )
            .pair("WebserverSecurityGroup", "tcp", 20154, "LogServerSecurityGroup", "WebserverLogserverLogging")
    )

    print mytemplate

NOTE: the .pair is just a timesaver method, equivilent to doing:

.. code-block:: python

    .ingress("LogserverSecurityGroup", "tcp", 20154, "WebserverSecurityGroup")
    .egress("WebserverSecurityGroup", "tcp", 20154, "LogserverSecurityGroup")

Result:

::

    {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Example Security Group Template",
        "Parameters": {
            "VPCID": {
                "Description": "The ID of your VPC",
                "Type": "String"
            }
        },
        "Resources": {
            "WebserverSecurityGroup": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "My Webserver Security Group",
                    "VpcId": {
                        "Ref": "VPCID"
                    },
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "80",
                            "ToPort": "80",
                            "CidrIp": "0.0.0.0/0"
                        },
                        {
                            "IpProtocol": "tcp",
                            "FromPort": "443",
                            "ToPort": "443",
                            "CidrIp": "0.0.0.0/0"
                        }
                    ]
                }
            },
            "WebserverLogserverLoggingIngress": {
                "Type": "AWS::EC2::SecurityGroupIngress",
                "Properties": {
                    "GroupId": {
                        "Ref": "LogServerSecurityGroup"
                    },
                    "IpProtocol": "tcp",
                    "FromPort": "20154",
                    "ToPort": "20154",
                    "SourceSecurityGroupId": {
                        "Ref": "WebserverSecurityGroup"
                    }
                }
            },
            "WebserverLogserverLoggingEgress": {
                "Type": "AWS::EC2::SecurityGroupEgress",
                "Properties": {
                    "GroupId": {
                        "Ref": "WebserverSecurityGroup"
                    },
                    "IpProtocol": "tcp",
                    "FromPort": "20154",
                    "ToPort": "20154",
                    "DestinationSecurityGroupId": {
                        "Ref": "LogServerSecurityGroup"
                    }
                }
            }
        }
    }