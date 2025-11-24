"""
Skylar Compliance Data Models

This module defines all Pydantic data models used throughout the Skylar Compliance MCP server.
These models provide type safety, data validation, and automatic serialization/deserialization
for API responses and internal data structures.

All models use Pydantic's Field with aliases to map between the API's naming convention
(PascalCase - Golang) and Python's naming convention (snake_case).
"""

from datetime import datetime
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseEnvelope(BaseModel, Generic[T]):
    results: List[T] = Field(description="List of response objects")
    num_results: int = Field(
        description="Total number of results possible based on the query")

class Device(BaseModel):
    id: int = Field(description="ID of the device", validation_alias="ID")
    name: str = Field(description="Display name of the device",
                      validation_alias="Name")
    compliance_status: str = Field(
        description="Compliance status of the device", validation_alias="ComplianceStatus")
    plugin_name: str = Field(
        description="Name of the plugin", validation_alias="PluginName")
    state: str = Field(
        description="The current state of the device", validation_alias="State")
    status: str = Field(
        description="The current status of the device", validation_alias="Status")


class BackupMetadataByConfigType(BaseModel):
    id: int = Field(description="ID of the backup")
    name: str = Field(description="Display name of the backup")
    created: str = Field(description="Date the backup was created")
    baseline: bool = Field(description="True if this is a baseline config, restoring any other backup creates a compliance alert")
    sha256: str = Field(description="SHA256 hash of the backup", exclude=True)


class BackupMetadata(BaseModel):
    id: int = Field(description="ID of the backup", validation_alias="ID")
    name: str = Field(description="Display name of the backup",
                      validation_alias="Name")
    created: str = Field(
        description="Date the backup was created", validation_alias="Created")
    types: List[str] = Field(
        description="Type of backups available", validation_alias="ConfigurationTypes")
    version: int = Field(
        description="version of the backup", validation_alias="Version")
    baseline: bool = Field(
        description="True if this is a baseline config, restoring any other backup creates a compliance alert",
        validation_alias="IsBaseline"
    )


class Backup(BaseModel):
    total_lines: int = Field(
        description="total number of lines in the backup", validation_alias="TotalLines")
    num_lines: int = Field(
        description="number of lines returned from the backup", validation_alias="NumLines")
    lines: List[str] = Field(
        description="lines from the backup", validation_alias="Lines")


class BackupDiff(BaseModel):
    diff: str = Field(description="diff output", validation_alias="Diff")
    total: int = Field(
        description="total number of line differences", validation_alias="Total")


class Agent(BaseModel):
    id: int = Field(description="ID of the agent", validation_alias="ID")
    name: str = Field(description="Display name of the agent",
                      validation_alias="Name")


class Job(BaseModel):
    id: int = Field(description="ID of the job", validation_alias="ID")
    type: str = Field(description="type of the job", validation_alias="Type")
    description: str = Field(
        description="description of the job", validation_alias="Description")
    device_id: Optional[int] = Field(
        default=None, description="id of the device affected", validation_alias="DeviceID")
    device_name: Optional[str] = Field(
        default=None, description="name of the device affected", validation_alias="DeviceName")
    progress: int = Field(
        description="percentage progress of job", validation_alias="Progress")
    user: str = Field(
        description="name of user that started the job", validation_alias="User")
    created: datetime = Field(
        description="time the job started", validation_alias="Created")
    status: str = Field(description="status of the job",
                        validation_alias="Status")


class Log(BaseModel):
    id: int = Field(description="ID of the log entry", validation_alias="ID")
    created: datetime = Field(
        description="time of the log message", validation_alias="Created")
    action: str = Field(description="type of log message",
                        validation_alias="Action")
    message: str = Field(
        description="content of the log message", validation_alias="Message")
    object_type: str = Field(
        description="type of object the log is about", validation_alias="ObjectType")
    object_id: int = Field(
        description="id of the object the log is about", validation_alias="ObjectID")
    object_name: str = Field(
        description="name of the object the log is about", validation_alias="ObjectName")
    user_id: int = Field(
        description="id of the user that caused the log", validation_alias="UserID")
    user_name: str = Field(
        description="name of the user that caused the log", validation_alias="UserName")
    user_ip_address: str = Field(
        description="ip of the user that caused the log", validation_alias="UserIPAddress")
    level: str = Field(
        description="severity level of the message", validation_alias="Level")


class StatusAppliance(BaseModel):
    expiration: str = Field(
        description="When the license expires", validation_alias="Expiration")
    version: str = Field(
        description="version of Skylar Compliance", validation_alias="Version")
    build: str = Field(
        description="build number of Skylar Compliance", validation_alias="Build")
    serial: str = Field(
        description="serial number of the system", validation_alias="Serial")
    max_devices: int = Field(
        description="number of devices allowed by the license", validation_alias="MaxDevices")


