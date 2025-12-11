
"""
Skylar One API Functions

This module contains all the API interaction functions for the Skylar One MCP server.
These functions handle communication with the Skylar One backend API.

All functions are designed to work with the FastMCP framework and return properly
typed data models for consistent API responses.
"""
import logging
from typing import List, Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field
from mcp_sl.config import get_config
from mcp_sl.skylar_one import models
from mcp_sl.http_client import HTTPClient

logger = logging.getLogger()

http_client = HTTPClient(
    base_url=get_config().SKY_ONE_API_URL,
    headers={"Authorization": f"Basic {get_config().SKY_ONE_API_KEY}",
             "Content-Type": "application/json"}
)
sky_one_mcp = FastMCP(name="Skylar One sub MCP Server")

_SEVERITIES = ("Notice", "Healthy", "Minor", "Major", "Critical")


def _build_event_search_filter(device_id: int = None, severity_level: int = None) -> str:
    if not device_id and not severity_level:
        return "{ }"

    search_string = "{ and: ["
    if device_id:
        search_string += f'{{alignedEntityId: {{ eq: {device_id} }} }},'
    if severity_level:
        selected_severities = _SEVERITIES[severity_level - 1:]
        severity_list = '", "'.join(selected_severities)
        search_string += f'{{severityLevel:{{ in: ["{severity_list}"] }} }},'
    search_string += " ] }"
    return search_string


def _build_device_search(device_id: int = None, severity_level: int = None, device_class: str = None, collector_group_name: str = None) -> str:
    if not device_id and not severity_level and not device_class and not collector_group_name:
        return "{ }"

    search_string = "{ and: ["
    if device_id:
        search_string += f'\n{{id: {{ eq: {device_id} }} }},'
    if severity_level:
        selected_severities = _SEVERITIES[severity_level - 1:]
        severity_list = '", "'.join(selected_severities)
        search_string += f'\n{{severityLevel:{{ in: ["{severity_list}"] }} }},'
    if device_class:
        search_string += f'\n{{deviceClass: {{ has: {{ class: {{ eq: "{device_class}" }} }} }} }},'
    if collector_group_name:
        search_string += f'\n{{collectorGroup: {{ has: {{ name: {{ eq: "{collector_group_name}" }} }} }} }},'
    search_string += "\n ] }"
    return search_string


# TODO refactor this into a better search generation function
def _build_business_service_search(
    risk_level: Optional[int] = None,
    health_level: Optional[int] = None,
    unavailable_only: bool = False,
    name_contains: Optional[str] = None
) -> str:
    if not risk_level and not health_level and not unavailable_only and not name_contains:
        return "{ }"
    search_string = "{ and: ["

    if risk_level:
        risk_value: int = 0
        if risk_level == 1:
            risk_value = 0
        elif risk_level == 2:
            risk_value = 21
        elif risk_level == 3:
            risk_value = 41
        elif risk_level == 4:
            risk_value = 61
        else:
            risk_value = 81
        search_string += f'{{risk: {{ gt: {risk_value} }} }}, '

    if health_level:
        health_value: int = 0
        if health_level == 1:
            health_value = 101
        elif health_level == 2:
            health_value = 81
        elif health_level == 3:
            health_value = 61
        elif health_level == 4:
            health_value = 41
        else:
            health_value = 21
        search_string += f'{{ health: {{ lt: {health_value} }} }}, '

    if unavailable_only:
        search_string += '{{ availability: {{ lte: 0 }} }}, '

    if name_contains:
        search_string += f'{{ name: {{ contains: "{name_contains}" }} }}, '

    search_string += " ] }"
    return search_string


