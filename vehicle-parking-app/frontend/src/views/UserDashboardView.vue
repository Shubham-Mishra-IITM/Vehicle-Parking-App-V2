<template>
    <!-- Personalized Welcome Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex align-items-center justify-content-between">
          <div>
            <h1 class="mb-1">{{ getPersonalizedGreeting() }}, {{ authStore.user?.full_name || authStore.user?.username || 'User' }}! 👋</h1>
            <p class="text-muted mb-0">{{ getWelcomeMessage() }}</p>
          </div>
          <div class="text-end">
            <small class="text-muted">{{ getCurrentDate() }}</small>
          </div>
        </div>
      </div>
    </div>
   
    <!-- Authentication Check -->
    <div v-if="!authStore.isAuthenticated" class="alert alert-warning">
      <h4>Authentication Required</h4>
      <p>Please log in to access your dashboard.</p>
      <p><strong>Debug:</strong> Auth state: {{ authStore.isAuthenticated }}, User: {{ authStore.user?.username || 'None' }}</p>
      <router-link to="/login" class="btn btn-primary">Go to Login</router-link>
    </div>
    
    <!-- Dashboard Content (only show if authenticated) -->
    <div v-else>
      <!-- Loading indicator -->
      <div v-if="loading" class="text-center mb-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Loading dashboard data...</p>
      </div>
      
      <div v-else>
        <!-- Enhanced Stats with Dashboard Data -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card text-white bg-info">
              <div class="card-body">
                <h5 class="card-title">Active Reservations</h5>
                <h3>{{ activeReservations.length }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-white bg-success">
              <div class="card-body">
                <h5 class="card-title">Total Reservations</h5>
                <h3>{{ totalReservations }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-white bg-warning">
              <div class="card-body">
                <h5 class="card-title">Completed</h5>
                <h3>{{ completedReservations.length }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-white bg-primary">
              <div class="card-body">
                <h5 class="card-title">Total Spent</h5>
                <h3>{{ formatINR(totalSpent) }}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="row mb-4">
          <!-- Show message if no chart data available -->
          <div v-if="!hasChartData" class="col-12 mb-3">
            <div class="alert alert-info">
              <h6 class="mb-2">📊 No Chart Data Available</h6>
              <p class="mb-0">
                Charts will appear once you have completed some parking reservations. 
                Start by booking a parking spot, mark it as "parked" when you arrive, 
                and "released" when you leave to generate data for the charts.
              </p>
            </div>
          </div>
          
          <!-- Monthly Activity Chart -->
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Monthly Activity</h5>
              </div>
              <div class="card-body" style="height: 400px;">
                <canvas id="monthlyChart"></canvas>
              </div>
            </div>
          </div>
          
          <!-- Status Distribution Pie Chart -->
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Reservation Status</h5>
              </div>
              <div class="card-body" style="height: 400px;">
                <canvas id="statusChart"></canvas>
              </div>
            </div>
          </div>
        </div>

                <!-- Additional Charts -->
        <div class="row mb-4">
          <!-- Parking Lot Usage -->
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Parking Lot Usage</h5>
              </div>
              <div class="card-body" style="height: 350px;">
                <canvas id="lotUsageChart"></canvas>
              </div>
            </div>
          </div>
          
          <!-- Weekly Spending Trend -->
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Weekly Spending</h5>
              </div>
              <div class="card-body" style="height: 350px;">
                <canvas id="weeklyChart"></canvas>
              </div>
            </div>
          </div>
      </div>
      
      <!-- Quick Stats -->
    <div class="row mb-4" v-if="false">
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
            <form @submit.prevent="reserveParkingLot">
              <div class="row">
                <div class="col-md-4">
                  <label class="form-label">Location</label>
                  <select class="form-select" v-model="bookingForm.parking_lot_id" required>
                    <option value="">Select Location</option>
                    <option v-for="lot in availableLots" :key="lot.id" :value="lot.id">
                      {{ lot.prime_location_name }} - {{ formatINR(lot.price) }}/hr ({{ lot.available_spots }} spots available)
                    </option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Vehicle Number</label>
                  <input type="text" class="form-control" v-model="bookingForm.vehicle_number" 
                         placeholder="e.g., ABC-123" required>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Expected Duration (hrs)</label>
                  <select class="form-select" v-model="bookingForm.hours" required>
                    <option value="">Select Hours</option>
                    <option v-for="hour in [1,2,3,4,5,6,8,12,24]" :key="hour" :value="hour">
                      {{ hour }} hour{{ hour > 1 ? 's' : '' }}
                    </option>
                  </select>
                </div>
                <div class="col-md-2">
                  <label class="form-label">&nbsp;</label>
                  <button type="submit" class="btn btn-primary w-100" :disabled="booking">
                    <span v-if="booking" class="spinner-border spinner-border-sm me-1"></span>
                    Reserve Spot
                  </button>
                </div>
              </div>
            </form>
            
            <div class="mt-3">
              <small class="text-muted">
                <strong>Note:</strong> The first available parking spot will be automatically assigned to you. 
                After reservation, you'll need to mark it as "Parked" when you park and "Released" when you leave.
              </small>
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
            <div v-if="currentActiveReservations.length === 0" class="text-center text-muted">
              No active reservations found
            </div>
            <div v-else>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Location</th>
                      <th>Spot</th>
                      <th>Vehicle</th>
                      <th>Reserved At</th>
                      <th>Parked At</th>
                      <th>Duration</th>
                      <th>Cost per hour</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in currentActiveReservations" :key="reservation.id">
                      <td>{{ reservation.parking_lot?.prime_location_name }}</td>
                      <td>{{ reservation.parking_spot?.spot_number }}</td>
                      <td>{{ reservation.vehicle_number }}</td>
                      <td>{{ formatDate(reservation.created_at) }}</td>
                      <td>{{ reservation.parking_timestamp ? formatDate(reservation.parking_timestamp) : '-' }}</td>
                      <td>{{ reservation.parking_duration ? reservation.parking_duration.toFixed(2) + ' hrs' : '-' }}</td>
                      <td>{{ formatINR(reservation.parking_cost) }}</td>
                      <td>
                        <span :class="getStatusBadgeClass(reservation.status)">
                          {{ getStatusText(reservation.status) }}
                        </span>
                      </td>
                      <td>
                        <!-- Mark as Parked (for reserved status) -->
                        <button v-if="reservation.status === 'reserved'" 
                                class="btn btn-sm btn-success me-1" 
                                @click="markAsParked(reservation.id)">
                          Mark Parked
                        </button>
                        
                        <!-- Mark as Released (for active status) -->
                        <button v-if="reservation.status === 'active'" 
                                class="btn btn-sm btn-warning me-1" 
                                @click="markAsReleased(reservation.id)">
                          Mark Released
                        </button>
                        
                        <!-- Cancel (for reserved status) -->
                        <button v-if="reservation.status === 'reserved'" 
                                class="btn btn-sm btn-danger" 
                                @click="cancelReservation(reservation.id)">
                          Cancel
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

    <!-- My Reservation History -->
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
                      <th>Reserved At</th>
                      <th>Location</th>
                      <th>Vehicle Number</th>
                      <th>Parked At</th>
                      <th>Released At</th>
                      <th>Duration</th>
                      <th>Total Cost</th>
                      <th>Status</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in reservationHistory" :key="reservation.id">
                      <td>{{ formatDate(reservation.created_at) }}</td>
                      <td>{{ reservation.parking_lot?.prime_location_name }}</td>
                      <td>{{ reservation.vehicle_number }}</td>
                      <td>{{ reservation.parking_timestamp ? formatDate(reservation.parking_timestamp) : '-' }}</td>
                      <td>{{ reservation.leaving_timestamp ? formatDate(reservation.leaving_timestamp) : '-' }}</td>
                      <td>{{ reservation.parking_duration ? reservation.parking_duration.toFixed(2) + ' hrs' : '-' }}</td>
                      <td>{{ formatINR(reservation.parking_cost) }}</td>
                      <td>
                        <span :class="getStatusBadgeClass(reservation.status)">
                          {{ getStatusText(reservation.status) }}
                        </span>
                      </td>
                      <td>
                        <button v-if="reservation.parking_cost > 0" 
                                class="btn btn-sm btn-outline-info" 
                                @click="showCostBreakdown(reservation)"
                                title="View cost breakdown"
                                style="font-size: 0.8rem; padding: 0.25rem 0.5rem;">
                          <i class="fas fa-info-circle"></i> Details
                        </button>
                        <span v-else class="text-muted">-</span>
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

    <!-- Cost Breakdown Modal -->
    <div class="modal fade" id="costBreakdownModal" tabindex="-1" aria-labelledby="costBreakdownModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="costBreakdownModalLabel">
              <i class="fas fa-calculator"></i> Cost Breakdown Details
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedReservation">
            <div class="row mb-3">
              <div class="col-12">
                <div class="card border-primary">
                  <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                      <i class="fas fa-map-marker-alt"></i> {{ selectedReservation.parking_lot?.prime_location_name }}
                    </h6>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-6">
                        <p><strong>Vehicle:</strong> {{ selectedReservation.vehicle_number }}</p>
                        <p><strong>Spot:</strong> {{ selectedReservation.parking_spot?.spot_number || 'N/A' }}</p>
                      </div>
                      <div class="col-md-6">
                        <p><strong>Reserved:</strong> {{ formatDate(selectedReservation.created_at) }}</p>
                        <p><strong>Status:</strong> 
                          <span :class="getStatusBadgeClass(selectedReservation.status)">
                            {{ getStatusText(selectedReservation.status) }}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <div class="card border-success">
                  <div class="card-header bg-success text-white">
                    <h6 class="mb-0"><i class="fas fa-clock"></i> Timing Details</h6>
                  </div>
                  <div class="card-body">
                    <p><strong>Parked At:</strong><br>
                      {{ selectedReservation.parking_timestamp ? formatDate(selectedReservation.parking_timestamp) : 'Not parked' }}
                    </p>
                    <p><strong>Released At:</strong><br>
                      {{ selectedReservation.leaving_timestamp ? formatDate(selectedReservation.leaving_timestamp) : 'Not released' }}
                    </p>
                    <p><strong>Total Duration:</strong><br>
                      <span class="h5 text-primary">{{ selectedReservation.parking_duration ? selectedReservation.parking_duration.toFixed(2) : '0' }} hours</span>
                    </p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card border-info">
                  <div class="card-header bg-info text-white">
                    <h6 class="mb-0"><i class="fas fa-rupee-sign"></i> Cost Calculation</h6>
                  </div>
                  <div class="card-body">
                    <div class="cost-breakdown">
                      <div class="d-flex justify-content-between mb-2">
                        <span>Hourly Rate:</span>
                        <span>{{ formatINR(selectedReservation.parking_lot?.price || 0) }}/hr</span>
                      </div>
                      <div class="d-flex justify-content-between mb-2">
                        <span>Duration:</span>
                        <span>{{ selectedReservation.parking_duration ? selectedReservation.parking_duration.toFixed(2) : '0' }} hrs</span>
                      </div>
                      <hr>
                      <div class="d-flex justify-content-between mb-2">
                        <span>Subtotal:</span>
                        <span>{{ formatINR(calculateSubtotal(selectedReservation)) }}</span>
                      </div>
                      <div class="d-flex justify-content-between mb-2 text-muted">
                        <small>Taxes & Fees:</small>
                        <small>{{ formatINR(0) }}</small>
                      </div>
                      <hr>
                      <div class="d-flex justify-content-between">
                        <strong class="h5">Total Cost:</strong>
                        <strong class="h5 text-success">{{ formatINR(selectedReservation.parking_cost) }}</strong>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="row" v-if="selectedReservation.status === 'completed'">
              <div class="col-12">
                <div class="alert alert-success">
                  <i class="fas fa-check-circle"></i>
                  <strong>Payment Status:</strong> Completed successfully
                  <br>
                  <small>This reservation has been completed and payment has been processed.</small>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="downloadReceipt" v-if="selectedReservation?.status === 'completed'">
              <i class="fas fa-download"></i> Download Receipt
            </button>
          </div>
        </div>
      </div>
    </div>

    </div> <!-- End of authenticated section -->
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { formatINR } from '@/utils/currency'
import api from '@/services/api'
import { Chart } from 'chart.js/auto'

export default {
  name: 'UserDashboardView',
  setup() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const availableLots = ref([])
    const reservations = ref([])
    const dashboardData = ref(null)
    const loading = ref(true)
    const booking = ref(false)
    const selectedReservation = ref(null)
    
    const bookingForm = ref({
      parking_lot_id: '',
      vehicle_number: '',
      hours: ''
    })

    const activeReservations = computed(() => 
      reservations.value.filter(r => r.status === 'active')
    )

    const currentActiveReservations = computed(() => 
      reservations.value.filter(r => r.status === 'active' || r.status === 'reserved')
    )

    const allReservations = computed(() => reservations.value)

    const reservationHistory = computed(() => 
      reservations.value.filter(r => r.status === 'completed' || r.status === 'cancelled' || r.status === 'expired')
    )

    const completedReservations = computed(() => 
      reservations.value.filter(r => r.status === 'completed')
    )

    const totalReservations = computed(() => reservations.value.length)

    const totalSpent = computed(() => {
      return reservations.value
        .filter(r => r.status === 'completed' && r.parking_cost)
        .reduce((sum, r) => sum + parseFloat(r.parking_cost || 0), 0)
    })

    const hasChartData = computed(() => {
      // Check if we have backend dashboard data
      if (dashboardData.value) {
        const hasBackendData = (
          (dashboardData.value.monthly_stats && dashboardData.value.monthly_stats.length > 0) ||
          (dashboardData.value.weekly_stats && dashboardData.value.weekly_stats.length > 0) ||
          (dashboardData.value.status_distribution && dashboardData.value.status_distribution.length > 0) ||
          (dashboardData.value.lot_usage_stats && dashboardData.value.lot_usage_stats.length > 0)
        )
        
        if (hasBackendData) return true
      }
      
      // Check if we have frontend reservations data to create charts
      return reservations.value.length > 0
    })

    const fetchDashboardData = async () => {
      try {
        console.log('Fetching dashboard data...')
        const response = await api.get('/user/dashboard')
        console.log('Dashboard data response:', response.data)
        dashboardData.value = response.data
        
        // Validate the data structure
        if (!response.data) {
          console.error('Dashboard API returned empty data')
          return
        }
        
        console.log('Dashboard data structure:')
        console.log('- statistics:', response.data.statistics)
        console.log('- monthly_stats:', response.data.monthly_stats)
        console.log('- weekly_stats:', response.data.weekly_stats)
        console.log('- status_distribution:', response.data.status_distribution)
        console.log('- lot_usage_stats:', response.data.lot_usage_stats)
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        console.error('Error details:', err.response?.data)
        
        // Set empty data structure if API fails
        dashboardData.value = {
          statistics: { total_reservations: 0, completed_reservations: 0, total_spent: 0 },
          monthly_stats: [],
          weekly_stats: [],
          status_distribution: [],
          lot_usage_stats: []
        }
      }
    }

    const fetchAvailableLots = async () => {
      try {
        console.log('Fetching available lots...')
        const response = await api.get('/parking/lots')
        console.log('Available lots response:', response.data)
        availableLots.value = response.data
      } catch (err) {
        console.error('Error fetching lots:', err)
      }
    }

    const fetchReservations = async () => {
      try {
        console.log('Fetching user reservations...')
        const response = await api.get('/user/reservations')
        console.log('Reservations response:', response.data)
        reservations.value = response.data
      } catch (err) {
        console.error('Error fetching reservations:', err)
      }
    }

    const reserveParkingLot = async () => {
      if (!bookingForm.value.parking_lot_id || !bookingForm.value.vehicle_number || !bookingForm.value.hours) return
      
      booking.value = true
      try {
        const lot = availableLots.value.find(l => l.id === parseInt(bookingForm.value.parking_lot_id))
        const estimatedCost = lot.price * parseInt(bookingForm.value.hours)
        
        const reservationData = {
          parking_lot_id: parseInt(bookingForm.value.parking_lot_id),
          vehicle_number: bookingForm.value.vehicle_number,
          parking_duration: parseInt(bookingForm.value.hours),
          parking_cost: estimatedCost
        }

        await api.post('/user/reservations', reservationData)
        
        // Reset form and refresh data
        bookingForm.value = { parking_lot_id: '', vehicle_number: '', hours: '' }
        await Promise.all([
          fetchReservations(),
          fetchAvailableLots(),
          fetchDashboardData()
        ])
        
        // Refresh charts with new data
        await createCharts()
        
        notificationStore.success('Parking spot reserved successfully! Please mark as "occupied" when you park your vehicle.')
      } catch (err) {
        console.error('Error reserving parking:', err)
        const errorMessage = err.response?.data?.error || 'Failed to reserve parking spot'
        notificationStore.error(errorMessage)
      } finally {
        booking.value = false
      }
    }

    const markAsParked = async (reservationId) => {
      try {
        await api.put(`/user/reservations/${reservationId}/park`)
        await Promise.all([
          fetchReservations(),
          fetchDashboardData()
        ])
        
        // Refresh charts with new data
        await createCharts()
        
        notificationStore.success('Parking marked as occupied. Timing started!')
      } catch (err) {
        console.error('Error marking as parked:', err)
        const errorMessage = err.response?.data?.error || 'Failed to mark as parked'
        notificationStore.error(errorMessage)
      }
    }

    const markAsReleased = async (reservationId) => {
      if (!confirm('Are you sure you have left the parking spot? This will calculate the final cost.')) return
      
      try {
        const response = await api.put(`/user/reservations/${reservationId}/release`)
        await Promise.all([
          fetchReservations(),
          fetchAvailableLots(),
          fetchDashboardData()
        ])
        
        // Refresh charts with new data
        await createCharts()
        
        const data = response.data
        notificationStore.success(`Parking released successfully! Duration: ${data.total_duration_hours}h, Final cost: ${formatINR(data.final_cost)}`)
      } catch (err) {
        console.error('Error marking as released:', err)
        const errorMessage = err.response?.data?.error || 'Failed to mark as released'
        notificationStore.error(errorMessage)
      }
    }

    const cancelReservation = async (reservationId) => {
      if (!confirm('Are you sure you want to cancel this reservation?')) return
      
      try {
        await api.delete(`/user/reservations/${reservationId}`)
        await Promise.all([
          fetchReservations(),
          fetchAvailableLots(),
          fetchDashboardData()
        ])
        
        // Refresh charts with new data
        await createCharts()
        
        notificationStore.success('Reservation cancelled successfully!')
      } catch (err) {
        console.error('Error cancelling reservation:', err)
        const errorMessage = err.response?.data?.error || 'Failed to cancel reservation'
        notificationStore.error(errorMessage)
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString()
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'reserved': 'badge bg-info',
        'active': 'badge bg-primary',
        'completed': 'badge bg-success',
        'cancelled': 'badge bg-danger',
        'expired': 'badge bg-warning'
      }
      return classes[status] || 'badge bg-secondary'
    }

    const getStatusText = (status) => {
      const texts = {
        'reserved': 'Reserved',
        'active': 'Parked',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'expired': 'Expired'
      }
      return texts[status] || status
    }

    const getPersonalizedGreeting = () => {
      const hour = new Date().getHours()
      if (hour < 12) {
        return 'Good Morning'
      } else if (hour < 18) {
        return 'Good Afternoon'
      } else {
        return 'Good Evening'
      }
    }

    const getWelcomeMessage = () => {
      const messages = [
        "Welcome back to your parking dashboard!",
        "Ready to manage your parking reservations?",
        "Let's make parking easier for you today!",
        "Your parking management hub awaits!",
        "Hope you're having a great day!"
      ]
      
      // Use a simple method to get a consistent message for the day
      const today = new Date().getDate()
      const messageIndex = today % messages.length
      return messages[messageIndex]
    }

    const getCurrentDate = () => {
      const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }
      return new Date().toLocaleDateString('en-US', options)
    }

    const showCostBreakdown = (reservation) => {
      console.log('showCostBreakdown called with:', reservation)
      selectedReservation.value = reservation
      
      // Use nextTick to ensure the reactive data is updated
      nextTick(() => {
        const modalElement = document.getElementById('costBreakdownModal')
        console.log('Modal element found:', modalElement)
        
        if (modalElement) {
          try {
            // Try different approaches to show modal
            if (window.bootstrap && window.bootstrap.Modal) {
              console.log('Using window.bootstrap.Modal')
              const modal = new window.bootstrap.Modal(modalElement)
              modal.show()
            } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              console.log('Using bootstrap.Modal')
              const modal = new bootstrap.Modal(modalElement)
              modal.show()
            } else {
              console.log('Bootstrap Modal not available, using manual approach')
              // Fallback: manually show modal
              modalElement.classList.add('show', 'd-block')
              modalElement.style.display = 'block'
              modalElement.setAttribute('aria-modal', 'true')
              modalElement.setAttribute('role', 'dialog')
              
              // Add backdrop
              let backdrop = document.getElementById('modal-backdrop-custom')
              if (!backdrop) {
                backdrop = document.createElement('div')
                backdrop.className = 'modal-backdrop fade show'
                backdrop.id = 'modal-backdrop-custom'
                document.body.appendChild(backdrop)
              }
              
              // Add body class
              document.body.classList.add('modal-open')
              document.body.style.overflow = 'hidden'
              
              // Handle close buttons
              const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close')
              closeButtons.forEach(btn => {
                btn.onclick = (e) => {
                  e.preventDefault()
                  console.log('Closing modal manually')
                  modalElement.classList.remove('show', 'd-block')
                  modalElement.style.display = 'none'
                  modalElement.removeAttribute('aria-modal')
                  modalElement.removeAttribute('role')
                  
                  const backdrop = document.getElementById('modal-backdrop-custom')
                  if (backdrop) {
                    backdrop.remove()
                  }
                  document.body.classList.remove('modal-open')
                  document.body.style.overflow = ''
                }
              })
              
              // Handle backdrop click
              backdrop.onclick = () => {
                closeButtons[0]?.click()
              }
            }
          } catch (error) {
            console.error('Error showing modal:', error)
            // Ultimate fallback: simple alert
            const costInfo = `
Cost Details for ${reservation.vehicle_number}

Location: ${reservation.parking_lot?.prime_location_name || 'N/A'}
Spot: ${reservation.parking_spot?.spot_number || 'N/A'}
Duration: ${reservation.parking_duration ? reservation.parking_duration.toFixed(2) : '0'} hours
Hourly Rate: ${formatINR(reservation.parking_lot?.price || 0)}/hr
Total Cost: ${formatINR(reservation.parking_cost || 0)}
Status: ${getStatusText(reservation.status)}

Parked: ${reservation.parking_timestamp ? formatDate(reservation.parking_timestamp) : 'N/A'}
Released: ${reservation.leaving_timestamp ? formatDate(reservation.leaving_timestamp) : 'N/A'}
            `
            alert(costInfo)
          }
        } else {
          console.error('Modal element not found')
          alert('Unable to show cost details. Please try again.')
        }
      })
    }

    const calculateSubtotal = (reservation) => {
      if (!reservation.parking_duration || !reservation.parking_lot?.price) {
        return 0
      }
      return reservation.parking_duration * reservation.parking_lot.price
    }

    const downloadReceipt = () => {
      if (!selectedReservation.value) return
      
      // Create a simple receipt text
      const reservation = selectedReservation.value
      const receiptContent = `
PARKING RECEIPT
=====================================

Location: ${reservation.parking_lot?.prime_location_name}
Vehicle: ${reservation.vehicle_number}
Spot: ${reservation.parking_spot?.spot_number || 'N/A'}

TIMING DETAILS:
Reserved At: ${formatDate(reservation.created_at)}
Parked At: ${reservation.parking_timestamp ? formatDate(reservation.parking_timestamp) : 'N/A'}
Released At: ${reservation.leaving_timestamp ? formatDate(reservation.leaving_timestamp) : 'N/A'}
Duration: ${reservation.parking_duration ? reservation.parking_duration.toFixed(2) : '0'} hours

COST BREAKDOWN:
Hourly Rate: ${formatINR(reservation.parking_lot?.price || 0)}/hr
Duration: ${reservation.parking_duration ? reservation.parking_duration.toFixed(2) : '0'} hrs
Subtotal: ${formatINR(calculateSubtotal(reservation))}
Taxes & Fees: ${formatINR(0)}
Total: ${formatINR(reservation.parking_cost)}

Status: ${getStatusText(reservation.status)}
Generated: ${new Date().toLocaleString()}

Thank you for using our parking service!
=====================================
      `
      
      // Create and download the receipt file
      const blob = new Blob([receiptContent], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `parking-receipt-${reservation.id}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      notificationStore.success('Receipt downloaded successfully!')
    }

    const createCharts = async () => {
      await nextTick() // Wait for DOM to be updated
      
      if (!dashboardData.value) {
        console.log('No dashboard data available for charts')
        return
      }
      
      console.log('Dashboard data for charts:', dashboardData.value)
      
      // Destroy existing charts before creating new ones
      try {
        const chartIds = ['monthlyChart', 'statusChart', 'lotUsageChart', 'weeklyChart']
        chartIds.forEach(id => {
          const canvas = document.getElementById(id)
          if (canvas) {
            const existingChart = Chart.getChart(canvas)
            if (existingChart) {
              existingChart.destroy()
            }
          }
        })
      } catch (error) {
        console.log('Error destroying existing charts:', error)
      }
      
      // Wait a bit more to ensure elements are rendered
      setTimeout(() => {
        try {
          console.log('Creating charts...')
          createMonthlyChart()
          createStatusChart()
          createLotUsageChart()
          createWeeklyChart()
          console.log('Charts created successfully')
        } catch (error) {
          console.error('Error creating charts:', error)
        }
      }, 100)
    }

    const createMonthlyChart = () => {
      try {
        const ctx = document.getElementById('monthlyChart')
        if (!ctx) {
          console.error('Monthly chart canvas not found')
          return
        }
        
        // Use backend data first, then fallback to frontend data
        let monthlyStats = dashboardData.value?.monthly_stats
        
        if (!monthlyStats || monthlyStats.length === 0) {
          // Create monthly stats from frontend reservations data
          const monthlyData = {}
          reservations.value.forEach(r => {
            if (r.created_at) {
              const date = new Date(r.created_at)
              const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
              
              if (!monthlyData[monthKey]) {
                monthlyData[monthKey] = { reservations: 0, amount_spent: 0 }
              }
              
              monthlyData[monthKey].reservations++
              if (r.status === 'completed' && r.parking_cost) {
                monthlyData[monthKey].amount_spent += parseFloat(r.parking_cost || 0)
              }
            }
          })
          
          monthlyStats = Object.entries(monthlyData).map(([month, data]) => ({
            month,
            reservations: data.reservations,
            amount_spent: data.amount_spent
          })).sort((a, b) => a.month.localeCompare(b.month))
          
          if (monthlyStats.length === 0) {
            console.log('No monthly stats data available, creating empty chart')
            // Create empty chart
            new Chart(ctx, {
              type: 'line',
              data: {
                labels: ['No Data'],
                datasets: [
                  {
                    label: 'Reservations',
                    data: [0],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                  }
                ]
              },
              options: {
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: 'No data available'
                  }
                }
              }
            })
            return
          }
        }

        const chartData = [...monthlyStats] // Keep chronological order (oldest to newest)
        console.log('Creating monthly chart with data:', chartData)
        
        // Calculate better scaling for dual axes
        const maxReservations = Math.max(...chartData.map(stat => stat.reservations))
        const maxSpent = Math.max(...chartData.map(stat => stat.amount_spent))
        
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: chartData.map(stat => {
              // Format month labels better (e.g., "2025-07" -> "Jul 2025")
              const [year, month] = stat.month.split('-')
              const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
              return `${monthNames[parseInt(month) - 1]} ${year}`
            }),
            datasets: [
              {
                label: 'Reservations',
                data: chartData.map(stat => stat.reservations),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                borderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: 'rgb(75, 192, 192)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                tension: 0.3,
                fill: true
              },
              {
                label: 'Amount Spent (₹)',
                data: chartData.map(stat => stat.amount_spent),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 3,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: 'rgb(255, 99, 132)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                yAxisID: 'y1',
                tension: 0.3,
                fill: true
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
              mode: 'index',
              intersect: false,
            },
            plugins: {
              legend: {
                display: true,
                position: 'top',
                labels: {
                  usePointStyle: true,
                  padding: 20
                }
              },
              tooltip: {
                callbacks: {
                  afterLabel: function(context) {
                    if (context.datasetIndex === 1) {
                      return `Total: ₹${context.parsed.y.toLocaleString()}`
                    }
                    return `Total: ${context.parsed.y} reservations`
                  }
                }
              }
            },
            scales: {
              x: {
                display: true,
                title: {
                  display: true,
                  text: 'Month',
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                grid: {
                  display: true,
                  color: 'rgba(0,0,0,0.1)'
                }
              },
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true,
                max: maxReservations > 0 ? Math.ceil(maxReservations * 1.2) : 10,
                title: {
                  display: true,
                  text: 'Number of Reservations',
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                grid: {
                  display: true,
                  color: 'rgba(75, 192, 192, 0.2)'
                },
                ticks: {
                  stepSize: 1,
                  callback: function(value) {
                    return Number.isInteger(value) ? value : null
                  }
                }
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                max: maxSpent > 0 ? Math.ceil(maxSpent * 1.2) : 100,
                title: {
                  display: true,
                  text: 'Amount Spent (₹)',
                  font: {
                    size: 14,
                    weight: 'bold'
                  }
                },
                grid: {
                  drawOnChartArea: false,
                  color: 'rgba(255, 99, 132, 0.2)'
                },
                ticks: {
                  callback: function(value) {
                    return '₹' + value.toLocaleString()
                  }
                }
              }
            }
          }
        })
        console.log('Monthly chart created successfully')
      } catch (error) {
        console.error('Error creating monthly chart:', error)
      }
    }

    const createStatusChart = () => {
      try {
        const ctx = document.getElementById('statusChart')
        if (!ctx) {
          console.error('Status chart canvas not found')
          return
        }
        
        // Use backend data first, then fallback to frontend data
        let statusData = dashboardData.value?.status_distribution
        
        if (!statusData || statusData.length === 0) {
          // Create status distribution from frontend reservations data
          const statusCounts = {}
          reservations.value.forEach(r => {
            statusCounts[r.status] = (statusCounts[r.status] || 0) + 1
          })
          
          statusData = Object.entries(statusCounts).map(([status, count]) => ({
            status,
            count
          }))
          
          if (statusData.length === 0) {
            console.log('No status distribution data available, creating empty chart')
            // Create empty chart
            new Chart(ctx, {
              type: 'pie',
              data: {
                labels: ['No Data'],
                datasets: [{
                  data: [1],
                  backgroundColor: ['#6c757d'],
                  borderWidth: 2,
                  borderColor: '#fff'
                }]
              },
              options: {
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                  title: {
                    display: true,
                    text: 'No data available'
                  }
                }
              }
            })
            return
          }
        }

        console.log('Creating status chart with data:', statusData)
        
        const colors = {
          'reserved': '#17a2b8',
          'active': '#007bff',
          'completed': '#28a745',
          'cancelled': '#dc3545',
          'expired': '#ffc107'
        }

        new Chart(ctx, {
          type: 'pie',
          data: {
            labels: statusData.map(item => getStatusText(item.status)),
            datasets: [{
              data: statusData.map(item => item.count),
              backgroundColor: statusData.map(item => colors[item.status] || '#6c757d'),
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'bottom',
              },
              title: {
                display: false
              }
            }
          }
        })
        console.log('Status chart created successfully')
      } catch (error) {
        console.error('Error creating status chart:', error)
      }
    }

    const createLotUsageChart = () => {
      try {
        const ctx = document.getElementById('lotUsageChart')
        if (!ctx) {
          console.error('Lot usage chart canvas not found')
          return
        }
        
        // Use backend data first, then fallback to frontend data
        let lotStats = dashboardData.value?.lot_usage_stats
        
        if (!lotStats || lotStats.length === 0) {
          // Create lot usage stats from frontend reservations and lots data
          const lotUsage = {}
          reservations.value.forEach(r => {
            if (r.parking_lot?.prime_location_name) {
              const lotName = r.parking_lot.prime_location_name
              lotUsage[lotName] = (lotUsage[lotName] || 0) + 1
            }
          })
          
          lotStats = Object.entries(lotUsage).map(([lot_name, reservations]) => ({
            lot_name,
            reservations
          }))
          
          if (lotStats.length === 0) {
            console.log('No lot usage stats data available, creating empty chart')
            // Create empty chart
            new Chart(ctx, {
              type: 'bar',
              data: {
                labels: ['No Data'],
                datasets: [{
                  label: 'Reservations',
                  data: [0],
                  backgroundColor: 'rgba(54, 162, 235, 0.8)',
                  borderColor: 'rgba(54, 162, 235, 1)',
                  borderWidth: 1
                }]
              },
              options: {
                responsive: true,
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Number of Reservations'
                    }
                  }
                },
                plugins: {
                  legend: {
                    display: false
                  },
                  title: {
                    display: true,
                    text: 'No data available'
                  }
                }
              }
            })
            return
          }
        }

        console.log('Creating lot usage chart with data:', lotStats)

        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: lotStats.map(stat => stat.lot_name),
            datasets: [{
              label: 'Reservations',
              data: lotStats.map(stat => stat.reservations),
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Reservations'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Parking Lots'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        })
        console.log('Lot usage chart created successfully')
      } catch (error) {
        console.error('Error creating lot usage chart:', error)
      }
    }

    const createWeeklyChart = () => {
      try {
        const ctx = document.getElementById('weeklyChart')
        if (!ctx) {
          console.error('Weekly chart canvas not found')
          return
        }
        
        // Use backend data first, then fallback to frontend data
        let weeklyStats = dashboardData.value?.weekly_stats
        
        if (!weeklyStats || weeklyStats.length === 0) {
          // Create weekly stats from frontend reservations data
          const weeklyData = {}
          const now = new Date()
          
          reservations.value.forEach(r => {
            if (r.created_at) {
              const date = new Date(r.created_at)
              const timeDiff = now.getTime() - date.getTime()
              const weeksDiff = Math.floor(timeDiff / (1000 * 3600 * 24 * 7))
              
              if (weeksDiff <= 4) { // Only include last 4 weeks
                const weekKey = `Week ${4 - weeksDiff}`
                
                if (!weeklyData[weekKey]) {
                  weeklyData[weekKey] = { reservations: 0, amount_spent: 0 }
                }
                
                weeklyData[weekKey].reservations++
                if (r.status === 'completed' && r.parking_cost) {
                  weeklyData[weekKey].amount_spent += parseFloat(r.parking_cost || 0)
                }
              }
            }
          })
          
          // Create array with all 4 weeks, filling missing weeks with 0
          weeklyStats = []
          for (let i = 4; i >= 1; i--) {
            const weekKey = `Week ${i}`
            weeklyStats.push({
              week: weekKey,
              reservations: weeklyData[weekKey]?.reservations || 0,
              amount_spent: weeklyData[weekKey]?.amount_spent || 0
            })
          }
          
          if (weeklyStats.every(w => w.amount_spent === 0 && w.reservations === 0)) {
            console.log('No weekly stats data available, creating empty chart')
            // Create empty chart
            new Chart(ctx, {
              type: 'bar',
              data: {
                labels: ['No Data'],
                datasets: [{
                  label: 'Amount Spent (₹)',
                  data: [0],
                  backgroundColor: 'rgba(255, 206, 86, 0.8)',
                  borderColor: 'rgba(255, 206, 86, 1)',
                  borderWidth: 1
                }]
              },
              options: {
                responsive: true,
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Amount Spent (₹)'
                    }
                  }
                },
                plugins: {
                  legend: {
                    display: false
                  },
                  title: {
                    display: true,
                    text: 'No data available'
                  }
                }
              }
            })
            return
          }
        }

        const chartData = [...weeklyStats].reverse() // Show oldest to newest
        console.log('Creating weekly chart with data:', chartData)

        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: chartData.map(stat => stat.week),
            datasets: [{
              label: 'Amount Spent (₹)',
              data: chartData.map(stat => stat.amount_spent),
              backgroundColor: 'rgba(255, 206, 86, 0.8)',
              borderColor: 'rgba(255, 206, 86, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Amount Spent (₹)'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Week'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        })
        console.log('Weekly chart created successfully')
      } catch (error) {
        console.error('Error creating weekly chart:', error)
      }
    }

    onMounted(async () => {
      console.log('UserDashboard mounted. Auth state:', authStore.isAuthenticated, authStore.user)
      
      // Ensure Bootstrap is available
      if (typeof window !== 'undefined') {
        // Wait for Bootstrap to be fully loaded
        setTimeout(() => {
          if (window.bootstrap) {
            console.log('Bootstrap loaded successfully')
          } else {
            console.warn('Bootstrap not loaded, modal functionality may not work')
          }
        }, 100)
      }
      
      if (authStore.isAuthenticated) {
        console.log('User is authenticated, fetching data...')
        loading.value = true
        try {
          await Promise.all([
            fetchAvailableLots(),
            fetchReservations(),
            fetchDashboardData()
          ])
          console.log('Dashboard data loaded successfully')
          // Create charts after data is loaded
          await createCharts()
        } catch (error) {
          console.error('UserDashboard: Error during data fetch:', error)
        } finally {
          loading.value = false
        }
      } else {
        console.log('User is not authenticated')
        loading.value = false
      }
    })

    return {
      authStore,
      availableLots,
      reservations,
      dashboardData,
      loading,
      selectedReservation,
      activeReservations,
      currentActiveReservations,
      allReservations,
      reservationHistory,
      completedReservations,
      totalReservations,
      totalSpent,
      hasChartData,
      booking,
      bookingForm,
      reserveParkingLot,
      markAsParked,
      markAsReleased,
      cancelReservation,
      formatDate,
      getStatusBadgeClass,
      getStatusText,
      getPersonalizedGreeting,
      getWelcomeMessage,
      getCurrentDate,
      showCostBreakdown,
      calculateSubtotal,
      downloadReceipt,
      createCharts,
      formatINR
    }
  }
}
</script>

<style scoped>
.cost-breakdown {
  font-size: 0.95rem;
}

.cost-breakdown hr {
  margin: 0.5rem 0;
  border-color: #dee2e6;
}

.modal-header {
  border-bottom: 2px solid #007bff;
}

.card.border-primary .card-header {
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.card.border-success .card-header {
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.card.border-info .card-header {
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.btn-outline-info {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .cost-breakdown {
    font-size: 0.9rem;
  }
}
</style>
