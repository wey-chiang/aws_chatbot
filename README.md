# AWS Infrastructure Chatbot

A natural language chatbot that queries AWS resources by generating and executing boto3 code dynamically.

## Architecture

This chatbot uses a code generation approach where:
1. User asks a question in natural language
2. LLM generates Python code using boto3 to answer the question
3. Code is executed in a sandboxed environment
4. Results are interpreted and presented to the user

## Quick Start

### Using Make (Recommended)

```bash
# Complete setup with virtual environment
make setup

# Activate the virtual environment
source venv/bin/activate

# Run the chatbot
make run
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .
```

### 2. Configure AWS Credentials

Use any of these methods:

```bash
# Method 1: AWS CLI
aws configure

# Method 2: Environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Method 3: IAM role (if on EC2)
# Automatically handled by boto3
```

### 3. Set OpenAI API Key

```bash
# Create .env file
echo "OPENAI_API_KEY=your-openai-key" > .env

# Or export directly
export OPENAI_API_KEY='your-openai-key'
```

## Usage

### Interactive Mode

```bash
# Using the installed command
aws-chatbot

# Or using make
make run
```

### Single Query

```bash
# Using the installed command
aws-chatbot "How many S3 buckets are exposed to the public?"

# Or using make
make query Q="How many S3 buckets are exposed to the public?"
```

### Output Formats

```bash
# Natural language (default)
aws-chatbot "What permissions does the user john have?"

# JSON format
aws-chatbot --format json "List all EC2 instances"

# Table format
aws-chatbot --format table "What is the size of the EC2 instance with IP 10.0.0.1?"
```

### Verbose Mode

See the generated code and execution steps:

```bash
aws-chatbot --verbose "What data does the S3 bucket my-bucket hold?"

# Or using make
make run-verbose
```

## Example Queries

- **S3**: 
  - "How many S3 buckets are exposed to the public?"
  - "What data does the S3 bucket my-data-bucket hold?"
  - "List all S3 buckets created in the last 30 days"

- **EC2**:
  - "What is the size of the EC2 instance with IP 10.0.1.5?"
  - "List all running EC2 instances and their types"
  - "Which EC2 instances don't have termination protection?"

- **IAM**:
  - "What permissions does the user developer-jane have?"
  - "List all IAM roles that can be assumed by EC2"
  - "Which users have AdministratorAccess?"

- **Cross-Service**:
  - "How much am I spending on EC2 vs S3 this month?"
  - "Which resources are in the us-west-2 region?"
  - "Find all resources tagged with Environment=Production"

## Makefile Commands

The project includes a comprehensive Makefile for easy management:

```bash
make help          # Show all available commands
make setup         # Complete setup (venv, deps, .env)
make install       # Install package and dependencies
make install-dev   # Install with dev dependencies
make run           # Run chatbot in interactive mode
make run-verbose   # Run with verbose output
make query Q="..." # Run a single query
make clean         # Clean all build artifacts
make lint          # Run code linting
make format        # Format code with black
make check-aws     # Check AWS credentials
make check-env     # Check environment setup
make status        # Full system status check
```

## How It Works

The chatbot generates boto3 code to answer your questions. For example:

**Question**: "How many S3 buckets are exposed to the public?"

**Generated Code**:
```python
import boto3
import json

s3 = boto3.client('s3')
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
```

## Security

- Code execution is sandboxed with restricted imports
- Only boto3 and json are available to generated code
- 30-second timeout on all code execution
- No file system or network access (except AWS APIs)

## Limitations

- Read-only operations are recommended (though write operations are possible)
- Code execution timeout is 30 seconds
- Complex multi-step operations may require multiple queries
  - Support for multi-step operations may be limited 

## Troubleshooting

1. **AWS Credentials Error**: Ensure your AWS credentials are properly configured
2. **OpenAI API Error**: Verify your OpenAI API key is valid
3. **Timeout Error**: Complex queries may timeout - try breaking them into smaller queries
4. **No Output**: Use `--verbose` flag to see the generated code and debug