<template>
  <div class="user-view">
    <h1>User Dashboard</h1>
    <div>
      <h2>Available Parking Lots</h2>
      <div v-for="lot in parkingLots" :key="lot.id" class="parking-lot">
        <ParkingLotCard :lot="lot" @reserve="reserveSpot" />
      </div>
    </div>
    <div>
      <h2>Your Reservations</h2>
      <ul>
        <li v-for="reservation in userReservations" :key="reservation.id">
          Spot ID: {{ reservation.spot_id }} - 
          Status: {{ reservation.status }} - 
          Parked At: {{ reservation.parking_timestamp }} - 
          Leaving At: {{ reservation.leaving_timestamp }}
          <button @click="releaseSpot(reservation.id)">Release Spot</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import ParkingLotCard from '../components/ParkingLotCard.vue';
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
        const response = await api.get('/parking-lots');
        this.parkingLots = response.data;
      } catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },
    async fetchUserReservations() {
      try {
        const response = await api.get('/user/reservations');
        this.userReservations = response.data;
      } catch (error) {
        console.error('Error fetching user reservations:', error);
      }
    },
    async reserveSpot(lotId) {
      try {
        const response = await api.post('/user/reserve', { lotId });
        this.userReservations.push(response.data);
        this.fetchParkingLots(); // Refresh parking lots
      } catch (error) {
        console.error('Error reserving spot:', error);
      }
    },
    async releaseSpot(reservationId) {
      try {
        await api.post('/user/release', { reservationId });
        this.userReservations = this.userReservations.filter(res => res.id !== reservationId);
        this.fetchParkingLots(); // Refresh parking lots
      } catch (error) {
        console.error('Error releasing spot:', error);
      }
    },
  },
};
</script>

<style scoped>
.user-view {
  padding: 20px;
}
.parking-lot {
  margin-bottom: 20px;
}
</style>