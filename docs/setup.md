# Set up the PTU workbook

This workbook shows the Foundry account and deployment behind each APIM
subscription and estimates that subscription's share of PTU use. **Validate the
results in your environment before operational or financial use.**

**You need:** the accompanying
[`PTU-usage-by-APIM-subscription.workbook.json`](../workbooks/PTU-usage-by-APIM-subscription.workbook.json)
file, an Azure sign-in, and the names of the APIM instance, Log Analytics
workspace, and Foundry accounts to view. You select those resources in the
portal; you do not need to type their resource IDs or run a script.

Ask your Azure administrator to confirm that you have:

- **Log Analytics Reader** on the workspace and read access to each APIM
  instance and Foundry account, including its deployments and metrics.
- Permission to save a workbook in the chosen resource group, such as
  **Monitoring Contributor**. Other viewers need read access to the saved
  workbook and the same underlying data.

## 1. Check APIM logging

If these logs already flow to the same workspace, skip to step 2. Otherwise,
ask your APIM administrator to set them up for every relevant APIM instance:

1. In the Azure portal, open the APIM instance. Go to **Monitoring** >
   **Diagnostic settings** > **+ Add diagnostic setting**.
2. Select **Logs related to ApiManagement Gateway** and **Logs related to
   generative AI gateway**. Choose **Send to Log Analytics workspace**, select
   the workspace, and choose **Resource specific** as the destination table.
   Save the setting.
3. For each API that sends traffic to the models, go to **APIs** > the API >
   **Settings** > **Diagnostic Logs** > **Azure Monitor**. Enable **Log LLM
   messages** and set sampling to **100%**. The report does not need prompt or
   completion text; leave those options off unless separately required.

These settings change logging and can increase Azure Monitor costs. Do not
change existing settings without the administrator's approval. If the required
categories are unavailable, ask the administrator to check APIM support.
Logs can take time to appear.

## 2. Check the Foundry PTU metric

The workbook reads the existing Azure Monitor **metric** directly; it does not
need Foundry diagnostic logs or a metric-export script.

1. In the Azure portal, open the Foundry / Azure OpenAI **account** that hosts
   the PTU deployment. Go to **Monitoring** > **Metrics**.
2. Select **Provisioned-managed Utilization V2**. Filter or split by
   **ModelDeploymentName** to find the deployment.
3. Check that the metric has data for a completed hour with model traffic.
   Repeat for each account. If it is missing, verify that the deployment uses
   provisioned throughput and that you can read the account's metrics.

## 3. Import and save the workbook

**Easiest: one click.** Select
[**Deploy to Azure**](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmichael-rechani%2Fazure-foundry-apim-monitoring%2Fmain%2Fdeploy%2Fazuredeploy.json),
choose a subscription and resource group, then **Review + create > Create**.
Open it from **Monitor** > **Workbooks**. To get a fix later, run it again with
the same name and resource group; it updates that workbook in place. If you
previously imported a copy by hand, that copy remains separate and can be
updated through its Advanced editor.

**Or paste it manually:**

1. Open
   [`PTU-usage-by-APIM-subscription.workbook.json`](../workbooks/PTU-usage-by-APIM-subscription.workbook.json)
   on GitHub and select **Copy raw file**, or open it in a text editor and
   copy **all** its contents.
