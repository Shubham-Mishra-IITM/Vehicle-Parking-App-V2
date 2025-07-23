<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Browse Parking Locations</h1>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search by location..." 
          v-model="searchQuery"
          style="width: 300px;">
        <select class="form-select" v-model="sortBy" style="width: 200px;">
          <option value="name">Sort by Name</option>
          <option value="price">Sort by Price</option>
          <option value="availability">Sort by Availability</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Parking Lots Grid -->
    <div v-else class="row">
      <div v-for="lot in filteredLots" :key="lot.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ lot.prime_location_name }}</h5>
            <span :class="lot.is_active ? 'badge bg-success' : 'badge bg-danger'">
              {{ lot.is_active ? 'Open' : 'Closed' }}
            </span>
          </div>
          <div class="card-body">
            <p class="text-muted small">{{ lot.address }}</p>
            <p class="text-muted small">PIN: {{ lot.pin_code }}</p>
            
            <div class="row mb-3">
              <div class="col-6">
                <small class="text-muted">Price per hour</small>
                <div class="h5 text-primary">${{ lot.price }}</div>
              </div>
              <div class="col-6">
                <small class="text-muted">Available spots</small>
                <div class="h5" :class="lot.available_spots > 0 ? 'text-success' : 'text-danger'">
                  {{ lot.available_spots }} / {{ lot.number_of_spots }}
                </div>
              </div>
            </div>

            <div class="progress mb-3" style="height: 8px;">
              <div 
                class="progress-bar" 
                :class="getOccupancyColor(lot)"
                :style="{ width: getOccupancyPercentage(lot) + '%' }"
              ></div>
            </div>

            <p v-if="lot.description" class="card-text small">
              {{ lot.description }}
            </p>

            <div class="row mt-3">
              <div class="col-6">
                <button 
                  class="btn btn-outline-primary btn-sm w-100" 
                  @click="viewDetails(lot)"
                >
                  View Details
                </button>
              </div>
              <div class="col-6">
                <button 
                  class="btn btn-primary btn-sm w-100" 
                  @click="quickBook(lot)"
                  :disabled="!lot.is_active || lot.available_spots === 0"
                >
                  Quick Book
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && filteredLots.length === 0" class="text-center text-muted">
      <h4>No parking lots found</h4>
      <p>Try adjusting your search criteria.</p>
    </div>

    <!-- Parking Lot Details Modal -->
    <div class="modal fade" :class="{ show: showDetailsModal }" style="display: block;" v-if="showDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedLot?.prime_location_name }}</h5>
            <button type="button" class="btn-close" @click="closeDetailsModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedLot">
              <div class="row mb-4">
                <div class="col-md-6">
                  <h6>Location Information</h6>
                  <p><strong>Address:</strong> {{ selectedLot.address }}</p>
                  <p><strong>PIN Code:</strong> {{ selectedLot.pin_code }}</p>
                  <p><strong>Total Spots:</strong> {{ selectedLot.number_of_spots }}</p>
                  <p><strong>Available:</strong> {{ selectedLot.available_spots }}</p>
                </div>
                <div class="col-md-6">
                  <h6>Pricing & Status</h6>
                  <p><strong>Price per Hour:</strong> ${{ selectedLot.price }}</p>
                  <p><strong>Status:</strong> 
                    <span :class="selectedLot.is_active ? 'badge bg-success' : 'badge bg-danger'">
                      {{ selectedLot.is_active ? 'Open' : 'Closed' }}
                    </span>
                  </p>
                  <p><strong>Occupancy:</strong> {{ getOccupancyPercentage(selectedLot) }}%</p>
                </div>
              </div>

              <div v-if="selectedLot.description" class="mb-4">
                <h6>Description</h6>
                <p>{{ selectedLot.description }}</p>
              </div>

              <!-- Available Spots -->
              <div v-if="spotDetails.length > 0">
                <h6>Available Parking Spots</h6>
                <div class="row">
                  <div v-for="spot in spotDetails" :key="spot.id" class="col-md-3 col-sm-4 col-6 mb-2">
                    <div class="card text-center" :class="spot.status === 'A' ? 'border-success' : 'border-danger'">
                      <div class="card-body py-2">
                        <small>Spot {{ spot.spot_number }}</small>
                        <div>{{ spot.spot_type }}</div>
                        <span :class="spot.status === 'A' ? 'badge bg-success' : 'badge bg-danger'">
                          {{ spot.status === 'A' ? 'Available' : 'Occupied' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDetailsModal">Close</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="bookFromDetails"
              :disabled="!selectedLot?.is_active || selectedLot?.available_spots === 0"
            >
              Book Parking
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showDetailsModal"></div>

    <!-- Quick Book Modal -->
    <div class="modal fade" :class="{ show: showQuickBookModal }" style="display: block;" v-if="showQuickBookModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Quick Book - {{ quickBookLot?.prime_location_name }}</h5>
            <button type="button" class="btn-close" @click="closeQuickBookModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="confirmQuickBook">
              <div class="mb-3">
                <label class="form-label">Vehicle Number</label>
                <input type="text" class="form-control" v-model="quickBookForm.vehicle_number" 
                       placeholder="e.g., ABC-123" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Parking Duration</label>
                <select class="form-select" v-model="quickBookForm.hours" required>
                  <option value="">Select Hours</option>
                  <option v-for="hour in [1,2,3,4,5,6,8,12,24]" :key="hour" :value="hour">
                    {{ hour }} hour{{ hour > 1 ? 's' : '' }} - ${{ calculateQuickBookCost(hour) }}
                  </option>
                </select>
              </div>
              <div class="alert alert-info">
                <strong>Total Cost:</strong> ${{ calculateQuickBookCost(quickBookForm.hours || 0) }}
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeQuickBookModal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="confirmQuickBook"
              :disabled="!quickBookForm.vehicle_number || !quickBookForm.hours || booking"
            >
              <span v-if="booking" class="spinner-border spinner-border-sm me-1"></span>
              Confirm Booking
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showQuickBookModal"></div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api'

export default {
  name: 'ParkingLotsView',
  setup() {
    const router = useRouter()
    const notificationStore = useNotificationStore()
    const loading = ref(true)
    const error = ref('')
    const parkingLots = ref([])
    const searchQuery = ref('')
    const sortBy = ref('name')
    const showDetailsModal = ref(false)
    const showQuickBookModal = ref(false)
    const selectedLot = ref(null)
    const quickBookLot = ref(null)
    const spotDetails = ref([])
    const booking = ref(false)
    
    const quickBookForm = ref({
      vehicle_number: '',
      hours: ''
    })

    const filteredLots = computed(() => {
      let filtered = parkingLots.value.filter(lot => 
        lot.prime_location_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        lot.address.toLowerCase().includes(searchQuery.value.toLowerCase())
      )

      // Sort the results
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'price':
            return a.price - b.price
          case 'availability':
            return b.available_spots - a.available_spots
          default: // name
            return a.prime_location_name.localeCompare(b.prime_location_name)
        }
      })

      return filtered
    })

    const fetchParkingLots = async () => {
      loading.value = true
      try {
        const response = await api.get('/parking/lots')
        parkingLots.value = response.data
      } catch (err) {
        error.value = 'Failed to load parking lots'
        console.error('Error fetching parking lots:', err)
      } finally {
        loading.value = false
      }
    }

    const getOccupancyPercentage = (lot) => {
      if (lot.number_of_spots === 0) return 0
      return Math.round(((lot.number_of_spots - lot.available_spots) / lot.number_of_spots) * 100)
    }

    const getOccupancyColor = (lot) => {
      const percentage = getOccupancyPercentage(lot)
      if (percentage < 50) return 'bg-success'
      if (percentage < 80) return 'bg-warning'
      return 'bg-danger'
    }

    const viewDetails = async (lot) => {
      selectedLot.value = lot
      try {
        const response = await api.get(`/parking/lots/${lot.id}/spots`)
        spotDetails.value = response.data
      } catch (err) {
        console.error('Error fetching spot details:', err)
        spotDetails.value = []
      }
      showDetailsModal.value = true
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      selectedLot.value = null
      spotDetails.value = []
    }

    const quickBook = (lot) => {
      quickBookLot.value = lot
      quickBookForm.value = { vehicle_number: '', hours: '' }
      showQuickBookModal.value = true
    }

    const closeQuickBookModal = () => {
      showQuickBookModal.value = false
      quickBookLot.value = null
      quickBookForm.value = { vehicle_number: '', hours: '' }
    }

    const calculateQuickBookCost = (hours) => {
      if (!quickBookLot.value || !hours) return '0.00'
      return (quickBookLot.value.price * hours).toFixed(2)
    }

    const confirmQuickBook = async () => {
      if (!quickBookForm.value.vehicle_number || !quickBookForm.value.hours) return
      
      booking.value = true
      try {
        // First get available spots for this lot
        const spotsResponse = await api.get(`/parking/lots/${quickBookLot.value.id}/available-spots`)
        const availableSpots = spotsResponse.data
        
        if (availableSpots.length === 0) {
          notificationStore.warning('No spots available at this location')
          return
        }

        // Book the first available spot
        const spot = availableSpots[0]
        const cost = parseFloat(calculateQuickBookCost(quickBookForm.value.hours))
        
        const reservationData = {
          parking_lot_id: quickBookLot.value.id,
          parking_spot_id: spot.id,
          vehicle_number: quickBookForm.value.vehicle_number,
          parking_duration: parseInt(quickBookForm.value.hours),
          parking_cost: cost
        }

        await api.post('/user/reservations', reservationData)
        
        closeQuickBookModal()
        await fetchParkingLots() // Refresh the data
        
        notificationStore.success(`Parking spot ${spot.spot_number} booked successfully!`)
        router.push('/dashboard')
      } catch (err) {
        console.error('Error booking spot:', err)
        notificationStore.error('Failed to book parking spot')
      } finally {
        booking.value = false
      }
    }

    const bookFromDetails = () => {
      closeDetailsModal()
      quickBook(selectedLot.value)
    }

    onMounted(() => {
      fetchParkingLots()
    })

    return {
      loading,
      error,
      parkingLots,
      filteredLots,
      searchQuery,
      sortBy,
      showDetailsModal,
      showQuickBookModal,
      selectedLot,
      quickBookLot,
      spotDetails,
      booking,
      quickBookForm,
      getOccupancyPercentage,
      getOccupancyColor,
      viewDetails,
      closeDetailsModal,
      quickBook,
      closeQuickBookModal,
      calculateQuickBookCost,
      confirmQuickBook,
      bookFromDetails
    }
  }
}
</script>

<style scoped>
.progress {
  height: 8px;
}

.card-header h5 {
  font-size: 1.1rem;
}

.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
