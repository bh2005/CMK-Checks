WHITEPAPAER

Integration for Solarwinds  
  
The integration of ExtremeCloud IQ into SolarWinds can be done in
various ways. However, since SolarWinds NPM (Network Performance
Monitor) explicitly supports monitoring Extreme Networks devices via the
ExtremeCloud IQ API , the best approach is to use this integrated
functionality instead of writing a completely custom plugin.

Here\'s a summary of how to integrate ExtremeCloud IQ into SolarWinds
NPM:

**1. Prerequisites:**

- You need a SolarWinds NPM system.

- You need ExtremeCloud IQ credentials (username and password for the
  orchestrator node).

- **Ensure that Extreme Networks\' API request limits** (up to 7500 API/h
  requests per customer) are considered.

**2. Integration in SolarWinds NPM:**

- **Log in to the SolarWinds Platform Web Console:** Log in as an
  administrator.

- **Add a Node:** Go to *Settings \> Manage Nodes* and click *Add a
  Node*.

- **Select Polling Method:** Under *Polling Method*, select the
  *Orchestrators: API* option.

- **Select ExtremeCloud IQ:** Choose *ExtremeCloud IQ Devices*.

- **Enter Credentials:** Enter the username and password for the
  ExtremeCloud IQ orchestrator node.

- **Proxy Settings (if required):** Check and adjust the proxy settings
  if your network uses a proxy.

- **Verify and Adjust Device Properties:** Check the device properties
  and adjust them as needed.

- **Verify Credentials and Proxy Settings:** Ensure all information is
  correct.

**Important Notes from SolarWinds Documentation and Forums:**

- **No Discovery Support:** Automatic device discovery via the
  ExtremeCloud IQ API is not supported in SolarWinds NPM. You must add
  nodes manually.

- **No \"Poll Now\" Support:** The \"Poll Now\" function is also not
  supported.

- **Adjusting Response Time Thresholds:** Nodes may show warning or
  critical states even if there are no connectivity problems (0% packet
  loss). In this case, you should adjust the response time thresholds.

- **API Calls:** SolarWinds NPM uses various API calls to retrieve data
  from ExtremeCloud IQ, including authentication, status polling,
  retrieving wireless interface information, and client data.

**Advantages of this Method:**

- **Official Support:** This is a SolarWinds-supported integration.

- **Simple Configuration:** Configuration is done directly in the
  SolarWinds NPM Web Console.

- **No Additional Scripts or Plugins Required:** You don\'t need to
  write or install custom scripts or plugins.

**Disadvantages:**

- **Manual Node Discovery:** Manual node discovery can be time-consuming
  for a large number of devices.

- **Limited Customization Options:** You have fewer customization
  options compared to a custom-written plugin.

**In Summary:**

For integrating ExtremeCloud IQ into SolarWinds NPM, the easiest and
most recommended approach is to use the built-in functionality within
SolarWinds NPM. This provides a direct connection via the ExtremeCloud
IQ API and does not require additional scripts or plugins. However, be
aware of the limitations regarding automatic discovery and the \"Poll
Now\" function.

If you need specific data not covered by the standard integration, or if
you are using other SolarWinds products that do not offer direct support
for ExtremeCloud IQ, you may need to consider alternative methods such
as the Orion SDK, SNMP, or Syslog
