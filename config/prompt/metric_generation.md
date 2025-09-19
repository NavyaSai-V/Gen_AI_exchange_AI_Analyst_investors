# AI Prompt for Extracting Metric Values for Graphical Visualization from Startup Summary

You are provided with a generated one-page startup summary, organized in sections such as Team, Product, Market, Traction, Risks, and Ask. Your task is to carefully read this summary and extract all relevant quantitative metrics that can be used for visual graphs and charts. These metrics may include (but are not limited to):

- Market size values (TAM, SAM, SOM)
- Revenue figures and projections
- Gross margin, EBITDA, or other financial ratios
- User/customer growth numbers and rates
- Churn rates and retention metrics
- Funding amounts, allocation breakdowns
- Product adoption or engagement numbers
- Distribution channel metrics (e.g., partner counts, order volume)
- Any other numerical or time-series data provided

## Instructions

1. **Identify and list every quantitative metric mentioned in the summary.**  
   For each metric, provide:
   - The metric name/description
   - The value(s) (and units)
   - The time frame or period (if specified)
   - The related section (e.g., Traction, Market, Ask)

2. **Organize the extracted metrics in a structured data format** suitable for graphing (such as a JSON array or table).

3. **If data is missing or unclear, note it as "not available".**

4. **Do NOT generate graphs or charts—only extract and structure the metric data.**

## Example Output Format

```json
[
  {
    "section": "Market",
    "metric": "TAM",
    "value": "10 million farmers",
    "unit": "individuals",
    "time_frame": "current"
  },
  {
    "section": "Traction",
    "metric": "Revenue",
    "value": "₹5 crore",
    "unit": "INR",
    "time_frame": "annual"
  },
  {
    "section": "Ask",
    "metric": "Funding Requested",
    "value": "₹20 crore",
    "unit": "INR",
    "time_frame": "current round"
  }
]
```

## Additional Notes

- Only include metrics explicitly stated in the summary.
- Use the most granular time or segmentation available (e.g., monthly, yearly, projections).
- If a metric relates to a distribution or allocation, include the relevant percentages or breakdowns.
- Your output should enable analysts to easily generate visual graphs from the structured metric data.

**Begin by extracting and structuring all available metrics from the provided startup summary.**