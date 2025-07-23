<template>
  <div>
    <h1>User Dashboard</h1>
    
    <!-- Quick Stats -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Active Reservations</h5>
            <h3>{{ activeReservations.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Total Reservations</h5>
            <h3>{{ totalReservations }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Available Lots</h5>
            <h3>{{ availableLots.length }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Book New Parking -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Book New Parking</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="searchAvailableSpots">
              <div class="row">
                <div class="col-md-4">
                  <label class="form-label">Location</label>
                  <select class="form-select" v-model="bookingForm.parking_lot_id" required>
                    <option value="">Select Location</option>
                    <option v-for="lot in availableLots" :key="lot.id" :value="lot.id">
                      {{ lot.prime_location_name }} - ${{ lot.price }}/hr
                    </option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Vehicle Number</label>
                  <input type="text" class="form-control" v-model="bookingForm.vehicle_number" 
                         placeholder="e.g., ABC-123" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Parking Hours</label>
                  <select class="form-select" v-model="bookingForm.hours" required>
                    <option value="">Select Hours</option>
                    <option v-for="hour in [1,2,3,4,5,6,8,12,24]" :key="hour" :value="hour">
                      {{ hour }} hour{{ hour > 1 ? 's' : '' }}
                    </option>
                  </select>
                </div>
                <div class="col-md-2">
                  <label class="form-label">&nbsp;</label>
                  <button type="submit" class="btn btn-primary w-100" :disabled="searching">
                    <span v-if="searching" class="spinner-border spinner-border-sm me-1"></span>
                    Search Spots
                  </button>
                </div>
              </div>
            </form>
            
            <!-- Available Spots -->
            <div v-if="availableSpots.length > 0" class="mt-4">
              <h6>Available Parking Spots:</h6>
              <div class="row">
                <div v-for="spot in availableSpots" :key="spot.id" class="col-md-3 mb-2">
                  <div class="card">
                    <div class="card-body text-center">
                      <h5>Spot {{ spot.spot_number }}</h5>
                      <p class="mb-2">{{ spot.spot_type }}</p>
                      <button class="btn btn-success btn-sm" @click="bookSpot(spot)">
                        Book for ${{ calculateCost(spot) }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Reservations -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Active Reservations</h5>
          </div>
          <div class="card-body">
            <div v-if="activeReservations.length === 0" class="text-center text-muted">
              No active reservations
            </div>
            <div v-else>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Location</th>
                      <th>Spot</th>
                      <th>Vehicle</th>
                      <th>Arrival</th>
                      <th>Duration</th>
                      <th>Cost</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in activeReservations" :key="reservation.id">
                      <td>{{ reservation.parking_lot?.prime_location_name }}</td>
                      <td>{{ reservation.parking_spot?.spot_number }}</td>
                      <td>{{ reservation.vehicle_number }}</td>
                      <td>{{ formatDate(reservation.arrival_timestamp) }}</td>
                      <td>{{ reservation.parking_duration }} hrs</td>
                      <td>${{ reservation.parking_cost }}</td>
                      <td>
                        <span class="badge bg-primary">{{ reservation.status }}</span>
                      </td>
                      <td>
                        <button v-if="reservation.status === 'active'" 
                                class="btn btn-sm btn-danger" 
                                @click="cancelReservation(reservation.id)">
                          Cancel
                        </button>
                        <button v-if="reservation.status === 'active'" 
                                class="btn btn-sm btn-success ms-1" 
                                @click="extendReservation(reservation)">
                          Extend
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reservation History -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Reservation History</h5>
          </div>
          <div class="card-body">
            <div v-if="reservationHistory.length === 0" class="text-center text-muted">
              No past reservations
            </div>
            <div v-else>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Location</th>
                      <th>Vehicle</th>
                      <th>Duration</th>
                      <th>Cost</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in reservationHistory" :key="reservation.id">
                      <td>{{ formatDate(reservation.arrival_timestamp) }}</td>
                      <td>{{ reservation.parking_lot?.prime_location_name }}</td>
                      <td>{{ reservation.vehicle_number }}</td>
                      <td>{{ reservation.parking_duration }} hrs</td>
                      <td>${{ reservation.parking_cost }}</td>
                      <td>
                        <span :class="getStatusBadgeClass(reservation.status)">
                          {{ reservation.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Extend Reservation Modal -->
    <div class="modal fade" :class="{ show: showExtendModal }" style="display: block;" v-if="showExtendModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Extend Reservation</h5>
            <button type="button" class="btn-close" @click="closeExtendModal"></button>
          </div>
          <div class="modal-body">
            <p>Current reservation ends at: {{ extendingReservation?.leaving_timestamp }}</p>
            <div class="mb-3">
              <label class="form-label">Additional Hours</label>
              <select class="form-select" v-model="extendForm.hours" required>
                <option value="">Select Hours</option>
                <option v-for="hour in [1,2,3,4,5,6]" :key="hour" :value="hour">
                  {{ hour }} hour{{ hour > 1 ? 's' : '' }} - ${{ calculateExtendCost(hour) }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeExtendModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="confirmExtend" :disabled="extending">
              <span v-if="extending" class="spinner-border spinner-border-sm me-1"></span>
              Extend Reservation
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showExtendModal"></div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api'

export default {
  name: 'UserDashboardView',
  setup() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const availableLots = ref([])
    const reservations = ref([])
    const availableSpots = ref([])
    const searching = ref(false)
    const showExtendModal = ref(false)
    const extendingReservation = ref(null)
    const extending = ref(false)
    
    const bookingForm = ref({
      parking_lot_id: '',
      vehicle_number: '',
      hours: ''
    })
    
    const extendForm = ref({
      hours: ''
    })

    const activeReservations = computed(() => 
      reservations.value.filter(r => r.status === 'active')
    )

    const reservationHistory = computed(() => 
      reservations.value.filter(r => r.status !== 'active')
    )

    const totalReservations = computed(() => reservations.value.length)

    const fetchAvailableLots = async () => {
      try {
        const response = await api.get('/parking/lots')
        availableLots.value = response.data
      } catch (err) {
        console.error('Error fetching lots:', err)
      }
    }

    const fetchReservations = async () => {
      try {
        const response = await api.get('/user/reservations')
        reservations.value = response.data
      } catch (err) {
        console.error('Error fetching reservations:', err)
      }
    }

    const searchAvailableSpots = async () => {
      if (!bookingForm.value.parking_lot_id || !bookingForm.value.hours) return
      
      searching.value = true
      try {
        const response = await api.get(`/parking/lots/${bookingForm.value.parking_lot_id}/available-spots`)
        availableSpots.value = response.data
      } catch (err) {
        console.error('Error searching spots:', err)
        alert('Failed to search available spots')
      } finally {
        searching.value = false
      }
    }

    const calculateCost = (spot) => {
      const lot = availableLots.value.find(l => l.id === parseInt(bookingForm.value.parking_lot_id))
      return lot ? (lot.price * parseInt(bookingForm.value.hours)).toFixed(2) : '0.00'
    }

    const calculateExtendCost = (hours) => {
      if (!extendingReservation.value) return '0.00'
      const lot = availableLots.value.find(l => l.id === extendingReservation.value.parking_lot_id)
      return lot ? (lot.price * hours).toFixed(2) : '0.00'
    }

    const bookSpot = async (spot) => {
      try {
        const lot = availableLots.value.find(l => l.id === parseInt(bookingForm.value.parking_lot_id))
        const cost = parseFloat(calculateCost(spot))
        
        const reservationData = {
          parking_lot_id: parseInt(bookingForm.value.parking_lot_id),
          parking_spot_id: spot.id,
          vehicle_number: bookingForm.value.vehicle_number,
          parking_duration: parseInt(bookingForm.value.hours),
          parking_cost: cost
        }

        await api.post('/user/reservations', reservationData)
        
        // Reset form and refresh data
        bookingForm.value = { parking_lot_id: '', vehicle_number: '', hours: '' }
        availableSpots.value = []
        await fetchReservations()
        
        notificationStore.success('Parking spot booked successfully!')
      } catch (err) {
        console.error('Error booking spot:', err)
        notificationStore.error('Failed to book parking spot')
      }
    }

    const cancelReservation = async (reservationId) => {
      if (!confirm('Are you sure you want to cancel this reservation?')) return
      
      try {
        await api.delete(`/user/reservations/${reservationId}`)
        await fetchReservations()
        notificationStore.success('Reservation cancelled successfully!')
      } catch (err) {
        console.error('Error cancelling reservation:', err)
        notificationStore.error('Failed to cancel reservation')
      }
    }

    const extendReservation = (reservation) => {
      extendingReservation.value = reservation
      extendForm.value.hours = ''
      showExtendModal.value = true
    }

    const closeExtendModal = () => {
      showExtendModal.value = false
      extendingReservation.value = null
      extendForm.value.hours = ''
    }

    const confirmExtend = async () => {
      if (!extendForm.value.hours) return
      
      extending.value = true
      try {
        const additionalCost = parseFloat(calculateExtendCost(parseInt(extendForm.value.hours)))
        
        await api.put(`/user/reservations/${extendingReservation.value.id}/extend`, {
          additional_hours: parseInt(extendForm.value.hours),
          additional_cost: additionalCost
        })
        
        closeExtendModal()
        await fetchReservations()
        notificationStore.success('Reservation extended successfully!')
      } catch (err) {
        console.error('Error extending reservation:', err)
        notificationStore.error('Failed to extend reservation')
      } finally {
        extending.value = false
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'active': 'badge bg-primary',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-danger',
        'expired': 'badge bg-warning'
      }
      return classes[status] || 'badge bg-secondary'
    }

    onMounted(() => {
      fetchAvailableLots()
      fetchReservations()
    })

    return {
      authStore,
      availableLots,
      reservations,
      activeReservations,
      reservationHistory,
      totalReservations,
      availableSpots,
      searching,
      bookingForm,
      showExtendModal,
      extendingReservation,
      extending,
      extendForm,
      searchAvailableSpots,
      calculateCost,
      calculateExtendCost,
      bookSpot,
      cancelReservation,
      extendReservation,
      closeExtendModal,
      confirmExtend,
      formatDate,
      getStatusBadgeClass
    }
  }
}
</script>
