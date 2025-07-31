<template>
  <div class="container-fluid">
    <!-- Header with logout button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Admin Dashboard</h1>
      <div class="d-flex align-items-center">
        <span class="me-3 text-muted">
          Welcome, <strong>{{ authStore.user?.username }}</strong>
        </span>
        <button class="btn btn-outline-danger" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
  </div>
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else>
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card text-white bg-primary mb-3">
            <div class="card-body">
              <h5 class="card-title">Total Users</h5>
              <h2 class="card-text">{{ stats.users_count || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-success mb-3">
            <div class="card-body">
              <h5 class="card-title">Parking Lots</h5>
              <h2 class="card-text">{{ stats.parking_lots_count || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-info mb-3">
            <div class="card-body">
              <h5 class="card-title">Total Reservations</h5>
              <h2 class="card-text">{{ stats.reservations_count || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-warning mb-3">
            <div class="card-body">
              <h5 class="card-title">Active Reservations</h5>
              <h2 class="card-text">{{ stats.active_reservations || 0 }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <ul class="nav nav-tabs mb-4" id="adminTabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="analytics-tab" data-bs-toggle="tab" data-bs-target="#analytics" 
                  type="button" role="tab" aria-controls="analytics" aria-selected="true">
            <i class="fas fa-chart-bar"></i> Analytics
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="lots-tab" data-bs-toggle="tab" data-bs-target="#lots" 
                  type="button" role="tab" aria-controls="lots" aria-selected="false">
            <i class="fas fa-building"></i> Parking Lots
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="spots-tab" data-bs-toggle="tab" data-bs-target="#spots" 
                  type="button" role="tab" aria-controls="spots" aria-selected="false">
            <i class="fas fa-car"></i> Spot Monitor
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="users-tab" data-bs-toggle="tab" data-bs-target="#users" 
                  type="button" role="tab" aria-controls="users" aria-selected="false">
            <i class="fas fa-users"></i> Users
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" id="reservations-tab" data-bs-toggle="tab" data-bs-target="#reservations" 
                  type="button" role="tab" aria-controls="reservations" aria-selected="false">
            <i class="fas fa-calendar-check"></i> Reservations
          </button>
        </li>
      </ul>

      <!-- Tab Content -->
      <div class="tab-content" id="adminTabContent">
        <!-- Analytics Tab -->
        <div class="tab-pane fade show active" id="analytics" role="tabpanel" aria-labelledby="analytics-tab">
          <div class="row">
            <!-- Parking Statistics -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header">
                  <h5><i class="fas fa-chart-pie"></i> Parking Spot Status</h5>
                </div>
                <div class="card-body">
                  <canvas ref="parkingStatusChart" height="300"></canvas>
                </div>
              </div>
            </div>

            <!-- Revenue Summary -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header">
                  <h5><i class="fas fa-dollar-sign"></i> Daily Revenue</h5>
                </div>
                <div class="card-body">
                  <canvas ref="revenueChart" height="300"></canvas>
                </div>
              </div>
            </div>

            <!-- Parking Lot Utilization -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header">
                  <h5><i class="fas fa-chart-bar"></i> Parking Lot Utilization</h5>
                </div>
                <div class="card-body">
                  <canvas ref="utilizationChart" height="300"></canvas>
                </div>
              </div>
            </div>

            <!-- Weekly Revenue Trend -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header">
                  <h5><i class="fas fa-chart-line"></i> Weekly Revenue Trend</h5>
                </div>
                <div class="card-body">
                  <canvas ref="weeklyRevenueChart" height="300"></canvas>
                </div>
              </div>
            </div>

            <!-- Peak Hours Analysis -->
            <div class="col-lg-12 mb-4">
              <div class="card">
                <div class="card-header">
                  <h5><i class="fas fa-clock"></i> Peak Hours Analysis</h5>
                </div>
                <div class="card-body">
                  <canvas ref="peakHoursChart" height="200"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Parking Lots Tab -->
        <div class="tab-pane fade" id="lots" role="tabpanel" aria-labelledby="lots-tab">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Parking Lots Management</h5>
              <button class="btn btn-primary" @click="showCreateModal = true">
                <i class="bi bi-plus"></i> Add New Parking Lot
              </button>
            </div>
            <div class="card-body">
              <div v-if="parkingLotsLoading" class="text-center">
                <div class="spinner-border" role="status"></div>
              </div>
              <div v-else>
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Price</th>
                        <th>Total Spots</th>
                        <th>Available</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="lot in parkingLots" :key="lot.id">
                        <td>{{ lot.prime_location_name }}</td>
                        <td>{{ lot.address }}</td>
                        <td>${{ lot.price }}</td>
                        <td>{{ lot.number_of_spots }}</td>
                        <td>{{ lot.available_spots }}</td>
                        <td>
                          <span :class="lot.is_active ? 'badge bg-success' : 'badge bg-danger'">
                            {{ lot.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                        <td>
                          <button class="btn btn-sm btn-outline-primary me-1" @click="editLot(lot)">
                            Edit
                          </button>
                          <button class="btn btn-sm btn-outline-danger" @click="deleteLot(lot.id)">
                            Delete
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
        
        <!-- Parking Spots Monitor Tab -->
        <div class="tab-pane fade" id="spots" role="tabpanel" aria-labelledby="spots-tab">
          <ParkingSpotMonitor />
        </div>
        
        <!-- Users Tab -->
        <div class="tab-pane fade" id="users" role="tabpanel" aria-labelledby="users-tab">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">User Management</h5>
            </div>
            <div class="card-body">
              <div v-if="usersLoading" class="text-center">
                <div class="spinner-border" role="status"></div>
              </div>
              <div v-else>
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Full Name</th>
                        <th>Phone</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="user in users" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.full_name || 'N/A' }}</td>
                        <td>{{ user.phone_number || 'N/A' }}</td>
                        <td>
                          <span :class="user.role === 'admin' ? 'badge bg-danger' : 'badge bg-primary'">
                            {{ user.role }}
                          </span>
                        </td>
                        <td>
                          <span :class="user.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                            {{ user.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                        <td>{{ formatDate(user.last_login) }}</td>
                        <td>
                          <button class="btn btn-sm btn-outline-info me-1" @click="viewUserStats(user.id)">
                            <i class="fas fa-chart-bar"></i> Stats
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
        
        <!-- Reservations Tab -->
        <div class="tab-pane fade" id="reservations" role="tabpanel" aria-labelledby="reservations-tab">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Reservation Management</h5>
            </div>
            <div class="card-body">
              <div v-if="reservationsLoading" class="text-center">
                <div class="spinner-border" role="status"></div>
              </div>
              <div v-else>
                <!-- Filter Controls -->
                <div class="row mb-3">
                  <div class="col-md-4">
                    <select v-model="reservationStatusFilter" @change="fetchReservations" class="form-select">
                      <option value="">All Statuses</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>
                
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>User</th>
                        <th>Vehicle</th>
                        <th>Spot</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Parking Time</th>
                        <th>Cost</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="reservation in reservations" :key="reservation.id">
                        <td>{{ reservation.id }}</td>
                        <td>{{ reservation.user_id }}</td>
                        <td>{{ reservation.vehicle_number }}</td>
                        <td>{{ reservation.spot_id }}</td>
                        <td>
                          <span :class="getStatusBadgeClass(reservation.status)">
                            {{ reservation.status }}
                          </span>
                        </td>
                        <td>{{ formatDate(reservation.created_at) }}</td>
                        <td>{{ formatDuration(reservation.current_duration_hours) }}</td>
                        <td>${{ reservation.parking_cost || 0 }}</td>
                        <td>
                          <button v-if="reservation.status === 'active'" 
                                  class="btn btn-sm btn-outline-success me-1" 
                                  @click="completeReservation(reservation.id)">
                            <i class="fas fa-check"></i> Complete
                          </button>
                          <button v-if="reservation.status !== 'completed'" 
                                  class="btn btn-sm btn-outline-danger" 
                                  @click="cancelReservation(reservation.id)">
                            <i class="fas fa-times"></i> Cancel
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <!-- Pagination -->
                <nav v-if="reservationPagination.pages > 1">
                  <ul class="pagination">
                    <li class="page-item" :class="{ disabled: reservationPagination.current_page === 1 }">
                      <button class="page-link" @click="changePage(reservationPagination.current_page - 1)">Previous</button>
                    </li>
                    <li v-for="page in reservationPagination.pages" :key="page" 
                        class="page-item" :class="{ active: page === reservationPagination.current_page }">
                      <button class="page-link" @click="changePage(page)">{{ page }}</button>
                    </li>
                    <li class="page-item" :class="{ disabled: reservationPagination.current_page === reservationPagination.pages }">
                      <button class="page-link" @click="changePage(reservationPagination.current_page + 1)">Next</button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Create/Edit Parking Lot Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" style="display: block;" v-if="showCreateModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingLot ? 'Edit' : 'Create' }} Parking Lot</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveParkingLot">
              <div class="mb-3">
                <label class="form-label">Location Name</label>
                <input type="text" class="form-control" v-model="lotForm.prime_location_name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="lotForm.address" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">PIN Code</label>
                <input type="text" class="form-control" v-model="lotForm.pin_code" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Price per Hour ($)</label>
                <input type="number" step="0.01" class="form-control" v-model="lotForm.price" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Number of Spots</label>
                <input type="number" class="form-control" v-model="lotForm.number_of_spots" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="lotForm.description"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveParkingLot" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editingLot ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showCreateModal"></div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import ParkingSpotMonitor from '@/components/ParkingSpotMonitor.vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Chart } from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

export default {
  name: 'AdminDashboardView',
  components: {
    ParkingSpotMonitor
  },
  setup() {
        // Stores
    const notificationStore = useNotificationStore()
    const authStore = useAuthStore()
    const router = useRouter()
    const loading = ref(true)
    const error = ref('')
    const stats = ref({})
    const parkingLots = ref([])
    const parkingLotsLoading = ref(false)
    const showCreateModal = ref(false)
    const editingLot = ref(null)
    const saving = ref(false)
    
    // Chart refs
    const parkingStatusChart = ref(null)
    const revenueChart = ref(null)
    const utilizationChart = ref(null)
    const weeklyRevenueChart = ref(null)
    const peakHoursChart = ref(null)
    
    // Analytics data
    const analyticsData = ref({})
    const chartsInitialized = ref(false)
    
    const lotForm = ref({
      prime_location_name: '',
      address: '',
      pin_code: '',
      price: '',
      number_of_spots: '',
      description: ''
    })

    // Users management
    const users = ref([])
    const usersLoading = ref(false)
    
    // Reservations management
    const reservations = ref([])
    const reservationsLoading = ref(false)
    const reservationStatusFilter = ref('')
    const reservationPagination = ref({
      current_page: 1,
      pages: 1,
      total: 0
    })

    const fetchStats = async () => {
      try {
        console.log('🔍 Fetching admin dashboard stats...')
        const response = await api.get('/admin/dashboard')
        console.log('✅ Dashboard response:', response.data)
        const data = response.data
        
        // Map the backend response to the expected format
        stats.value = {
          users_count: data.statistics.total_users,
          parking_lots_count: data.statistics.total_parking_lots,
          reservations_count: data.statistics.active_reservations,
          active_reservations: data.statistics.active_reservations
        }
        console.log('📊 Mapped stats:', stats.value)
      } catch (err) {
        console.error('❌ Error fetching dashboard stats:', err)
        console.error('❌ Error response:', err.response?.data)
        console.error('❌ Error status:', err.response?.status)
        
        if (err.response?.status === 401) {
          error.value = 'Authentication failed. Please login as admin.'
        } else if (err.response?.status === 403) {
          error.value = 'Access denied. Admin privileges required.'
        } else {
          error.value = `Failed to load dashboard stats: ${err.response?.data?.error || err.message}`
        }
      } finally {
        loading.value = false
      }
    }

    const fetchParkingLots = async () => {
      parkingLotsLoading.value = true
      try {
        console.log('🔍 Fetching parking lots...')
        const response = await api.get('/admin/parking-lots')
        console.log('✅ Parking lots response:', response.data)
        parkingLots.value = response.data
      } catch (err) {
        console.error('❌ Error fetching parking lots:', err)
        console.error('❌ Error response:', err.response?.data)
      } finally {
        parkingLotsLoading.value = false
      }
    }

    const editLot = (lot) => {
      editingLot.value = lot.id
      lotForm.value = {
        prime_location_name: lot.prime_location_name,
        address: lot.address,
        pin_code: lot.pin_code,
        price: lot.price.toString(),
        number_of_spots: lot.number_of_spots.toString(),
        description: lot.description || ''
      }
      showCreateModal.value = true
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingLot.value = null
      lotForm.value = {
        prime_location_name: '',
        address: '',
        pin_code: '',
        price: '',
        number_of_spots: '',
        description: ''
      }
    }

    const saveParkingLot = async () => {
      saving.value = true
      try {
        const formData = {
          ...lotForm.value,
          price: parseFloat(lotForm.value.price),
          number_of_spots: parseInt(lotForm.value.number_of_spots)
        }

        if (editingLot.value) {
          await api.put(`/admin/parking-lots/${editingLot.value}`, formData)
        } else {
          await api.post('/admin/parking-lots', formData)
        }

        closeModal()
        await fetchParkingLots()
        await fetchStats()
        
        const action = editingLot.value ? 'updated' : 'created'
        notificationStore.success(`Parking lot ${action} successfully!`)
      } catch (err) {
        console.error('Error saving parking lot:', err)
        notificationStore.error('Failed to save parking lot')
      } finally {
        saving.value = false
      }
    }

    const deleteLot = async (lotId) => {
      if (!confirm('Are you sure you want to delete this parking lot?')) return
      
      try {
        await api.delete(`/admin/parking-lots/${lotId}`)
        await fetchParkingLots()
        await fetchStats()
        notificationStore.success('Parking lot deleted successfully!')
      } catch (err) {
        console.error('Error deleting parking lot:', err)
        notificationStore.error('Failed to delete parking lot')
      }
    }

    // Users management functions
    const fetchUsers = async () => {
      usersLoading.value = true
      try {
        const response = await api.get('/admin/users')
        users.value = response.data
      } catch (err) {
        console.error('Error fetching users:', err)
        notificationStore.error('Failed to load users')
      } finally {
        usersLoading.value = false
      }
    }

    const viewUserStats = async (userId) => {
      try {
        const response = await api.get(`/admin/users/${userId}/statistics`)
        console.log('User stats:', response.data)
        notificationStore.info(`User has ${response.data.total_reservations} total reservations`)
      } catch (err) {
        console.error('Error fetching user stats:', err)
        notificationStore.error('Failed to load user statistics')
      }
    }

    // Reservations management functions
    const fetchReservations = async (page = 1) => {
      reservationsLoading.value = true
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          per_page: '25'
        })
        
        if (reservationStatusFilter.value) {
          params.append('status', reservationStatusFilter.value)
        }
        
        const response = await api.get(`/admin/reservations?${params}`)
        reservations.value = response.data.reservations
        reservationPagination.value = {
          current_page: response.data.current_page,
          pages: response.data.pages,
          total: response.data.total
        }
      } catch (err) {
        console.error('Error fetching reservations:', err)
        notificationStore.error('Failed to load reservations')
      } finally {
        reservationsLoading.value = false
      }
    }

    const completeReservation = async (reservationId) => {
      if (!confirm('Are you sure you want to complete this reservation?')) return
      
      try {
        await api.put(`/admin/reservations/${reservationId}/complete`)
        await fetchReservations(reservationPagination.value.current_page)
        notificationStore.success('Reservation completed successfully!')
      } catch (err) {
        console.error('Error completing reservation:', err)
        notificationStore.error('Failed to complete reservation')
      }
    }

    const cancelReservation = async (reservationId) => {
      if (!confirm('Are you sure you want to cancel this reservation?')) return
      
      try {
        await api.delete(`/admin/reservations/${reservationId}`)
        await fetchReservations(reservationPagination.value.current_page)
        notificationStore.success('Reservation cancelled successfully!')
      } catch (err) {
        console.error('Error cancelling reservation:', err)
        notificationStore.error('Failed to cancel reservation')
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= reservationPagination.value.pages) {
        fetchReservations(page)
      }
    }

    // Utility functions
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    const formatDuration = (hours) => {
      if (!hours) return 'N/A'
      const h = Math.floor(hours)
      const m = Math.floor((hours - h) * 60)
      return `${h}h ${m}m`
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'active':
          return 'badge bg-success'
        case 'completed':
          return 'badge bg-primary'
        case 'cancelled':
          return 'badge bg-danger'
        default:
          return 'badge bg-secondary'
      }
    }

    // Analytics functions
    const fetchAnalyticsData = async () => {
      try {
        console.log('🔍 Fetching analytics data...')
        console.log('🔑 Auth store token:', authStore.token ? 'Present' : 'Missing')
        console.log('👤 Current user:', authStore.user?.username)
        
        const response = await api.get('/admin/analytics')
        analyticsData.value = response.data
        
        console.log('✅ Analytics data received:', analyticsData.value)
        
        // Initialize charts after data is loaded
        await nextTick()
        initializeCharts()
      } catch (err) {
        console.error('❌ Error fetching analytics data:', err)
        console.error('❌ Error status:', err.response?.status)
        console.error('❌ Error data:', err.response?.data)
        notificationStore.error('Failed to load analytics data')
      }
    }

    const initializeCharts = () => {
      if (chartsInitialized.value) return
      
      createParkingStatusChart()
      createRevenueChart()
      createUtilizationChart()
      createWeeklyRevenueChart()
      createPeakHoursChart()
      
      chartsInitialized.value = true
    }

    const createParkingStatusChart = () => {
      const ctx = parkingStatusChart.value?.getContext('2d')
      if (!ctx || !analyticsData.value.parking_status) return

      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Available', 'Occupied', 'Reserved'],
          datasets: [{
            data: [
              analyticsData.value.parking_status.available || 0,
              analyticsData.value.parking_status.occupied || 0,
              analyticsData.value.parking_status.reserved || 0
            ],
            backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((context.parsed / total) * 100).toFixed(1)
                  return `${context.label}: ${context.parsed} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }

    const createRevenueChart = () => {
      const ctx = revenueChart.value?.getContext('2d')
      if (!ctx || !analyticsData.value.daily_revenue) return

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: analyticsData.value.daily_revenue.dates || [],
          datasets: [{
            label: 'Daily Revenue ($)',
            data: analyticsData.value.daily_revenue.amounts || [],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value.toFixed(0)
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Revenue: $${context.parsed.y.toFixed(2)}`
                }
              }
            }
          }
        }
      })
    }

    const createUtilizationChart = () => {
      const ctx = utilizationChart.value?.getContext('2d')
      if (!ctx || !analyticsData.value.lot_utilization) return

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: analyticsData.value.lot_utilization.lot_names || [],
          datasets: [{
            label: 'Utilization Rate (%)',
            data: analyticsData.value.lot_utilization.utilization_rates || [],
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%'
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Utilization: ${context.parsed.y.toFixed(1)}%`
                }
              }
            }
          }
        }
      })
    }

    const createWeeklyRevenueChart = () => {
      const ctx = weeklyRevenueChart.value?.getContext('2d')
      if (!ctx || !analyticsData.value.weekly_revenue) return

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: analyticsData.value.weekly_revenue.weeks || [],
          datasets: [{
            label: 'Weekly Revenue ($)',
            data: analyticsData.value.weekly_revenue.amounts || [],
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value.toFixed(0)
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Revenue: $${context.parsed.y.toFixed(2)}`
                }
              }
            }
          }
        }
      })
    }

    const createPeakHoursChart = () => {
      const ctx = peakHoursChart.value?.getContext('2d')
      if (!ctx || !analyticsData.value.peak_hours) return

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: analyticsData.value.peak_hours.hours || [],
          datasets: [{
            label: 'Average Occupancy',
            data: analyticsData.value.peak_hours.occupancy || [],
            borderColor: '#ff6384',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return value.toFixed(0) + ' spots'
                }
              }
            },
            x: {
              title: {
                display: true,
                text: 'Hour of Day'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `Avg Occupancy: ${context.parsed.y.toFixed(1)} spots`
                }
              }
            }
          }
        }
      })
    }

    // Authentication functions
    const handleLogout = async () => {
      try {
        console.log('👋 Logging out...')
        await authStore.logout()
        notificationStore.success('Logged out successfully!')
        router.push('/login')
      } catch (err) {
        console.error('❌ Error during logout:', err)
        notificationStore.error('Error during logout')
        // Force logout even if API call fails
        authStore.logout()
        router.push('/login')
      }
    }

    onMounted(() => {
      console.log('🚀 AdminDashboardView mounted')
      console.log('🔑 Is authenticated:', authStore.isAuthenticated)
      console.log('👤 User role:', authStore.user?.role)
      
      fetchStats()
      fetchParkingLots()
      fetchUsers()
      fetchReservations()
      
      // Only fetch analytics if user is authenticated and is admin
      if (authStore.isAuthenticated && authStore.user?.role === 'admin') {
        fetchAnalyticsData()
      } else {
        console.warn('⚠️ Not fetching analytics - user not authenticated or not admin')
      }
    })

    return {
      // Stores
      authStore,
      // Core state
      loading,
      error,
      stats,
      parkingLots,
      parkingLotsLoading,
      showCreateModal,
      editingLot,
      saving,
      lotForm,
      editLot,
      closeModal,
      saveParkingLot,
      deleteLot,
      // Analytics
      analyticsData,
      parkingStatusChart,
      revenueChart,
      utilizationChart,
      weeklyRevenueChart,
      peakHoursChart,
      fetchAnalyticsData,
      // Users
      users,
      usersLoading,
      viewUserStats,
      // Reservations
      reservations,
      reservationsLoading,
      reservationStatusFilter,
      reservationPagination,
      fetchReservations,
      completeReservation,
      cancelReservation,
      changePage,
      // Utilities
      formatDate,
      formatDuration,
      getStatusBadgeClass,
      // Authentication
      handleLogout
    }
  }
}
</script>