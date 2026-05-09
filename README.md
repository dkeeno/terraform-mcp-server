# Terraform MCP Server

An MCP server that provides tools for generating, validating, planning, and applying Terraform configurations.

## Features

- **generate_terraform**: Generate Terraform configuration files
- **terraform_init**: Initialize Terraform in a project directory
- **terraform_validate**: Validate Terraform configuration files
- **terraform_plan**: Generate and show execution plan
- **terraform_apply**: Apply configuration to create/update infrastructure
- **terraform_destroy**: Destroy Terraform-managed infrastructure
- **terraform_output**: Read Terraform output values
- **terraform_state_list**: List resources in Terraform state

## Prerequisites

- Python 3.10+
- Terraform CLI installed and in PATH
- Cloud provider credentials configured (AWS, Azure, or GCP)

## Installation

```bash
cd terraform-mcp-server
pip install -r requirements.txt
```

## Configuration

Add to your Claude Code settings (~/.claude/settings.json):

```json
{
  "mcpServers": {
    "terraform": {
      "command": "python",
      "args": ["/Users/youruser/Documents/Base/DevOps-ClaudeAi/test-cases/SM1/my-first-vpc/terraform-mcp-server/server.py"],
      "env": {
        "TERRAFORM_WORKSPACE": "/path/to/your/terraform/projects"
      }
    }
  }
}
```

## Usage

Once configured, Claude Code can use these tools:

```
User: "Initialize terraform in my vpc project"
Claude: [calls terraform_init with project_path]

User: "Run terraform plan"
Claude: [calls terraform_plan]

User: "Apply the changes with auto-approve"
Claude: [calls terraform_apply with auto_approve=true]
```

## Environment Variables

- `TERRAFORM_WORKSPACE`: Base directory for Terraform projects (default: ~/terraform-projects)

## Security Notes

- The `terraform_apply` and `terraform_destroy` commands can make real infrastructure changes
- Always review plans before applying
- Use `auto_approve=false` (default) to require manual confirmation
- Ensure proper cloud provider credentials are configured with least-privilege access
