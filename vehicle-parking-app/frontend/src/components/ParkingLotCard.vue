<template>
  <div class="parking-lot-card">
    <h3>{{ parkingLot.prime_location_name }}</h3>
    <p>Price: ${{ parkingLot.price }}</p>
    <p>Address: {{ parkingLot.address }}</p>
    <p>Pin Code: {{ parkingLot.pin_code }}</p>
    <p>Available Spots: {{ availableSpots }}</p>
    <button @click="reserveSpot" :disabled="availableSpots === 0">Reserve Spot</button>
  </div>
</template>

<script>
export default {
  props: {
    parkingLot: {
      type: Object,
      required: true
    },
    reservedSpots: {
      type: Array,
      required: true
    }
  },
  computed: {
    availableSpots() {
      return this.parkingLot.number_of_spots - this.reservedSpots.length;
    }
  },
  methods: {
    reserveSpot() {
      this.$emit('reserve', this.parkingLot.id);
    }
  }
}
</script>

<style scoped>
.parking-lot-card {
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 15px;
  margin: 10px;
  text-align: center;
}
.parking-lot-card h3 {
  margin: 0;
}
.parking-lot-card button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
}
.parking-lot-card button:disabled {
  background-color: #ccc;
}
</style>