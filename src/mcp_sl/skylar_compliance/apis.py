
"""
Skylar Compliance API Functions

This module contains all the API interaction functions for the Skylar Compliance MCP server.
These functions handle communication with the Skylar Compliance backend API and provide
MCP tools for device management, backup operations, logging, and system monitoring.

All functions are designed to work with the FastMCP framework and return properly
typed data models for consistent API responses.
"""

from typing import List, Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field
from mcp_sl.skylar_compliance import models
from mcp_sl.http_client import HTTPClient
from mcp_sl.config import get_config

http_client = HTTPClient(
    base_url=get_config().SKY_COMP_API_URL,
    headers={"Authorization": f"Custom {get_config().SKY_COMP_API_KEY}"}
)
sky_comp_mcp = FastMCP(name="Skylar Compliance sub MCP Server")


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_devices",
    description="Returns a list of devices",
    tags={"devices"},
)
async def list_devices(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Device]:
    params = {"limit": limit, "offset": offset,
              "fields": "ID,Name,ComplianceStatus,PluginName,State,Status"}
    json = await http_client.get("v2/devices", params=params)

    devices: List[models.Device] = [
        models.Device.model_validate(device)
        for device in json['data']
    ]
    envelope: models.ResponseEnvelope[models.Device] = models.ResponseEnvelope(
        results=devices,
        num_results=json['total'],
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_device_by_id",
    description="Returns a single of Skylar Compliance device",
    tags={"devices"},
)
async def get_device_by_id(
    device_id: Annotated[int, "ID of the device"]
) -> models.Device:
    json = await http_client.get(f"v2/devices/{device_id}")

    device: models.Device = models.Device.model_validate(json)
    return device


# searches through the SHA dict for one matching type and returns that SHA
def _find_sha(shas: List[dict[str, str]], backup_type: str) -> str:
    for sha in shas:
        if sha['ConfigType'] == backup_type:
            return sha['SHA256Sum']

@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_device_backups_by_type",
    description="Returns a history of backups for a Skylar Compliance device split out by config type",
    tags={"devices", "backup"},
)
async def list_device_backups_by_type(
    device_id: Annotated[int, "ID of the device"],
    limit: Annotated[Optional[int], Field(
        description="Number of backups to look through",
        gt=0)] = 100
) -> dict[str, List[models.BackupMetadataByConfigType]]:
    params = {"limit": limit, "offset": 0, "sort": "Created"}
    json = await http_client.get(f"v2/devices/{device_id}/backups", params=params)

    response: dict[str, List[models.BackupMetadataByConfigType]] = {}

    # loop over backups
    # sort into buckets by config type (multiple types can be present)
    # throw away entries that don't change from the last entry
    for backup in json['data']:
        for config_type in backup['ConfigurationTypes']:
            sha256 = _find_sha(backup['SHA256Sums'], config_type)
            # add entries for config types if they don't exist, add this entry as first
            if response.get(config_type) is None:
                response[config_type] = []
                response[config_type].append(
                    models.BackupMetadataByConfigType(
                        id=backup['ID'],
                        name=backup['Name'],
                        baseline=backup['IsBaseline'],
                        created=backup['Created'],
                        sha256=sha256
                    )
                )
            #otherwise, check if SHA256 changed from last entry
            elif sha256 != response[config_type][-1].sha256:
                response[config_type].append(
                    models.BackupMetadataByConfigType(
                        id=backup['ID'],
                        name=backup['Name'],
                        baseline=backup['IsBaseline'],
                        created=backup['Created'],
                        sha256=sha256
                    )
                )
    #dont wrap in envelope because num_results is meaningless here
    #reverse each list because we want the most recent change to show first
    for config_type, backups in response.items():
        backups.reverse()
    return response


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_device_backup_by_id",
    description="Returns a specific backup for a Skylar Compliance device",
    tags={"devices", "backup"},
)
async def get_device_backup_by_id(
    device_id: Annotated[int, "ID of the device"],
    backup_id: Annotated[int, "ID of the backup"]
) -> models.BackupMetadata:
    params = {"limit": 5, "offset": 0}
    json = await http_client.get(f"v2/devices/{device_id}/backups/{backup_id}", params=params)

    backup: models.BackupMetadata = models.BackupMetadata.model_validate(json)
    return backup


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_device_backup",
    description="Returns the lines for a specific backup for a Skylar Compliance device",
    tags={"devices", "backup"},
)
async def get_device_backup(
    device_id: Annotated[int, "ID of the device"],
    backup_id: Annotated[int, "ID of the backup"],
    backup_type: Annotated[str, "type of the backup"]
) -> models.Backup:
    params = {"limit": 100, "offset": 0}
    body = {
        "ConfigType": backup_type,
        "Location": "",
        "Search": ""
    }
    json = await http_client.post(
        f"v2/devices/{device_id}/backups/{backup_id}/config",
        params=params,
        json_data=body
    )

    backup: models.Backup = models.Backup.model_validate(json)
    return backup

