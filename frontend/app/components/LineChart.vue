<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script setup>
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const props = defineProps({
  labels: Array,
  datasets: Array,
  title: String,
});

const chartCanvas = ref(null);
let chartInstance = null;

onMounted(() => {
  if (chartCanvas.value) {
    chartInstance = new ChartJS(chartCanvas.value, {
      type: "line",
      data: {
        labels: props.labels,
        datasets: props.datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: !!props.title,
            text: props.title,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});

watch(
  () => [props.labels, props.datasets],
  () => {
    if (chartInstance) {
      chartInstance.data.labels = props.labels;
      chartInstance.data.datasets = props.datasets;
      chartInstance.update();
    }
  },
  { deep: true }
);
</script>