@sky_one_mcp.tool(
    name=f"{get_config().SKY_ONE_PREFIX}list_devices",
    description="Returns a list of Skylar One devices, You can provide an optional device id to filter events to.  You can provide an optional severity level filter that will return events at that severity or greater.  Severities are from 1 to 5, with 5 being the worst.  You can also pass in optional device_ids, collector_name, and device class to further filter results.",
    tags={"devices"},
)
async def list_devices(
    device_id: Annotated[Optional[int], Field(
        description="ID of device to return")] = None,
    severity_level: Annotated[Optional[int], Field(
        description="minimum severity level of devices to return (from 1 to 5)", ge=1, le=5)] = None,
    device_class:  Annotated[Optional[str], Field(
        description="Name of device class of devices to filter to")] = None,
    collector_group_name: Annotated[Optional[str], Field(
        description="Name of collector group to return devices of")] = None,
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    cursor: Annotated[Optional[str],
                      "Cursor of the last device to start from (will return next device), get the cursor from a previous request"] = ""
) -> models.ResponseEnvelope[models.DeviceGQL]:
    search = _build_device_search(
        device_id, severity_level, device_class, collector_group_name)
    body = {
        "query": f"""
            query list_devices {{
                devices(
                    first: {limit},
                    after: "{cursor}",
                    search: {search}
                ) {{
                    edges {{
                        node {{
                            id
                            name
                            organization {{
                                id
                            }}
                            active	{{
                                maintenance
                                systemDisabled
                                unavailable
                                userDisabled
                                userInitiatedMaintenance
                            }}
                            collectorGroup {{
                                id
                                name
                            }}
                            dateCreated
                            deviceClass {{
                                id
                                class
                                description
                                deviceCategory {{
                                    name
                                }}
                                logicalName
                                virtualType
                            }}
                            severityLevel
                        }}
                        cursor
                    }}
                    pageInfo {{
                        matchCount
                    }}
                }}
            }}
        """,
        "operationName": "list_devices"
    }
    json = await http_client.post("gql", json_data=body)

    devices: List[models.DeviceGQL] = [
        models.DeviceGQL.model_validate(device)
        for device in json['data']['devices']['edges']
    ]
    envelope: models.ResponseEnvelope[models.DeviceGQL] = models.ResponseEnvelope(
        results=devices,
        num_results=json['data']['devices']['pageInfo']['matchCount'],
        cursor=json['data']['devices']['edges'][-1]['cursor'] if json['data']['devices']['edges'] else None
    )

    return envelope


@sky_one_mcp.tool(
    name=f"{get_config().SKY_ONE_PREFIX}list_events",
    description="Returns a list of Skylar One events.  You can provide an optional device id to filter events to.  You can provide an optional severity level filter that will return events at that severity or greater.  Severities are from 1 to 5, with 5 being the worst.",
    tags={"events"},
)
async def list_events(
    device_id: Annotated[Optional[int], "Optional ID of the device"] = None,
    severity_level: Annotated[Optional[int], Field(
        description="minimum severity level of events to return (from 1 to 5)", ge=1, le=5)] = None,
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    cursor: Annotated[Optional[str],
                      "Cursor of the last event to start from (will return next device), get the cursor from a previous request"] = "",
) -> models.ResponseEnvelope[models.EventGQL]:
    search = _build_event_search_filter(device_id, severity_level)
    body = {
        "query": f"""
            query list_events {{
                events(
                    first: {limit},
                    after: "{cursor}",
                    order: {{field:"dateFirst", direction: desc}},
                    search: {search}
                ) {{
                    edges {{
                        node {{
                            id
                            dateFirst
                            counter
                            message
                            organization {{
                                id
                            }}
                            alignedEntity {{
                                __typename
                            }}
                            alignedResourceName
                            source {{
                                id
                                name
                            }}
                            severityLevel
                            subtype
                        }}
                        cursor
                    }}
                    pageInfo {{
                        matchCount
                    }}
                }}
            }}
        """,
        "operationName": "list_events"
    }
    json = await http_client.post("gql", json_data=body)

    events: List[models.EventGQL] = [
        models.EventGQL.model_validate(event)
        for event in json['data']['events']['edges']
    ]
    envelope: models.ResponseEnvelope[models.EventGQL] = models.ResponseEnvelope(
        results=events,
        num_results=json['data']['events']['pageInfo']['matchCount'],
        cursor=json['data']['events']['edges'][-1]['cursor'] if json['data']['events']['edges'] else None
    )
    return envelope


@sky_one_mcp.tool(
    name=f"{get_config().SKY_ONE_PREFIX}get_asset_by_device_id",
    description="Returns a list of Skylar One assets",
    tags={"assets"},
)
async def get_asset_by_device_id(
    device_id: Annotated[int, "ID of the device to retrieve assets from"]
) -> models.ResponseEnvelope[models.AssetGQL]:
    body = {
        "query": f"""
            query get_asset_by_device_id {{
                assets(search: {{ device: {{ has: {{ id: {{ eq: {device_id} }} }} }} }}) {{
                    edges {{
                        node {{
                            id
                            floor
                            function
                            location
                            make
                            model
                            modelNumber
                            status
                            type
                        }}
                        cursor
                    }}
                    pageInfo {{
                        matchCount
                    }}
                }}
            }}
        """,
        "operationName": "get_asset_by_device_id"
    }
    json = await http_client.post("gql", json_data=body)

    assets: List[models.AssetGQL] = [
        models.AssetGQL.model_validate(asset)
        for asset in json['data']['assets']['edges']
    ]
    envelope: models.ResponseEnvelope[models.AssetGQL] = models.ResponseEnvelope(
        results=assets,
        num_results=json['data']['assets']['pageInfo']['matchCount'],
        cursor=json['data']['assets']['edges'][-1]['cursor'] if json['data']['assets']['edges'] else None
    )
    return envelope