@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}compare_backup",
    description="Compares the backups of two Skylar Compliance devices",
    tags={"devices", "backup"},
)
async def compare_backup(
    device1_id: Annotated[int, "ID of the first device"],
    backup1_id: Annotated[int, "ID of the first backup"],
    backup1_type: Annotated[str, "type of the first backup"],
    device2_id: Annotated[int, "ID of the second device"],
    backup2_id: Annotated[int, "ID of the second backup"],
    backup2_type: Annotated[str, "type of the second backup"]
) -> models.BackupDiff:
    data = {
        "Backups": [
            {
                "DeviceID": device1_id,
                "BackupID": backup1_id,
                "ConfigType": backup1_type
            },
            {
                "DeviceID": device2_id,
                "BackupID": backup2_id,
                "ConfigType": backup2_type
            }
        ],
        "OnlyDifferences": False,
        "HideIgnored": False,
        "Context": 3,
        "Offset": 0,
        "Limit": 200,
        "HTML": True
    }
    json = await http_client.post("v2/devices/backups/diff", json_data=data)
    backup: models.BackupDiff = models.BackupDiff.model_validate(json)
    return backup


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_agents",
    description="Returns a list of agents",
    tags={"agents"},
)
async def list_agents(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Agent]:
    params = {"limit": limit, "offset": offset}
    json = await http_client.get("v2/devices", params=params)

    agents: List[models.Agent] = [
        models.Agent.model_validate(agent)
        for agent in json['data']
    ]
    envelope: models.ResponseEnvelope[models.Agent] = models.ResponseEnvelope(
        results=agents,
        num_results=json['total']
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_jobs",
    description="Returns a list of currently running Skylar Compliance jobs",
    tags={"jobs"},
)
async def list_jobs(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Job]:
    params = {"limit": limit, "offset": offset, "fields": ""}
    json = await http_client.get("v2/jobs", params=params)

    jobs = [
        models.Job.model_validate(job)
        for job in json['data']
    ]
    envelope = models.ResponseEnvelope(
        results=jobs,
        num_results=json['total']
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_job_by_id",
    description="Returns a list of currently running Skylar Compliance jobs",
    tags={"jobs"},
)
async def get_job_by_id(
    job_id: Annotated[int, "ID of the job to return"]
) -> models.Job:
    json = await http_client.get(f"v2/jobs/{job_id}")

    job = models.Job.model_validate(json)
    return job


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_historic_jobs",
    description="Returns a list of historic Skylar Compliance jobs",
    tags={"jobs"},
)
async def list_historic_jobs(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Job]:
    params = {"limit": limit, "offset": offset, "fields": ""}
    json = await http_client.get("v2/jobs/historic", params=params)

    jobs = [
        models.Job.model_validate(job)
        for job in json['data']
    ]
    envelope = models.ResponseEnvelope(
        results=jobs,
        num_results=json['total']
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_logs",
    description="Returns system logs",
    tags={"logs"},
)
async def list_logs(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Log]:
    params = {"limit": limit, "offset": offset,
              "fields": "", "sort": "Created"}
    json = await http_client.get("v2/logs", params=params)

    logs = [
        models.Log.model_validate(log)
        for log in json['data']
    ]
    envelope = models.ResponseEnvelope(
        results=logs,
        num_results=json['total']
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}status",
    description="Returns the status of system components",
    tags={"health"},
)
async def system_status() -> models.StatusFull:

    json = await http_client.get("v2/status")
    status = models.Status.model_validate(json)

    json = await http_client.get("v2/settings/ha/status")
    status_ha = models.StatusHA.model_validate(json)

    return models.StatusFull(status=status, ha=status_ha)


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_device_compliance_results",
    description="Test a Skylar Compliance device against it's compliance rules",
    tags={"devices", "compliance"},
)
async def get_device_compliance_results(
    device_id: Annotated[int, "ID of the device"]
) -> List[models.ComplianceResult]:
    json = await http_client.get(f"v2/devices/{device_id}/compliance")

    compliance_results = [
        models.ComplianceResult.model_validate(result)
        for result in json['Results']
    ]
    return compliance_results


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_compliance_policies",
    description="Returns a list of compliance policies",
    tags={"policies"},
)
async def list_compliance_policies(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.CompliancePolicy]:
    params = {"limit": limit, "offset": offset}
    json = await http_client.get("v2/policies", params=params)

    policies = [
        models.CompliancePolicy.model_validate(policy)
        for policy in json['data']
    ]
    envelope = models.ResponseEnvelope(
        results=policies,
        num_results=json['total']
    )
    return envelope


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}get_compliance_policy_by_id",
    description="Returns a list of compliance policies",
    tags={"policies"},
)
async def get_compliance_policy_by_id(
    policy_id: Annotated[int, "ID of the policy"]
) -> models.CompliancePolicy:
    json = await http_client.get(f"v2/policies/{policy_id}")

    policy = models.CompliancePolicy.model_validate(json)
    return policy


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_plugins",
    description="Returns a list of plugins",
    tags={"plugins"},
)
async def list_plugins(
) -> List[models.Plugin]:
    params = {"field": "Key,Name,Manufacturer,Model"}
    json = await http_client.get("v2/plugins", params=params)

    plugins = [
        models.Plugin.model_validate(plugin)
        for plugin in json['data']
    ]
    return plugins


@sky_comp_mcp.tool(
    name=f"{get_config().SKY_COMP_PREFIX}list_domains",
    description="Returns a list of domains",
    tags={"domains"},
)
async def list_domains(
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    offset: Annotated[Optional[int],
                      "Number of results to skip for pagination"] = 0
) -> models.ResponseEnvelope[models.Domain]:
    params = {"limit": limit, "offset": offset,
              "fields": "ID,Name,DeviceCount"}
    json = await http_client.get("v2/domains", params=params)

    domains = [
        models.Domain.model_validate(domain)
        for domain in json['data']
    ]
    envelope = models.ResponseEnvelope(
        results=domains,
        num_results=json['total']
    )
    return envelope
