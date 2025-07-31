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
            <h5 class="mb-0">{{ lot?.prime_location_name || 'Unknown Location' }}</h5>
            <span :class="lot?.is_active ? 'badge bg-success' : 'badge bg-danger'">
              {{ lot?.is_active ? 'Open' : 'Closed' }}
            </span>
          </div>
          <div class="card-body">
            <p class="text-muted small">{{ lot?.address || 'Address not available' }}</p>
            <p class="text-muted small">PIN: {{ lot?.pin_code || 'N/A' }}</p>
            
            <div class="row mb-3">
              <div class="col-6">
                <small class="text-muted">Price per hour</small>
                <div class="h5 text-primary">{{ formatINR(lot?.price || 0) }}</div>
              </div>
              <div class="col-6">
                <small class="text-muted">Available spots</small>
                <div class="h5" :class="(lot?.available_spots || 0) > 0 ? 'text-success' : 'text-danger'">
                  {{ lot?.available_spots || 0 }} / {{ lot?.number_of_spots || 0 }}
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
                  {{ authStore.isAuthenticated ? 'Quick Book' : 'Login to Book' }}
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
                  <p><strong>Address:</strong> {{ selectedLot?.address || 'N/A' }}</p>
                  <p><strong>PIN Code:</strong> {{ selectedLot?.pin_code || 'N/A' }}</p>
                  <p><strong>Total Spots:</strong> {{ selectedLot?.number_of_spots || 0 }}</p>
                  <p><strong>Available:</strong> {{ selectedLot?.available_spots || 0 }}</p>
                </div>
                <div class="col-md-6">
                  <h6>Pricing & Status</h6>
                                    <p><strong>Price per Hour:</strong> {{ formatINR(selectedLot.price) }}</p>
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
              {{ authStore.isAuthenticated ? 'Book Parking' : 'Login to Book' }}
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
                    {{ hour }} hour{{ hour > 1 ? 's' : '' }} - {{ formatINR(calculateQuickBookCost(hour)) }}
                  </option>
                </select>
              </div>
              <div class="alert alert-info">
                <strong>Total Cost:</strong> {{ formatINR(calculateQuickBookCost(quickBookForm.hours || 0)) }}
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
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { formatINR } from '@/utils/currency'
import api from '@/services/api'

export default {
  name: 'ParkingLotsView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
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
      if (!parkingLots.value || !Array.isArray(parkingLots.value)) {
        return []
      }

      let filtered = parkingLots.value.filter(lot => {
        if (!lot) return false
        
        const locationName = lot.prime_location_name || ''
        const address = lot.address || ''
        const searchTerm = (searchQuery.value || '').toLowerCase()
        
        return locationName.toLowerCase().includes(searchTerm) ||
               address.toLowerCase().includes(searchTerm)
      })

      // Sort the results
      filtered.sort((a, b) => {
        if (!a || !b) return 0
        
        switch (sortBy.value) {
          case 'price':
            return (a.price || 0) - (b.price || 0)
          case 'availability':
            return (b.available_spots || 0) - (a.available_spots || 0)
          default: // name
            const nameA = a.prime_location_name || ''
            const nameB = b.prime_location_name || ''
            return nameA.localeCompare(nameB)
        }
      })

      return filtered
    })

    const fetchParkingLots = async () => {
      loading.value = true
      try {
        const response = await api.get('/parking/lots')
        
        // Validate that response.data is an array
        if (!Array.isArray(response.data)) {
          console.error('Expected array but got:', typeof response.data, response.data)
          error.value = 'Invalid data format received from server'
          parkingLots.value = []
          return
        }
        
        parkingLots.value = response.data
        
      } catch (err) {
        error.value = 'Failed to load parking lots'
        console.error('Error fetching parking lots:', err)
        parkingLots.value = []
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
        const response = await api.get(`/parking/lots/${lot.id}`)
        const lotDetails = response.data
        spotDetails.value = [...(lotDetails.available_spots_details || []), ...(lotDetails.occupied_spots_details || [])]
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
      // Check if user is authenticated
      if (!authStore.isAuthenticated) {
        notificationStore.error('Please login to proceed for booking')
        router.push('/login')
        return
      }
      
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
      if (!quickBookLot.value || !hours) return 0
      return quickBookLot.value.price * hours
    }

    const confirmQuickBook = async () => {
      if (!quickBookForm.value.vehicle_number || !quickBookForm.value.hours) return
      
      // Double-check authentication before making API call
      if (!authStore.isAuthenticated) {
        notificationStore.error('Please login to proceed for booking')
        router.push('/login')
        return
      }
      
      booking.value = true
      try {
        // First get available spots for this lot
        const spotsResponse = await api.get(`/parking/lots/${quickBookLot.value.id}`)
        const lotDetails = spotsResponse.data
        const availableSpots = lotDetails.available_spots_details || []
        
        if (availableSpots.length === 0) {
          notificationStore.warning('No spots available at this location')
          return
        }

        // Book the first available spot
        const spot = availableSpots[0]
        const cost = calculateQuickBookCost(quickBookForm.value.hours)
        
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
        
        // Check for authentication/authorization errors first
        if (err.response?.status === 401 || err.response?.status === 403) {
          notificationStore.error('Please login to proceed for booking')
          router.push('/login')
          return
        }
        
        // Show specific error message from backend
        const errorMessage = err.response?.data?.error || 'Failed to book parking spot'
        
        // Check if user already has active reservation
        if (errorMessage.toLowerCase().includes('active reservation')) {
          notificationStore.error('You already have an active parking reservation. Please go to your dashboard to manage it or cancel it before booking a new spot.')
          setTimeout(() => {
            router.push('/dashboard')
          }, 3000) // Give user time to read the message
        } else {
          notificationStore.error(errorMessage)
        }
      } finally {
        booking.value = false
      }
    }

    const bookFromDetails = () => {
      // Check if user is authenticated
      if (!authStore.isAuthenticated) {
        notificationStore.error('Please login to proceed for booking')
        router.push('/login')
        return
      }
      
      closeDetailsModal()
      quickBook(selectedLot.value)
    }

    onMounted(() => {
      fetchParkingLots()
    })

    return {
      authStore,
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
      bookFromDetails,
      formatINR
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