class StatusStorage(BaseModel):
    total: int = Field(
        description="total amount of bytes on system", validation_alias="Total")
    used: int = Field(
        description="total amount of bytes used on system", validation_alias="Used")
    available: int = Field(
        description="total amount of bytes available on system", validation_alias="Available")
    backup: int = Field(
        description="total amount of bytes used by backups on system", validation_alias="Backup")
    index: int = Field(
        description="total amount of bytes used by indexes on system", validation_alias="Index")
    cache: int = Field(
        description="total amount of bytes used by caching on system", validation_alias="Cache")
    debug: int = Field(
        description="total amount of bytes used by debug on system", validation_alias="Debug")
    other: int = Field(
        description="total amount of bytes used by other on system", validation_alias="Other")
    calculating_backups: bool = Field(
        description="are backups being calculated", validation_alias="CalculatingBackups")


class StatusMemory(BaseModel):
    total: int = Field(
        description="total amount of memory on system", validation_alias="Total")
    used: int = Field(
        description="total amount of memory used on system", validation_alias="Used")
    available: int = Field(
        description="total amount of memory on system", validation_alias="Available")
    swap: int = Field(
        description="total amount of swap memory on system", validation_alias="Swap")


class StatusSystem(BaseModel):
    release: str = Field(description="name of the os distro",
                         validation_alias="Release")
    uptime: int = Field(description="seconds of uptime",
                        validation_alias="Uptime")
    load: List[float] = Field(
        description="list of current cpu loads", validation_alias="Load")
    files_open: int = Field(
        description="number of open file handles", validation_alias="FilesOpen")
    processes: int = Field(
        description="number of processes running", validation_alias="Processes")
    local_ip: str = Field(
        description="ip address of the system", validation_alias="LocalIP")
    memory: StatusMemory = Field(
        description="memory status of the system", validation_alias="Memory")


class Status(BaseModel):
    appliance: StatusAppliance = Field(
        description="status of the appliance", validation_alias="Appliance")
    storage: StatusStorage = Field(
        description="status of the storage", validation_alias="Storage")
    system: StatusSystem = Field(
        description="status of the system", validation_alias="System")


class StatusHA(BaseModel):
    active: bool = Field(description="true if HA is enabled",
                         validation_alias="Active")
    cluster_status: str = Field(
        description="status message of cluster", validation_alias="ClusterStatus")


class StatusFull(BaseModel):
    status: Status = Field(description="status of the system")
    ha: StatusHA = Field(description="status of high availability")


class ComplianceRule(BaseModel):
    id: int = Field(description="ID of the compliance rule",
                    validation_alias="ID")
    policy_id: int = Field(
        description="ID of the compliance policy", validation_alias="PolicyID")
    name: str = Field(description="name of the compliance rule",
                      validation_alias="Name")
    type: str = Field(description="Type of the compliance rule",
                      validation_alias="Type")


class ComplianceResult(BaseModel):
    rule: ComplianceRule = Field(
        description="Compliance rule definition", validation_alias="Rule")
    policy_id: int = Field(
        description="ID of the compliance policy", validation_alias="PolicyID")
    tested: bool = Field(
        description="true if this rule was run", validation_alias="Tested")
    passed: bool = Field(
        description="true if this rule passed", validation_alias="Passed")
    alert: bool = Field(
        description="true if this rule triggers an alert", validation_alias="Alert")
    score: int = Field(
        description="score of the compliance policy", validation_alias="Score")
    fail_details: str = Field(
        description="text description of reason for failure", validation_alias="FailDetails")
    error: str = Field(description="any error text", validation_alias="Error")


class CompliancePolicy(BaseModel):
    id: int = Field(description="ID of the compliance policy",
                    validation_alias="ID")
    domain_id: int = Field(
        description="ID of the domain this compliance policy is for", validation_alias="DomainID")
    name: str = Field(
        description="name of the compliance policy", validation_alias="Name")
    device_ids: List[int] = Field(
        description="List of device IDs this policy is assigned to", validation_alias="DeviceIDs")


class Plugin(BaseModel):
    key: str = Field(description="plugin identifier", validation_alias="Key")
    name: str = Field(description="name of the plugin",
                      validation_alias="Name")
    manufacturer: str = Field(
        description="manufacturer the plugin applies to", validation_alias="Manufacturer")
    model: str = Field(
        description="device model the plugin applies to", validation_alias="Model")


class Domain(BaseModel):
    id: int = Field(description="ID of the domain", validation_alias="ID")
    name: str = Field(description="name of the domain",
                      validation_alias="Name")
    device_count: int = Field(
        description="number of devices in this domain", validation_alias="DeviceCount")