@sky_one_mcp.tool(
    name=f"{get_config().SKY_ONE_PREFIX}list_business_services",
    description="Returns a list of Skylar One business services",
    tags={"business_services"},
)
async def list_business_services(
    risk_level: Annotated[Optional[int], Field(
        description="Number of the minimal risk level to return (1-5), 1 being the least risky. Returns everything above this level"
    )] = None,
    health_level: Annotated[Optional[int], Field(
        description="Number of the minimal health level to return (1-5), 1 being the most healthy. Returns everything above this level"
    )] = None,
    unavailable_only: Annotated[Optional[bool], Field(
        description="True to only return unavailable business services, false will return all"
    )] = False,
    limit: Annotated[Optional[int], Field(
        description="Number of results to return for pagination",
        gt=0,
        le=get_config().MAX_QUERY_LIMIT)] = 10,
    name_contains: Annotated[Optional[str], Field(
        description="Name of the business service to filter by, will do a contains search"
    )] = None,
    cursor: Annotated[Optional[str],
                      "Cursor of the last business service to start from (will return next device), get the cursor from a previous request"] = ""
) -> models.ResponseEnvelope[models.BusinessServiceGQL]:
    search = _build_business_service_search(
        risk_level, health_level, unavailable_only, name_contains)
    logger.debug("BizSvc search query: %s", search)
    body = {
        "query": f"""
            query list_business_services {{
                harProviders(
                first: {limit},
                after: "{cursor}",
                search: {search}
                ) {{
                    edges {{
                        node {{
                            id
                            name
                            organization {{
                                id
                            }}
                            availability
                            health
                            risk
                            collectionTime
                            constituentIds
                            dateCreated
                            description
                            enabled
                        }}
                        cursor
                    }}
                    pageInfo {{
                        matchCount
                    }}
                }}
            }}
        """,
        "operationName": "list_business_services"
    }
    json = await http_client.post("gql", json_data=body)

    services: List[models.BusinessServiceGQL] = [
        models.BusinessServiceGQL.model_validate(service)
        for service in json['data']['harProviders']['edges']
    ]
    envelope: models.ResponseEnvelope[models.BusinessServiceGQL] = models.ResponseEnvelope(
        results=services,
        num_results=json['data']['harProviders']['pageInfo']['matchCount'],
        cursor=json['data']['harProviders']['edges'][-1]['cursor'] if json['data']['harProviders']['edges'] else None
    )
    return envelope


@sky_one_mcp.tool(
    name=f"{get_config().SKY_ONE_PREFIX}get_appliance_status",
    description="Returns a list of Skylar One appliances and their status",
    tags={"health"},
)
async def get_appliance_status() -> models.ResponseEnvelope[models.Appliance]:
    body = {
        "query": """
            query get_appliances {
                appliances(
                    search: { type: { notIn: ["CU", "MC"] } }
                ) {
                    edges {
                        node {
                            id
                            dateEdited
                            dateCreated
                            databaseVersion
                            description
                            name        
                            expiration
                            capacity
                            highAvailabilityStatus
                            releaseVersion
                            type
                            operatingSystemVersion
                            needsReboot
                            licenseType
                            licenseStatus
                            ip
                            status
                            taskManagerPaused
                        }
                        cursor
                    }
                    pageInfo {
                        matchCount
                    }
                }
            }
        """,
        "operationName": "get_appliances"
    }
    json = await http_client.post("gql", json_data=body)
    appliances: List[models.Appliance] = [
        models.Appliance.model_validate(appliance)
        for appliance in json['data']['appliances']['edges']
    ]
    envelope: models.ResponseEnvelope[models.Appliance] = models.ResponseEnvelope(
        results=appliances,
        num_results=json['data']['appliances']['pageInfo']['matchCount'],
        cursor=json['data']['appliances']['edges'][-1]['cursor'] if json['data']['appliances']['edges'] else None
    )
    return envelope
