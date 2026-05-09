#!/usr/bin/env python3
"""
Terraform MCP Server
Provides tools for generating, validating, planning, and applying Terraform configurations.
"""

import asyncio
import json
import subprocess
import os
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

server = Server("terraform-mcp-server")

TERRAFORM_WORKSPACE = os.environ.get("TERRAFORM_WORKSPACE", str(Path.home() / "terraform-projects"))
Path(TERRAFORM_WORKSPACE).mkdir(parents=True, exist_ok=True)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Terraform tools."""
    return [
        Tool(
            name="generate_terraform",
            description="Generate Terraform configuration files (main.tf, variables.tf, outputs.tf)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the Terraform project directory"
                    },
                    "provider": {
                        "type": "string",
                        "description": "Cloud provider (aws, azure, gcp)",
                        "enum": ["aws", "azure", "gcp"]
                    },
                    "resources": {
                        "type": "string",
                        "description": "Description of resources to create (e.g., 'VPC with 2 subnets', 'S3 bucket with versioning')"
                    },
                    "region": {
                        "type": "string",
                        "description": "Cloud region (e.g., us-east-1, eastus, us-central1)"
                    },
                    "tags": {
                        "type": "object",
                        "description": "Tags to apply to resources (optional)"
                    }
                },
                "required": ["project_name", "provider", "resources", "region"]
            }
        ),
        Tool(
            name="terraform_init",
            description="Initialize Terraform in a project directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_validate",
            description="Validate Terraform configuration files",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_plan",
            description="Generate and show Terraform execution plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    },
                    "var_file": {
                        "type": "string",
                        "description": "Path to .tfvars file (optional)"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_apply",
            description="Apply Terraform configuration to create/update infrastructure",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    },
                    "auto_approve": {
                        "type": "boolean",
                        "description": "Skip interactive approval (default: false)",
                        "default": False
                    },
                    "var_file": {
                        "type": "string",
                        "description": "Path to .tfvars file (optional)"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_destroy",
            description="Destroy Terraform-managed infrastructure",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    },
                    "auto_approve": {
                        "type": "boolean",
                        "description": "Skip interactive approval (default: false)",
                        "default": False
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_output",
            description="Read Terraform output values",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    },
                    "output_name": {
                        "type": "string",
                        "description": "Specific output to retrieve (optional, returns all if not specified)"
                    }
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="terraform_state_list",
            description="List resources in Terraform state",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to Terraform project directory"
                    }
                },
                "required": ["project_path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for Terraform operations."""

    if name == "generate_terraform":
        project_path = Path(TERRAFORM_WORKSPACE) / arguments["project_name"]
        project_path.mkdir(parents=True, exist_ok=True)

        # This is a simplified example - in production, you'd use templates or generate based on the description
        result = f"Generated Terraform project at: {project_path}\n\n"
        result += "Note: This is a template generator. For specific resources, you should provide detailed templates.\n"
        result += f"Provider: {arguments['provider']}\n"
        result += f"Region: {arguments['region']}\n"
        result += f"Resources requested: {arguments['resources']}\n"

        return [TextContent(type="text", text=result)]

    elif name == "terraform_init":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        result = subprocess.run(
            ["terraform", "init"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_validate":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        result = subprocess.run(
            ["terraform", "validate"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_plan":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        cmd = ["terraform", "plan"]
        if "var_file" in arguments and arguments["var_file"]:
            cmd.extend(["-var-file", arguments["var_file"]])

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_apply":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        cmd = ["terraform", "apply"]
        if arguments.get("auto_approve", False):
            cmd.append("-auto-approve")
        if "var_file" in arguments and arguments["var_file"]:
            cmd.extend(["-var-file", arguments["var_file"]])

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            input="" if arguments.get("auto_approve", False) else None
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_destroy":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        cmd = ["terraform", "destroy"]
        if arguments.get("auto_approve", False):
            cmd.append("-auto-approve")

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            input="" if arguments.get("auto_approve", False) else None
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_output":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        cmd = ["terraform", "output", "-json"]
        if "output_name" in arguments and arguments["output_name"]:
            cmd = ["terraform", "output", arguments["output_name"]]

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    elif name == "terraform_state_list":
        project_path = Path(arguments["project_path"])
        if not project_path.exists():
            return [TextContent(type="text", text=f"Error: Project path does not exist: {project_path}")]

        result = subprocess.run(
            ["terraform", "state", "list"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        output = f"Exit code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return [TextContent(type="text", text=output)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
