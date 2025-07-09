<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>
    <div class="dashboard-controls">
      <button @click="fetchParkingLots">Refresh Parking Lots</button>
      <button @click="createParkingLot">Add Parking Lot</button>
    </div>
    <div class="parking-lots">
      <h2>Parking Lots</h2>
      <div v-for="lot in parkingLots" :key="lot.id" class="parking-lot-card">
        <h3>{{ lot.prime_location_name }}</h3>
        <p>Price: {{ lot.price }}</p>
        <p>Address: {{ lot.address }}</p>
        <p>Pin Code: {{ lot.pin_code }}</p>
        <p>Available Spots: {{ lot.number_of_spots }}</p>
        <button @click="editParkingLot(lot.id)">Edit</button>
        <button @click="deleteParkingLot(lot.id)">Delete</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      parkingLots: []
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
    createParkingLot() {
      // Logic to create a new parking lot
    },
    editParkingLot(lotId) {
      // Logic to edit the selected parking lot
    },
    async deleteParkingLot(lotId) {
      try {
        await api.delete(`/admin/parking-lots/${lotId}`);
        this.fetchParkingLots();
      } catch (error) {
        console.error('Error deleting parking lot:', error);
      }
    }
  },
  mounted() {
    this.fetchParkingLots();
  }
};
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.dashboard-controls {
  margin-bottom: 20px;
}

.parking-lot-card {
  border: 1px solid #ccc;
  padding: 15px;
  margin-bottom: 10px;
}
</style>