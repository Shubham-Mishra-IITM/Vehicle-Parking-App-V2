<template>
  <div class="admin">
    <h1>Admin Dashboard</h1>
    <div class="admin-controls">
      <button @click="fetchParkingLots">View Parking Lots</button>
      <button @click="createParkingLot">Create Parking Lot</button>
    </div>
    <div v-if="parkingLots.length">
      <h2>Parking Lots</h2>
      <ul>
        <li v-for="lot in parkingLots" :key="lot.id">
          <strong>{{ lot.prime_location_name }}</strong> - ${{ lot.price }}
          <button @click="editParkingLot(lot.id)">Edit</button>
          <button @click="deleteParkingLot(lot.id)">Delete</button>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No parking lots available.</p>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      parkingLots: [],
    };
  },
  methods: {
    async fetchParkingLots() {
      try {
        const response = await api.get('/admin/parking-lots');
        this.parkingLots = response.data;
      } catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },
    async createParkingLot() {
      // Logic to create a new parking lot
    },
    async editParkingLot(id) {
      // Logic to edit the parking lot
    },
    async deleteParkingLot(id) {
      try {
        await api.delete(`/admin/parking-lots/${id}`);
        this.fetchParkingLots(); // Refresh the list
      } catch (error) {
        console.error('Error deleting parking lot:', error);
      }
    },
  },
  mounted() {
    this.fetchParkingLots();
  },
};
</script>

<style scoped>
.admin {
  padding: 20px;
}
.admin-controls {
  margin-bottom: 20px;
}
</style>