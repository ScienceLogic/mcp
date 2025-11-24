
"""
SL1 Data Models

This module defines all Pydantic data models used throughout the SL1 MCP server.
These models provide type safety, data validation, and automatic serialization/deserialization
for API responses and internal data structures.

All models use Pydantic's Field with aliases to map between the API's naming convention
(PascalCase - Golang) and Python's naming convention (snake_case).
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import AliasChoices, AliasPath, BaseModel, Field, field_validator

T = TypeVar('T')

class ResponseEnvelope(BaseModel, Generic[T]):
    results: List[T] = Field(description="List of response objects")
    num_results: int = Field(description="Total number of results possible based on the query")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination to fetch next set of results")

def strip_id(value: str) -> int:
    return int(value.split("/")[-1])

class Appliance(BaseModel):
    id: int = Field(description="ID of the appliance", validation_alias=AliasPath("node", "id"))
    date_created: int = Field(description="Epoch time this appliance was created", validation_alias=AliasPath("node", "dateCreated"))
    date_edited: int = Field(description="Epoch time this appliance was edited", validation_alias=AliasPath("node", "dateEdited"))
    name: str = Field(description="Display name of the appliance", validation_alias=AliasPath("node", "name"))
    description: Optional[str] = Field(description="Description of the appliance", validation_alias=AliasPath("node", "description"))
    database_version: str = Field(description="version of the database", validation_alias=AliasPath("node", "databaseVersion"))
    capacity: int = Field(description="Number of devices this appliance has been licensed to monitor", validation_alias=AliasPath("node", "capacity"))
    expiration: int = Field(description="Epoch time this appliance license expires", validation_alias=AliasPath("node", "expiration"))
    ha_status: bool = Field(description="True if this appliance is part of a highly available infrastructure setup", validation_alias=AliasPath("node", "highAvailabilityStatus"))
    release_version: str = Field(description="Version of the appliance", validation_alias=AliasPath("node", "releaseVersion"))
    type: str = Field(description="Type of this appliance", validation_alias=AliasPath("node", "type"))
    os_version: str = Field(description="Version of the operating system", validation_alias=AliasPath("node", "operatingSystemVersion"))
    needs_reboot: bool = Field(description="True if this device needs rebooted", validation_alias=AliasPath("node", "needsReboot"))
    license_type: str = Field(description="Type of license", validation_alias=AliasPath("node", "licenseType"))
    license_status: str = Field(description="Status of the license", validation_alias=AliasPath("node", "licenseStatus"))
    ip: str = Field(description="IP address of this appliance", validation_alias=AliasPath("node", "ip"))
    status: str = Field(description="Status of this appliance", validation_alias=AliasPath("node", "status"))
    task_manager_paused: bool = Field(description="True if this appliance's task manager is paused", validation_alias=AliasPath("node", "taskManagerPaused"))

class DeviceGQL(BaseModel):
    id: int = Field(description="ID of the device", validation_alias=AliasPath("node", "id"))
    name: str = Field(description="Display name of the device", validation_alias=AliasPath("node", "name"))
    organization: int = Field(description="ID of the org this event is aligned to", validation_alias=AliasPath("node", "organization", "id"))
    active_maintenance: bool = Field(description="True if device is in maintenance mode", validation_alias=AliasPath("node", "active", "maintenance"))
    active_system_disabled: bool = Field(description="True if device is in system disabled mode", validation_alias=AliasPath("node", "active", "systemDisabled"))
    active_unavailable: bool = Field(description="True if device is in unavailable mode", validation_alias=AliasPath("node", "active", "unavailable"))
    active_user_disabled: bool = Field(description="True if device is in user disabled mode", validation_alias=AliasPath("node", "active", "userDisabled"))
    active_user_initiated_maintenance: bool = Field(description="True if device is in user initiated maintenance mode", validation_alias=AliasPath("node", "active", "userInitiatedMaintenance"))
    collector_group: str = Field(description="Name of the collector group this device is aligned to", validation_alias=AliasPath("node", "collectorGroup", "name"))
    date_created: int = Field(description="Epoch time this device was created", validation_alias=AliasPath("node", "dateCreated"))
    device_class: str = Field(description="Class of this device", validation_alias=AliasPath("node", "deviceClass", "class"))
    device_class_id: str = Field(description="ID of the device class this device belongs to", validation_alias=AliasPath("node", "deviceClass", "id"))
    device_class_description: str = Field(description="Description of this device class", validation_alias=AliasPath("node", "deviceClass", "description"))
    device_class_logical_name: str = Field(description="Logical name of this device class", validation_alias=AliasPath("node", "deviceClass", "logicalName"))
    device_class_category: str = Field(description="Category of this device class", validation_alias=AliasPath("node", "deviceClass", "deviceCategory", "name"))
    device_class_virtual_type: str = Field(description="Virtual Type of this device class (physical, virtual, or component)", validation_alias=AliasPath("node", "deviceClass", "virtualType"))
    severity_level: str = Field(description="Current health of the device", validation_alias=AliasPath("node", "severityLevel"))

class EventGQL(BaseModel):
    id: int = Field(description="ID of the event", validation_alias=AliasPath("node", "id"))
    date_first: int = Field(description="Epoch time this event first occurred", validation_alias=AliasPath("node", "dateFirst"))
    counter: int = Field(description="Number of occurrences of this event", validation_alias=AliasPath("node", "counter"))
    entity_name: str = Field(description="Name of the entity this event applies to", validation_alias=AliasPath("node", "alignedResourceName"))
    entity_type: str = Field(description="Name of the type of entity this event is aligned to (0=Organization, 1=Device)", validation_alias=AliasPath("node", "alignedEntity", "__typename"))
    entity_subtype: Optional[str] = Field(default=None, description="Name of the type of subentity this event is aligned to (0=Organization, 1=Device)", validation_alias=AliasChoices(
        AliasPath("node", "alignedSubEntity", "__typename"),
        AliasPath("node", "alignedSubEntity")
    ))
    message: str = Field(description="Text of this event", validation_alias=AliasPath("node", "message"))
    organization: int = Field(description="ID of the org this event is aligned to", validation_alias=AliasPath("node", "organization", "id"))
    type: str = Field(description="Name of the type of this event (esource)", validation_alias=AliasPath("node", "source", "name"))
    subtype: Optional[str] = Field(default=None, description="Name of the subtype of this event", validation_alias=AliasPath("node", "subtype"))
    severity_level: str = Field(description="Severity level of this event from Notice, Healthy, Minor, Major, Critical", validation_alias=AliasPath("node", "severityLevel"))

class AssetGQL(BaseModel):
    id: int = Field(description="ID of the asset", validation_alias=AliasPath("node", "id"))
    floor: str = Field(description="Floor this asset is located on", validation_alias=AliasPath("node", "floor"))
    function: str = Field(description="Function of this asset", validation_alias=AliasPath("node", "function"))
    location: str = Field(description="Location of this asset", validation_alias=AliasPath("node", "location"))
    make: str = Field(description="Make of this asset", validation_alias=AliasPath("node", "make"))
    model: str = Field(description="Model of this asset", validation_alias=AliasPath("node", "model"))
    model_number: str = Field(description="Model number of this asset", validation_alias=AliasPath("node", "modelNumber"))
    status: str = Field(description="Status of this asset", validation_alias=AliasPath("node", "status"))
    type: str = Field(description="Type of this asset", validation_alias=AliasPath("node", "type"))


class BusinessServiceGQL(BaseModel):
    id: str = Field(description="ID of the business service", validation_alias=AliasPath("node", "id"))
    name: str = Field(description="Display name of the business service", validation_alias=AliasPath("node", "name"))
    description: Optional[str] = Field(description="Description of the business service", validation_alias=AliasPath("node", "description"))
    organization: int = Field(description="ID of the org this event is aligned to", validation_alias=AliasPath("node", "organization", "id"))
    date_created: int = Field(description="Epoch time this business service was created", validation_alias=AliasPath("node", "dateCreated"))
    availability: Optional[str] = Field(description="Latest availability status", validation_alias=AliasPath("node", "availability"))
    health: Optional[str] = Field(default=None, description="Latest health score as text label", validation_alias=AliasPath("node", "health"))
    risk: Optional[str] = Field(default=None, description="Latest risk level", validation_alias=AliasPath("node", "risk"))
    collection_time: Optional[int] = Field(default=None, description="Epoch time when the latest health, availability, risk scores were calculated", validation_alias=AliasPath("node", "collectionTime"))
    enabled: bool = Field(description="True if this business service is enabled", validation_alias=AliasPath("node", "enabled"))
    constituent_ids: List[str] = Field(description="A list of IDs of the children of this service", validation_alias=AliasPath("node", "constituentIds"))

    @field_validator('health', mode='before')
    @classmethod
    def transform_health_score(cls, v):
        if v is None:
            return "Unknown"

        # Convert numeric health score to string label
        if isinstance(v, (int, float)):
            if v > 80:
                return "Healthy"
            elif v > 60:
                return "Notice"
            elif v > 40:
                return "Minor"
            elif v > 20:
                return "Major"
            else:
                return "Critical"

        # If it's already a string, return as-is
        return v

    @field_validator('risk', mode='before')
    @classmethod
    def transform_risk_score(cls, v):
        if v is None:
            return "Unknown"

        # Convert numeric risk score to string label
        if isinstance(v, (int, float)):
            if v > 80:
                return "Very High"
            elif v > 60:
                return "High"
            elif v > 40:
                return "Medium"
            elif v > 20:
                return "Low"
            else:
                return "No Risk"

        # If it's already a string, return as-is
        return v

    @field_validator('availability', mode='before')
    @classmethod
    def transform_availability_score(cls, v):
        if v is None:
            return "Unknown"

        # Convert numeric availability score to string label
        if isinstance(v, (int, float)):
            if v > 0:
                return "Available"
            else:
                return "Unavailable"

        # If it's already a string, return as-is
        return v
