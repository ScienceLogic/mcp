# ScienceLogic MCP

A FastMCP server that provides AI agents with access to ScienceLogic products through API integration.

## Supported Products

* Skylar One - `/sky_one/mcp`
* Skylar Compliance - `/sky_comp/mcp`

## Quick Start

### Prerequisites

- Docker
- API credentials for your ScienceLogic products

### Running the Server

```
docker run --rm -p 8000:8000 \
-e SKY_COMP_API_URL=https://changeme/api/ \
-e SKY_COMP_API_KEY=changeme \
-e SKY_ONE_API_URL=https://changeme/ \
-e SKY_ONE_API_KEY=changeme \
calebburch199/sciencelogic-mcp:latest
```

# Example Usage

Connect your AI agent to the MCP server, by default will run at:
* `http://localhost:8000/sky_one/mcp`
* `http://localhost:8000/sky_comp/mcp`

Ask your AI assissant to:
* Return a list of devices with a critical status
* Find what recent events need your attention
* Compare two backups of a device to determine differences
* Determine the current state of your appliances

# Running

## Dockerhub image

```
docker run --rm -p 8000:8000 \
-e SKY_COMP_API_URL=https://changeme/api/ \
-e SKY_COMP_API_KEY=changeme \
-e SKY_ONE_API_URL=https://changeme/ \
-e SKY_ONE_API_KEY=changeme \
calebburch199/sciencelogic-mcp:latest
```

## Build Docker image from Source

```
docker build -t mcp-sl:latest --platform linux/amd64 .

docker run --rm -p 8000:8000 \
-e SKY_COMP_API_URL=https://changeme/api/ \
-e SKY_COMP_API_KEY=changeme \
-e SKY_ONE_API_URL=https://changeme/ \
-e SKY_ONE_API_KEY=changeme \
mcp-sl:latest

```

## Run python locally

```
cp .env .myenv
# update configuration file
vi .myenv
uv run --env-file .myenv uvicorn mcp_sl.server:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 5
```

# Configuration

| ENV VAR                   | Description 
| ------------------------- | ----------------------
| `SKY_COMP_ENABLE` | (Optional, default=true) enables the Skylar Compliance MCP server, requires SKY_COMP_API_URL and SKY_COMP_API_KEY to be set
| `SKY_COMP_API_URL`              | (Required) API endpoint for your Skylar Compliance instance e.g. `https://rp42.rp.internal/api/` (requires trailing slash)
| `SKY_COMP_API_KEY`              | (Required) API Key used to auth your API instance
| `SKY_COMP_PREFIX` | (Optional, default="/sc_") Prefixes every tool, helpful for tool name collisions
| `SKY_ONE_ENABLE` | (Optional, default=true) enables the Skylar One MCP server, requires SKY_ONE_API_URL and SKY_ONE_API_KEY 
| `SKY_ONE_API_URL`              | (Required) API endpoint for your Skylar One instance e.g. `https://my.sl1.host/api/` (requires trailing slash)
| `SKY_ONE_API_KEY`              | (Required) API Key used to auth your API instance, Base64 encoded 'user:pass'
| `SKY_ONE_PREFIX` | (Optional, default="/s1_") Prefixes every tool, helpful for tool name collisions
| `MAX_QUERY_LIMIT` | (Optional, default=50) limits the maximum number of results an agent can request (to prevent overloading API endpoints)
| `LOG_LEVEL`               | (Optional, default=INFO) set the app log level (uvicorn will ignore it currently)
| `TOOL_TIMEOUT_MS`         | (Optional, default=10000) number of MS to wait for an API call to return from RP
| `SUPPORT_ELICITATION`     | (Required, default=true) set to true if you want the MCP server to request additional information on non-READ API calls.

# TOOLS

## Skylar Compliance MCP Server

| Tool Name | Description | API Endpoint(s)
| - | - | -
| `list_devices` | Returns a list of device details | [GET /devices](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_devices)
| `get_device_by_id` | Returns a device by ID | [GET /devices/{id}](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/get_device)
| `list_device_backups_by_type` | Returns a history of backups for a Skylar Compliance device split out by config type | [GET /devices/{id}/backups](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_device_backups)
| `get_device_backup_by_id` | Returns a device backup by id | [GET /devices/{id}/backups/{backup_id}](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/get_backup)
| `get_device_backup` | Returns the lines of a backup | [POST /devices/{id}/backups/{backup_id}/config](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/config_details)
| `compare_backup` | Shows the difference between two backups | [POST /devices/backups/diff](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/diff_backup)
| `list_agents` | Returns a list of agents | [GET /agents](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_agents)
| `list_jobs` | Returns a list of any running jobs | [GET /jobs](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_jobs)
| `get_job_by_id` | Returns a job by id | [GET /jobs/{id}](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/get_job)
| `list_historic_jobs` | Returns a list of any historic jobs | [GET /jobs/historic](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_historic_jobs)
| `list_logs` | Returns system logs | [GET /logs](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_logs)
| `status` | Returns the health and HA status of the appliance | [GET /status](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/system_status) <br> [GET /settings/ha/status](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/get_high_availability_status) 
| `list_compliance_policies` | Returns a list of compliance policies | [GET /policies](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/list_policies)
| `get_compliance_policy_by_id` | Returns a compliancy policy by id | [GET /policies/{id}](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/get_policy)
| `get_device_compliance_results` | Returns the results of a device's compliance test | [GET /devices/{id}/compliance](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#operation/device_compliance)
| `list_plugins` | Returns a list of device plugins | [GET /plugins](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#tag/Plugin)
| `list_domains` | Returns a list of domains | [GET /domains](https://docs.sciencelogic.com/restorepoint/api/5-6/api.html#tag/Domain)

## Skylar One MCP Server

| Tool Name | Description | GQL Endpoint(s)
| - | - |  -
| `list_devices` | Returns a list of device details | devices
| `get_asset_by_device_id` | Returns assets for a device | assets
| `list_events` | Returns a list of events, sorted by most recent | events
| `list_business_services` | Returns a list of business services | harProviders
| `get_appliance_status` | Returns a list of appliances and their status | appliances

# Testing

```
uv run pytest
```

# Security

- Uses API token authentication
- All requests proxy through configured API endpoints
- Not recommended for public networks
- Access to this server grants access to your ScienceLogic appliances

# License

Licensed under Apache 2.0 - see [LICENSE](LICENSE) file.  This is not an official ScienceLogic product.