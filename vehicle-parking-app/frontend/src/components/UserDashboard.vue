<template>
  <div class="user-dashboard">
    <h1>User Dashboard</h1>
    <div class="parking-lots">
      <h2>Available Parking Lots</h2>
      <div v-for="lot in parkingLots" :key="lot.id" class="parking-lot-card">
        <ParkingLotCard :lot="lot" @reserve="reserveSpot" />
      </div>
    </div>
    <div class="reservations">
      <h2>Your Reservations</h2>
      <table>
        <thead>
          <tr>
            <th>Parking Spot</th>
            <th>Parking Time</th>
            <th>Leaving Time</th>
            <th>Cost</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="reservation in userReservations" :key="reservation.id">
            <td>{{ reservation.spot_id }}</td>
            <td>{{ reservation.parking_timestamp }}</td>
            <td>{{ reservation.leaving_timestamp }}</td>
            <td>{{ reservation.parking_cost }}</td>
            <td>
              <button @click="releaseSpot(reservation.id)">Release</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import ParkingLotCard from './ParkingLotCard.vue';
import api from '../services/api';

export default {
  components: {
    ParkingLotCard,
  },
  data() {
    return {
      parkingLots: [],
      userReservations: [],
    };
  },
  created() {
    this.fetchParkingLots();
    this.fetchUserReservations();
  },
  methods: {
    async fetchParkingLots() {
      try {
        const response = await api.getParkingLots();
        this.parkingLots = response.data;
      } catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },
    async fetchUserReservations() {
      try {
        const response = await api.getUserReservations();
        this.userReservations = response.data;
      } catch (error) {
        console.error('Error fetching user reservations:', error);
      }
    },
    async reserveSpot(lotId) {
      try {
        const response = await api.reserveParkingSpot(lotId);
        this.userReservations.push(response.data);
        this.fetchParkingLots(); // Refresh parking lots
      } catch (error) {
        console.error('Error reserving parking spot:', error);
      }
    },
    async releaseSpot(reservationId) {
      try {
        await api.releaseParkingSpot(reservationId);
        this.userReservations = this.userReservations.filter(res => res.id !== reservationId);
        this.fetchParkingLots(); // Refresh parking lots
      } catch (error) {
        console.error('Error releasing parking spot:', error);
      }
    },
  },
};
</script>

<style scoped>
.user-dashboard {
  padding: 20px;
}

.parking-lots, .reservations {
  margin-bottom: 20px;
}

.parking-lot-card {
  margin: 10px 0;
}
</style>