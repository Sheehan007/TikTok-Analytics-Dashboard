(function () {
  const dataset = window.ADS_PRODUCT_ANALYTICS;
  if (!dataset) {
    document.body.innerHTML = '<main class="empty-state">Run npm run build:data to generate dashboard data.</main>';
    return;
  }

  const weekly = dataset.weeklyPerformance;
  const benchmarks = dataset.benchmarks;
  const filters = {
    period: document.getElementById("periodFilter"),
    region: document.getElementById("regionFilter"),
    country: document.getElementById("countryFilter"),
    segment: document.getElementById("segmentFilter"),
    objective: document.getElementById("objectiveFilter"),
    product: document.getElementById("productFilter"),
  };

  const colors = {
    cyan: "#00b8c4",
    pink: "#f12b6d",
    green: "#168a4a",
    amber: "#b87900",
    violet: "#6a5acd",
    ink: "#14171c",
    muted: "#64707d",
    line: "#dfe4ea",
  };

  const moneyCompact = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  });
  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  const numberCompact = new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  });
  const numberFull = new Intl.NumberFormat("en-US");

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function safeDivide(numerator, denominator) {
    return denominator ? numerator / denominator : 0;
  }

  function pct(value, digits = 1) {
    return `${(value * 100).toFixed(digits)}%`;
  }

  function signedPct(value) {
    const sign = value > 0 ? "+" : "";
    return `${sign}${pct(value)}`;
  }

  function fillSelect(select, values, label = "All") {
    select.innerHTML = "";
    const allOption = document.createElement("option");
    allOption.value = "All";
    allOption.textContent = label;
    select.appendChild(allOption);
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  function initializeFilters() {
    fillSelect(filters.region, dataset.filters.regions);
    fillSelect(filters.country, dataset.filters.countries);
    fillSelect(filters.segment, dataset.filters.segments);
    fillSelect(filters.objective, dataset.filters.objectives);
    fillSelect(filters.product, dataset.filters.products);

    Object.values(filters).forEach((select) => {
      select.addEventListener("change", () => {
        if (select === filters.region) syncCountryOptions();
        render();
      });
    });

    document.getElementById("resetFilters").addEventListener("click", () => {
      filters.period.value = "8";
      filters.region.value = "All";
      syncCountryOptions();
      filters.country.value = "All";
      filters.segment.value = "All";
      filters.objective.value = "All";
      filters.product.value = "All";
      render();
    });
    document.getElementById("exportCsv").addEventListener("click", exportFilteredCsv);
  }

  function syncCountryOptions() {
    const region = filters.region.value;
    const countries = region === "All"
      ? dataset.filters.countries
      : [...new Set(weekly.filter((row) => row.region === region).map((row) => row.country))].sort();
    const current = filters.country.value;
    fillSelect(filters.country, countries);
    filters.country.value = countries.includes(current) ? current : "All";
  }

  function selectedWeeks(periodValue) {
    const allWeeks = [...new Set(weekly.map((row) => row.week_start))].sort();
    if (periodValue === "all") return allWeeks;
    return allWeeks.slice(-Number(periodValue));
  }

  function previousWeeks(periodValue) {
    const allWeeks = [...new Set(weekly.map((row) => row.week_start))].sort();
    if (periodValue === "all") return allWeeks.slice(-26, -13);
    const count = Number(periodValue);
    return allWeeks.slice(-(count * 2), -count);
  }

  function matchesDimensions(row) {
    return (
      (filters.region.value === "All" || row.region === filters.region.value) &&
      (filters.country.value === "All" || row.country === filters.country.value) &&
      (filters.segment.value === "All" || row.advertiser_segment === filters.segment.value) &&
      (filters.objective.value === "All" || row.campaign_objective === filters.objective.value) &&
      (filters.product.value === "All" || row.ad_product === filters.product.value)
    );
  }

  function filteredRows(weeks) {
    const allowedWeeks = new Set(weeks);
    return weekly.filter((row) => allowedWeeks.has(row.week_start) && matchesDimensions(row));
  }

  function aggregateRows(rows) {
    return rows.reduce(
      (acc, row) => {
        acc.spend += row.spend;
        acc.impressions += row.impressions;
        acc.clicks += row.clicks;
        acc.conversions += row.conversions;
        acc.revenue += row.revenue;
        acc.cohort += row.advertiser_cohort;
        acc.retained += row.retained_advertisers_d30;
        return acc;
      },
      { spend: 0, impressions: 0, clicks: 0, conversions: 0, revenue: 0, cohort: 0, retained: 0 }
    );
  }

  function groupBy(rows, keyFn) {
    const grouped = new Map();
    rows.forEach((row) => {
      const key = keyFn(row);
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(row);
    });
    return grouped;
  }

  function metricRecord(rows) {
    const totals = aggregateRows(rows);
    return {
      ...totals,
      ctr: safeDivide(totals.clicks, totals.impressions),
      cvr: safeDivide(totals.conversions, totals.clicks),
      cpc: safeDivide(totals.spend, totals.clicks),
      cpm: safeDivide(totals.spend, totals.impressions) * 1000,
      cpa: safeDivide(totals.spend, totals.conversions),
      roas: safeDivide(totals.revenue, totals.spend),
      retention: safeDivide(totals.retained, totals.cohort),
    };
  }

  function renderKpis(rows, previousRows) {
    const current = metricRecord(rows);
    const previous = metricRecord(previousRows);
    const revenueGrowth = safeDivide(current.revenue - previous.revenue, previous.revenue);

    setText("kpiRevenue", moneyCompact.format(current.revenue));
    setText("kpiGrowth", `${signedPct(revenueGrowth)} revenue growth`);
    setText("kpiSpend", moneyCompact.format(current.spend));
    setText("kpiCpm", `${money.format(current.cpm)} CPM`);
    setText("kpiRoas", `${current.roas.toFixed(2)}x`);
    setText("kpiCpa", `${money.format(current.cpa)} CPA`);
    setText("kpiCtr", pct(current.ctr, 2));
    setText("kpiCpc", `${money.format(current.cpc)} CPC`);
    setText("kpiCvr", pct(current.cvr, 2));
    setText("kpiConversions", `${numberFull.format(current.conversions)} conversions`);
    setText("kpiRetention", pct(current.retention, 1));
    setText("kpiCohort", `${numberFull.format(current.cohort)} advertisers`);
  }

  function setText(id, value) {
    document.getElementById(id).textContent = value;
  }

  function pointPath(points) {
    return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  }

  function drawTrend(rows, selectedWeekList) {
    const target = document.getElementById("trendChart");
    const weeklyRows = selectedWeekList.map((week) => {
      const record = metricRecord(rows.filter((row) => row.week_start === week));
      return { week, spend: record.spend, revenue: record.revenue };
    });

    setText("trendSummary", `${selectedWeekList.length} weeks`);

    if (!weeklyRows.length || !rows.length) {
      target.innerHTML = '<div class="empty-state">No data for selected filters</div>';
      return;
    }

    const width = 680;
    const height = 320;
    const pad = { top: 20, right: 26, bottom: 34, left: 54 };
    const maxValue = Math.max(...weeklyRows.flatMap((row) => [row.spend, row.revenue]), 1);
    const x = (index) => pad.left + (index / Math.max(1, weeklyRows.length - 1)) * (width - pad.left - pad.right);
    const y = (value) => height - pad.bottom - (value / maxValue) * (height - pad.top - pad.bottom);
    const revenuePoints = weeklyRows.map((row, index) => ({ x: x(index), y: y(row.revenue) }));
    const spendPoints = weeklyRows.map((row, index) => ({ x: x(index), y: y(row.spend) }));
    const firstLabel = weeklyRows[0].week.slice(5);
    const lastLabel = weeklyRows[weeklyRows.length - 1].week.slice(5);

    target.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Weekly revenue and spend trend">
        <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="${colors.line}" />
        <line x1="${pad.left}" y1="${pad.top}" x2="${pad.left}" y2="${height - pad.bottom}" stroke="${colors.line}" />
        <text class="axis-label" x="${pad.left}" y="${height - 10}">${firstLabel}</text>
        <text class="axis-label" x="${width - pad.right - 36}" y="${height - 10}">${lastLabel}</text>
        <text class="axis-label" x="8" y="${y(maxValue) + 4}">${moneyCompact.format(maxValue)}</text>
        <path d="${pointPath(spendPoints)}" fill="none" stroke="${colors.cyan}" stroke-width="4" stroke-linecap="round" />
        <path d="${pointPath(revenuePoints)}" fill="none" stroke="${colors.pink}" stroke-width="4" stroke-linecap="round" />
        ${revenuePoints.map((point) => `<circle cx="${point.x}" cy="${point.y}" r="3.6" fill="${colors.pink}" />`).join("")}
        ${spendPoints.map((point) => `<circle cx="${point.x}" cy="${point.y}" r="3.2" fill="${colors.cyan}" />`).join("")}
        <rect x="${width - 188}" y="18" width="160" height="48" rx="8" fill="#ffffff" stroke="${colors.line}" />
        <circle cx="${width - 166}" cy="37" r="5" fill="${colors.pink}" />
        <text class="chart-label" x="${width - 154}" y="41">Revenue</text>
        <circle cx="${width - 166}" cy="56" r="5" fill="${colors.cyan}" />
        <text class="chart-label" x="${width - 154}" y="60">Spend</text>
      </svg>
    `;
  }

  function drawRegionBars(rows) {
    const target = document.getElementById("regionChart");
    const groups = [...groupBy(rows, (row) => row.region).entries()].map(([region, groupRows]) => ({
      region,
      ...metricRecord(groupRows),
    }));

    if (!groups.length) {
      target.innerHTML = '<div class="empty-state">No regional data</div>';
      return;
    }

    const width = 420;
    const rowHeight = 54;
    const height = 36 + groups.length * rowHeight;
    const maxRoas = Math.max(...groups.map((row) => row.roas), benchmarks.roas);

    target.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Regional ROAS bar chart">
        ${groups
          .sort((a, b) => b.roas - a.roas)
          .map((row, index) => {
            const y = 24 + index * rowHeight;
            const barWidth = Math.max(8, (row.roas / maxRoas) * 210);
            const color = row.roas >= benchmarks.roas ? colors.green : colors.pink;
            return `
              <text class="chart-label" x="0" y="${y + 18}">${escapeHtml(row.region)}</text>
              <rect x="154" y="${y}" width="226" height="24" rx="8" fill="#edf1f4" />
              <rect x="154" y="${y}" width="${barWidth}" height="24" rx="8" fill="${color}" />
              <text class="chart-label" x="388" y="${y + 18}" text-anchor="end">${row.roas.toFixed(2)}x</text>
            `;
          })
          .join("")}
      </svg>
    `;
  }

  function drawFunnel(rows) {
    const target = document.getElementById("funnelChart");
    const totals = metricRecord(rows);
    const stages = [
      { label: "Impressions", value: totals.impressions, display: numberCompact.format(totals.impressions), rate: 1, color: colors.ink },
      { label: "Clicks", value: totals.clicks, display: numberCompact.format(totals.clicks), rate: totals.ctr, color: colors.cyan },
      { label: "Conversions", value: totals.conversions, display: numberCompact.format(totals.conversions), rate: totals.cvr, color: colors.violet },
      { label: "Revenue", value: totals.revenue, display: moneyCompact.format(totals.revenue), rate: Math.min(1, totals.roas / 4), color: colors.pink },
    ];

    if (!rows.length) {
      target.innerHTML = '<div class="empty-state">No funnel data</div>';
      return;
    }

    target.innerHTML = stages
      .map((stage, index) => {
        const width = index === 0 ? 100 : Math.max(4, stage.rate * 100);
        const sublabel = index === 0 ? "100%" : index === 3 ? `${totals.roas.toFixed(2)}x ROAS` : pct(stage.rate, 2);
        return `
          <div class="funnel-row">
            <div class="funnel-label">${stage.label}</div>
            <div class="funnel-track">
              <div class="funnel-fill" style="width:${width}%;background:${stage.color}"></div>
            </div>
            <div class="funnel-value">${stage.display}<br>${sublabel}</div>
          </div>
        `;
      })
      .join("");
  }

  function drawCountryScatter(rows) {
    const target = document.getElementById("countryScatter");
    const groups = [...groupBy(rows, (row) => `${row.region}|${row.country}`).entries()].map(([key, groupRows]) => {
      const [region, country] = key.split("|");
      return { region, country, ...metricRecord(groupRows) };
    });

    if (!groups.length) {
      target.innerHTML = '<div class="empty-state">No country data</div>';
      return;
    }

    const width = 680;
    const height = 320;
    const pad = { top: 18, right: 34, bottom: 42, left: 58 };
    const maxCpa = Math.max(...groups.map((row) => row.cpa), benchmarks.cpa);
    const maxRoas = Math.max(...groups.map((row) => row.roas), benchmarks.roas);
    const maxRevenue = Math.max(...groups.map((row) => row.revenue), 1);
    const x = (value) => pad.left + (value / maxCpa) * (width - pad.left - pad.right);
    const y = (value) => height - pad.bottom - (value / maxRoas) * (height - pad.top - pad.bottom);
    const benchmarkX = x(benchmarks.cpa);
    const benchmarkY = y(benchmarks.roas);

    target.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Country ROAS versus CPA">
        <rect x="${pad.left}" y="${pad.top}" width="${width - pad.left - pad.right}" height="${height - pad.top - pad.bottom}" fill="#fbfcfd" stroke="${colors.line}" />
        <line x1="${benchmarkX}" y1="${pad.top}" x2="${benchmarkX}" y2="${height - pad.bottom}" stroke="${colors.amber}" stroke-dasharray="5 5" />
        <line x1="${pad.left}" y1="${benchmarkY}" x2="${width - pad.right}" y2="${benchmarkY}" stroke="${colors.green}" stroke-dasharray="5 5" />
        <text class="axis-label" x="${pad.left}" y="${height - 12}">Low CPA</text>
        <text class="axis-label" x="${width - pad.right - 48}" y="${height - 12}">High CPA</text>
        <text class="axis-label" x="10" y="${pad.top + 12}">High ROAS</text>
        ${groups
          .sort((a, b) => b.revenue - a.revenue)
          .map((row) => {
            const radius = 5 + Math.sqrt(row.revenue / maxRevenue) * 13;
            const color = row.roas >= benchmarks.roas && row.cpa <= benchmarks.cpa ? colors.green : row.roas < benchmarks.roas ? colors.pink : colors.cyan;
            return `
              <circle cx="${x(row.cpa)}" cy="${y(row.roas)}" r="${radius.toFixed(1)}" fill="${color}" fill-opacity="0.72" stroke="#ffffff" stroke-width="2">
                <title>${escapeHtml(row.country)}: ${row.roas.toFixed(2)}x ROAS, ${money.format(row.cpa)} CPA</title>
              </circle>
              <text class="axis-label" x="${x(row.cpa) + radius + 3}" y="${y(row.roas) + 4}">${escapeHtml(row.country)}</text>
            `;
          })
          .join("")}
      </svg>
    `;
  }

  function renderCountryTable(rows) {
    const target = document.getElementById("countryTable");
    const groups = [...groupBy(rows, (row) => `${row.region}|${row.country}`).entries()]
      .map(([key, groupRows]) => {
        const [region, country] = key.split("|");
        return { region, country, ...metricRecord(groupRows) };
      })
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 8);

    if (!groups.length) {
      target.innerHTML = '<div class="empty-state">No countries found</div>';
      return;
    }

    target.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Country</th>
            <th>Revenue</th>
            <th>ROAS</th>
            <th>CPA</th>
          </tr>
        </thead>
        <tbody>
          ${groups
            .map(
              (row) => `
                <tr>
                  <td>${escapeHtml(row.country)}<br><small>${escapeHtml(row.region)}</small></td>
                  <td>${moneyCompact.format(row.revenue)}</td>
                  <td>${row.roas.toFixed(2)}x</td>
                  <td>${money.format(row.cpa)}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    `;
  }

  function renderRecommendations() {
    const target = document.getElementById("recommendationTable");
    const rows = dataset.segmentRecommendations
      .filter((row) => filters.region.value === "All" || row.region === filters.region.value)
      .filter((row) => filters.segment.value === "All" || row.advertiser_segment === filters.segment.value)
      .filter((row) => filters.objective.value === "All" || row.campaign_objective === filters.objective.value)
      .filter((row) => filters.product.value === "All" || row.ad_product === filters.product.value)
      .slice(0, 10);

    if (!rows.length) {
      target.innerHTML = '<div class="empty-state">No recommendations for selected filters</div>';
      return;
    }

    target.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Priority</th>
            <th>Segment</th>
            <th>Performance</th>
            <th>Recommendation</th>
            <th>Upside</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map((row) => {
              const priorityClass = row.priority.toLowerCase();
              return `
                <tr>
                  <td><span class="priority ${priorityClass}">${escapeHtml(row.priority)}</span></td>
                  <td>${escapeHtml(row.region)}<br><small>${escapeHtml(row.advertiser_segment)} | ${escapeHtml(row.campaign_objective)} | ${escapeHtml(row.ad_product)}</small></td>
                  <td>${row.roas.toFixed(2)}x ROAS<br><small>${pct(row.cvr, 2)} CVR | ${money.format(row.cpa)} CPA</small></td>
                  <td>${escapeHtml(row.recommended_action)}</td>
                  <td>${moneyCompact.format(row.estimated_revenue_upside)}</td>
                </tr>
              `;
            })
            .join("")}
        </tbody>
      </table>
    `;
  }

  function exportFilteredCsv() {
    const weeks = selectedWeeks(filters.period.value);
    const rows = filteredRows(weeks);
    const headers = [
      "week_start",
      "region",
      "country",
      "advertiser_segment",
      "campaign_objective",
      "ad_product",
      "spend",
      "impressions",
      "clicks",
      "conversions",
      "revenue",
      "ctr",
      "cvr",
      "cpc",
      "cpm",
      "cpa",
      "roas",
      "d30_retention",
    ];
    const csv = [headers.join(",")]
      .concat(
        rows.map((row) =>
          headers
            .map((header) => {
              const value = row[header] ?? "";
              return `"${String(value).replace(/"/g, '""')}"`;
            })
            .join(",")
        )
      )
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "tiktok_ads_filtered_kpis.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function render() {
    const weeks = selectedWeeks(filters.period.value);
    const previous = previousWeeks(filters.period.value);
    const rows = filteredRows(weeks);
    const previousRows = filteredRows(previous);

    renderKpis(rows, previousRows);
    drawTrend(rows, weeks);
    drawRegionBars(rows);
    drawFunnel(rows);
    drawCountryScatter(rows);
    renderCountryTable(rows);
    renderRecommendations();
  }

  initializeFilters();
  syncCountryOptions();
  render();
})();