2. In the [Azure portal](https://portal.azure.com), open **Monitor** >
   **Workbooks** > **+ New**.
3. Select **`</>` Advanced editor** and the **Gallery Template** tab. Replace
   all the existing text with the copied JSON, then select **Apply**.
4. Select **Save**, give the workbook a name, and choose the subscription,
   resource group, and location. The workbook is now available from
   **Monitor** > **Workbooks**.

Saving creates a workbook resource. The workbook itself only **reads** the
other resources; it does not create, change, or delete APIM or Foundry
deployments. There is no exporter, scheduled job, or custom table to install.

## 4. View the results

1. Open the saved workbook and select the **Log Analytics workspace** that
   receives the APIM logs and up to five **Foundry account(s)** that host the
   deployments. Select the accounts, not Foundry projects. Nothing is selected
   by default, so pick both before the report loads.
2. Under **APIM instance(s)**, select every instance that sends traffic to
   those deployments and logs to that workspace.
3. Choose a **Time range** with at least one completed UTC hour after the
   deployments finished provisioning or changing. Start with **Time grain** =
   **1 hour** and **Output token weight** = **1**.
4. Choose a specific account and deployment under **PTU deployment**, or
   **All deployments (combined)**. The breakdown shows the Foundry account,
   deployment, APIM subscription, calls, tokens, and estimated PTU. The chart
   and subscription totals follow the deployment selection.
5. Open **Data check** and review any warnings before using the numbers. If
   data is missing, check the selected resources, permissions, APIM logs, and
   metric availability; allow time for new logs and metrics to arrive.
   The utilization metric can be visible even when APIM traffic is incomplete.
   Affected buckets are excluded from subscription estimates, so those
   estimates may cover less than the selected time range.

### Troubleshooting

- **Tokens and PTU are blank for an API.** The LLM log or usable token counts
  may be missing. Check **Settings > Diagnostics logs > Azure Monitor** on
  that API: enable **Log LLM messages** and confirm 100% sampling. Streaming
  responses that omit usage can also leave tokens blank. The workbook does not
  allocate affected buckets; investigate the Data check warnings first.
- **Rows show `<unmapped>` as the Foundry account.** APIM logged requests, but
  the BackendUrl did not identify a deployment on a selected account. Examples
  include the `/openai/v1` path, another host, or an account you did not select.
  Select that account, or check the API's backend URL. In Data check, review
  **LLM calls without an identifiable backend deployment**.
- **`E_QUERY_RESULT_SET_TOO_LARGE` (64 MB) or `Request entity too large`.**
  Shorten the **Time range** (for example 24 hours), or select fewer accounts,
  then re-run. A coarser **Time grain** may reduce some intermediate results,
  but the workbook still retrieves hourly metrics. Large selections can still
  exceed Azure Monitor query limits.
- **APIM log rows without correlation IDs.** Check APIM diagnostics and the
  affected gateway and LLM logs. Without an ID, the workbook cannot reliably
  join the records, so it leaves affected allocations blank. Unmatched LLM
  logs can also block adjacent hours because log timestamps may cross a bucket
  boundary. Only accessible logs can be checked.
- **The Log Analytics workspace or Foundry account list is empty.** Both lists
  come from Azure Resource Graph. If a resource is missing, confirm you have at
  least Reader on it. Newly created resources can take a few minutes to appear.
  Workbook dropdowns are [limited to 1,000 items](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-limits#parameter-limits);
  larger environments may not show every resource. Redeploy the latest
  template (Deploy to Azure) if you installed an earlier version that used the
  built-in resource picker, which can show nothing in some tenants.

## Important when sharing results

- Subscription PTU is an **estimate based on logged token share**, not a
  measurement of that subscription's capacity consumption. Direct or unlogged
  traffic can distort the split.
- APIM subscription IDs may not be customer names; map them separately if
  needed. The report may not identify custom proxy backends or rewritten URLs.
- Historical capacity and the completion time of deployment changes are not
  reliably reconstructed. Do not rely on estimates around changes or deleted
  deployments without independent verification.
- Large dropdowns, grids, and charts have [Azure Workbook limits](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-limits).
  Some subscription series may be grouped as **Other** in a chart; use the table
  for individual results.

Microsoft references: [APIM gateway logging](https://learn.microsoft.com/azure/api-management/api-management-howto-use-azure-monitor#resource-logs),
[LLM logging](https://learn.microsoft.com/azure/api-management/api-management-howto-llm-logs),
[PTU metrics](https://learn.microsoft.com/azure/foundry/openai/monitor-openai-reference),
and [Azure Workbooks](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-overview).
