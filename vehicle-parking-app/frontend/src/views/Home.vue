<template>
  <div class="home">
    <h1>Welcome to the Vehicle Parking App</h1>
    <p>Find and reserve your parking spot easily!</p>
    <router-link to="/login" class="btn btn-primary">Login</router-link>
    <router-link to="/register" class="btn btn-secondary">Register</router-link>
    <div class="parking-lots">
      <h2>Available Parking Lots</h2>
      <ParkingLotCard v-for="lot in parkingLots" :key="lot.id" :lot="lot" />
    </div>
  </div>
</template>

<script>
import ParkingLotCard from '../components/ParkingLotCard.vue';
import { fetchParkingLots } from '../services/api.js';

export default {
  name: 'Home',
  components: {
    ParkingLotCard,
  },
  data() {
    return {
      parkingLots: [],
    };
  },
  created() {
    this.loadParkingLots();
  },
  methods: {
    async loadParkingLots() {
      try {
        const response = await fetchParkingLots();
        this.parkingLots = response.data;
      } catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },
  },
};
</script>

<style scoped>
.home {
  text-align: center;
  margin: 20px;
}

.parking-lots {
  margin-top: 20px;
}
</style>