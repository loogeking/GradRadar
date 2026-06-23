// ============== ECharts 图表封装 ==============

/**
 * 复试线趋势折线图
 */
function renderScoreLineChart(containerId, data) {
    const chart = echarts.init(document.getElementById(containerId));

    const series = [];
    if (data.total_score && data.total_score.some(v => v !== null)) {
        series.push({ name: '总分线', type: 'line', data: data.total_score, smooth: true });
    }
    if (data.politics && data.politics.some(v => v !== null)) {
        series.push({ name: '政治', type: 'line', data: data.politics, smooth: true });
    }
    if (data.english && data.english.some(v => v !== null)) {
        series.push({ name: '英语', type: 'line', data: data.english, smooth: true });
    }
    if (data.math && data.math.some(v => v !== null)) {
        series.push({ name: '数学', type: 'line', data: data.math, smooth: true });
    }
    if (data.professional && data.professional.some(v => v !== null)) {
        series.push({ name: '专业课', type: 'line', data: data.professional, smooth: true });
    }

    chart.setOption({
        title: { text: '历年复试分数线趋势', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: data.years.map(y => y + '年') },
        yAxis: { type: 'value', name: '分数' },
        series: series
    });
    return chart;
}

/**
 * 招生人数柱状图
 */
function renderEnrollmentChart(containerId, data) {
    const chart = echarts.init(document.getElementById(containerId));
    chart.setOption({
        title: { text: '历年招生计划', left: 'center' },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: { type: 'category', data: data.years.map(y => y + '年') },
        yAxis: { type: 'value', name: '人数' },
        series: [
            { name: '计划总数', type: 'bar', data: data.plan_total },
            { name: '统考', type: 'bar', data: data.plan_exam },
            { name: '推免', type: 'bar', data: data.plan_recommend }
        ]
    });
    return chart;
}

/**
 * 推免比例饼图（取最新一年）
 */
function renderRecommendRatioChart(containerId, data) {
    const chart = echarts.init(document.getElementById(containerId));
    const lastIdx = data.years.length - 1;
    if (lastIdx < 0) return;

    const exam = data.plan_exam[lastIdx] || 0;
    const recommend = data.plan_recommend[lastIdx] || 0;

    chart.setOption({
        title: {
            text: `${data.years[lastIdx]}年招生构成`,
            left: 'center'
        },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0 },
        series: [{
            name: '招生构成',
            type: 'pie',
            radius: '60%',
            data: [
                { value: exam, name: '统考' },
                { value: recommend, name: '推免' }
            ]
        }]
    });
    return chart;
}