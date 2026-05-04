<%inherit file="layout.mako"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>

<div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-0">
  <h2 class="mb-0"><i class="bi bi-bar-chart"></i> ${_("Reports")}</h2>
  <div class="btn-group" role="group" aria-label="${_('View mode')}">
    <input type="radio" class="btn-check" name="reportViewToggle" id="toggleTable" autocomplete="off" checked>
    <label class="btn btn-outline-secondary btn-sm" for="toggleTable">
      <i class="bi bi-table"></i> ${_("Table")}
    </label>
    <input type="radio" class="btn-check" name="reportViewToggle" id="toggleChart" autocomplete="off">
    <label class="btn btn-outline-secondary btn-sm" for="toggleChart">
      <i class="bi bi-bar-chart-fill"></i> ${_("Chart")}
    </label>
  </div>
</div>
<hr>
<p class="lead">${lead}</p>

<div id="report-table-view">
  <%include file="report_table.mako"/>
</div>

<div id="report-chart-view" class="d-none">
  <div class="chart-container" style="position:relative;">
    <canvas id="reportChart"></canvas>
  </div>
  <p class="text-body-secondary small mt-2">
    <i class="bi bi-info-circle"></i> ${_("Chart shows top")} 25 ${_("results")}
  </p>
</div>

<script>
(function () {
  const chartData = ${chart_data_json | n};
  if (!chartData) return;

  const canvasEl = document.getElementById('reportChart');
  const itemCount = chartData.labels.length;
  const barHeight = 36;
  const minHeight = 260;
  canvasEl.style.height = Math.max(minHeight, itemCount * barHeight) + 'px';

  const colors = chartData.labels.map(function (_, i) {
    const hue = Math.round((i / Math.max(itemCount - 1, 1)) * 200 + 200);
    return 'hsl(' + hue + ',60%,52%)';
  });

  const chart = new Chart(canvasEl, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: document.title,
        data: chartData.values,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1,
        borderRadius: 3,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (ctx) {
              const val = ctx.parsed.x;
              if (chartData.is_decimal) {
                return ' ' + val.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
              }
              return ' ' + val.toLocaleString();
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              if (chartData.is_decimal) {
                return value.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 2});
              }
              return value.toLocaleString();
            }
          }
        },
        y: {
          ticks: { font: { size: 12 } }
        }
      }
    }
  });

  document.getElementById('toggleTable').addEventListener('change', function () {
    document.getElementById('report-table-view').classList.remove('d-none');
    document.getElementById('report-chart-view').classList.add('d-none');
  });
  document.getElementById('toggleChart').addEventListener('change', function () {
    document.getElementById('report-table-view').classList.add('d-none');
    document.getElementById('report-chart-view').classList.remove('d-none');
    chart.resize();
  });
}());
</script>
