<template>
  <div>
    <h2>Parking Summary Charts</h2>
    <div>
      <canvas id="parkingChart"></canvas>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale);

export default {
  name: 'Charts',
  components: {
    LineChart: Line
  },
  data() {
    return {
      parkingData: {
        labels: [],
        datasets: [
          {
            label: 'Parking Spots Occupied',
            data: [],
            borderColor: '#42A5F5',
            fill: false
          }
        ]
      }
    };
  },
  mounted() {
    this.fetchParkingData();
  },
  methods: {
    fetchParkingData() {
      // Fetch parking data from the API
      this.$http.get('/api/parking/stats')
        .then(response => {
          const data = response.data;
          this.parkingData.labels = data.labels;
          this.parkingData.datasets[0].data = data.values;
        })
        .catch(error => {
          console.error('Error fetching parking data:', error);
        });
    }
  }
};
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 20px;
}
</style>