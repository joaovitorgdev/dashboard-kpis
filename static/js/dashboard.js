// charts globais pra poder destruir e recriar
let chartMes = null;
let chartRegiao = null;
let chartCategoria = null;
let chartVendedores = null;

const fmtMoeda = (v) => {
    return 'R$ ' + Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
};

const pegarFiltros = () => {
    return {
        data_inicio: document.getElementById('data_inicio').value,
        data_fim: document.getElementById('data_fim').value,
        regiao: document.getElementById('regiao').value,
        categoria: document.getElementById('categoria').value,
        status: document.getElementById('status').value,
        vendedor: document.getElementById('vendedor').value,
    };
};

const filtrosParaQuery = (f) => {
    const params = new URLSearchParams();
    Object.keys(f).forEach(k => {
        if (f[k]) params.append(k, f[k]);
    });
    return params.toString();
};

const atualizarKpis = (kpis) => {
    document.getElementById('kpi-receita').textContent = fmtMoeda(kpis.receita_total);
    document.getElementById('kpi-lucro').textContent = fmtMoeda(kpis.lucro_total);
    document.getElementById('kpi-margem').textContent = kpis.margem_media + '%';
    document.getElementById('kpi-qtd').textContent = kpis.qtd_vendas;
    document.getElementById('kpi-ticket').textContent = fmtMoeda(kpis.ticket_medio);
    document.getElementById('kpi-taxa').textContent = kpis.taxa_conclusao + '%';
};

const statusClass = (s) => {
    if (s === 'Concluído') return 'status-concluido';
    if (s === 'Pendente') return 'status-pendente';
    if (s === 'Cancelado') return 'status-cancelado';
    return '';
};

const atualizarTabela = (rows) => {
    const tbody = document.querySelector('#tabela-vendas tbody');
    tbody.innerHTML = '';

    if (!rows || rows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#94a3b8">Nenhum registro</td></tr>';
        return;
    }

    rows.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.data}</td>
            <td>${r.regiao}</td>
            <td>${r.categoria}</td>
            <td>${r.produto}</td>
            <td>${r.vendedor}</td>
            <td>${r.quantidade}</td>
            <td>${fmtMoeda(r.receita)}</td>
            <td>${fmtMoeda(r.lucro)}</td>
            <td class="${statusClass(r.status)}">${r.status}</td>
        `;
        tbody.appendChild(tr);
    });
};

const coresPadrao = [
    '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#ec4899', '#84cc16'
];

const criarChart = (ctx, tipo, labels, datasets, extraOpts) => {
    return new Chart(ctx, {
        type: tipo,
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: tipo === 'bar' || tipo === 'line' ? {
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            } : {},
            ...extraOpts
        }
    });
};

const atualizarCharts = (charts) => {
    // mes
    if (chartMes) chartMes.destroy();
    chartMes = criarChart(
        document.getElementById('chart-mes'),
        'line',
        charts.mes.labels,
        [
            { label: 'Receita', data: charts.mes.receita, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', fill: true, tension: 0.3 },
            { label: 'Lucro', data: charts.mes.lucro, borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.1)', fill: true, tension: 0.3 }
        ]
    );

    // regiao
    if (chartRegiao) chartRegiao.destroy();
    chartRegiao = criarChart(
        document.getElementById('chart-regiao'),
        'doughnut',
        charts.regiao.labels,
        [{
            data: charts.regiao.valores,
            backgroundColor: coresPadrao
        }]
    );

    // categoria
    if (chartCategoria) chartCategoria.destroy();
    chartCategoria = criarChart(
        document.getElementById('chart-categoria'),
        'bar',
        charts.categoria.labels,
        [{
            label: 'Receita',
            data: charts.categoria.valores,
            backgroundColor: '#3b82f6'
        }]
    );

    // vendedores
    if (chartVendedores) chartVendedores.destroy();
    chartVendedores = criarChart(
        document.getElementById('chart-vendedores'),
        'bar',
        charts.vendedores.labels,
        [{
            label: 'Receita',
            data: charts.vendedores.valores,
            backgroundColor: '#22c55e'
        }],
        { indexAxis: 'y' }
    );
};

const carregarDados = async () => {
    const filtros = pegarFiltros();
    const qs = filtrosParaQuery(filtros);

    try {
        const resp = await fetch('/api/kpis?' + qs);
        if (!resp.ok) throw new Error('erro na api');
        const data = await resp.json();

        atualizarKpis(data.kpis);
        atualizarCharts(data.charts);
        atualizarTabela(data.tabela);

        if (data.atualizado_em) {
            document.getElementById('atualizado-em').textContent = 'Atualizado: ' + data.atualizado_em;
        }
    } catch (err) {
        console.error('falhou ao carregar:', err);
    }
};

const limparFiltros = () => {
    document.getElementById('data_inicio').value = window.FILTER_DEFAULTS.data_min;
    document.getElementById('data_fim').value = window.FILTER_DEFAULTS.data_max;
    document.getElementById('regiao').value = 'todas';
    document.getElementById('categoria').value = 'todas';
    document.getElementById('status').value = 'todos';
    document.getElementById('vendedor').value = 'todos';
    carregarDados();
};

const exportarPdf = () => {
    const filtros = pegarFiltros();
    const qs = filtrosParaQuery(filtros);
    window.location.href = '/api/export/pdf?' + qs;
};

// eventos
document.getElementById('btn-filtrar').addEventListener('click', carregarDados);
document.getElementById('btn-limpar').addEventListener('click', limparFiltros);
document.getElementById('btn-pdf').addEventListener('click', exportarPdf);

// carrega ao abrir
document.addEventListener('DOMContentLoaded', carregarDados);
