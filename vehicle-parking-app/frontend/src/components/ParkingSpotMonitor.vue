<template>
  <div class="parking-spot-monitor">
    <!-- Header with controls -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>🚗 Parking Spot Monitor</h3>
      <div class="d-flex gap-2">
        <button @click="refreshData" class="btn btn-outline-primary btn-sm" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i> Refresh
        </button>
        <button @click="showOccupiedOnly = !showOccupiedOnly" 
                class="btn btn-outline-warning btn-sm"
                :class="{ active: showOccupiedOnly }">
          <i class="fas fa-car"></i> Occupied Only ({{ occupiedCount }})
        </button>
      </div>
    </div>

    <!-- Filter Controls -->
    <div class="row mb-3">
      <div class="col-md-4">
        <select v-model="selectedLot" @change="filterSpots" class="form-select">
          <option value="">All Parking Lots</option>
          <option v-for="lot in parkingLots" :key="lot.id" :value="lot.id">
            {{ lot.name }} - {{ lot.location }}
          </option>
        </select>
      </div>
      <div class="col-md-4">
        <select v-model="statusFilter" @change="filterSpots" class="form-select">
          <option value="">All Statuses</option>
          <option value="A">Available</option>
          <option value="O">Occupied</option>
          <option value="R">Reserved</option>
        </select>
      </div>
      <div class="col-md-4">
        <input v-model="searchTerm" @input="filterSpots" 
               placeholder="Search by spot number or vehicle..." 
               class="form-control">
      </div>
    </div>

    <!-- Summary Statistics -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card border-success">
          <div class="card-body text-center">
            <h5 class="text-success">Available</h5>
            <h3 class="text-success">{{ summary.available || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-danger">
          <div class="card-body text-center">
            <h5 class="text-danger">Occupied</h5>
            <h3 class="text-danger">{{ summary.occupied || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-warning">
          <div class="card-body text-center">
            <h5 class="text-warning">Reserved</h5>
            <h3 class="text-warning">{{ summary.reserved || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-info">
          <div class="card-body text-center">
            <h5 class="text-info">Occupancy</h5>
            <h3 class="text-info">{{ summary.occupancy_rate || 0 }}%</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading parking spots...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-triangle"></i> {{ error }}
    </div>

    <!-- Parking Spots Grid -->
    <div v-else class="parking-spots-grid">
      <div class="row">
        <div v-for="spot in filteredSpots" :key="spot.id" class="col-lg-4 col-md-6 mb-3">
          <div class="card parking-spot-card" 
               :class="getSpotCardClass(spot.status)"
               @click="showSpotDetails(spot)">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i :class="getSpotIcon(spot.status)"></i>
                Spot {{ spot.spot_number }}
              </h6>
              <span class="badge" :class="getStatusBadgeClass(spot.status)">
                {{ getStatusText(spot.status) }}
              </span>
            </div>
            <div class="card-body">
              <p class="text-muted mb-2">
                <i class="fas fa-map-marker-alt"></i> {{ spot.lot_name }}
              </p>
              
              <!-- Occupied Spot Details -->
              <div v-if="spot.status === 'O' && spot.vehicle_details">
                <div class="vehicle-info">
                  <strong>🚗 {{ spot.vehicle_details.vehicle_number }}</strong>
                  <p class="mb-1">👤 {{ spot.vehicle_details.owner_name }}</p>
                  <p class="mb-1">📞 {{ spot.vehicle_details.owner_phone }}</p>
                  <div class="d-flex justify-content-between">
                    <small class="text-muted">
                      ⏰ {{ formatDuration(spot.vehicle_details.parking_duration) }}
                    </small>
                    <small class="text-success">
                      💰 ${{ spot.vehicle_details.estimated_cost.toFixed(2) }}
                    </small>
                  </div>
                  
                  <!-- Overstay Alert -->
                  <div v-if="spot.vehicle_details.parking_duration > 24" class="alert alert-warning alert-sm mt-2">
                    <i class="fas fa-exclamation-triangle"></i> Long-term parking ({{ Math.floor(spot.vehicle_details.parking_duration / 24) }} days)
                  </div>
                </div>
              </div>

              <!-- Reserved Spot Details -->
              <div v-else-if="spot.status === 'R' && spot.current_reservation">
                <p class="mb-1">
                  🚗 {{ spot.current_reservation.vehicle_number }}
                </p>
                <small class="text-muted">
                  Reserved since {{ formatTime(spot.current_reservation.parking_timestamp) }}
                </small>
              </div>

              <!-- Available Spot -->
              <div v-else-if="spot.status === 'A'">
                <p class="text-success mb-0">
                  <i class="fas fa-check-circle"></i> Ready for parking
                </p>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div v-if="spot.status === 'O'" class="card-footer">
              <button @click.stop="forceReleaseSpot(spot)" 
                      class="btn btn-danger btn-sm"
                      title="Force release this spot">
                <i class="fas fa-eject"></i> Force Release
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav v-if="pagination.pages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
            <button class="page-link" @click="changePage(pagination.page - 1)" :disabled="pagination.page <= 1">
              Previous
            </button>
          </li>
          <li v-for="page in getPageNumbers()" :key="page" 
              class="page-item" :class="{ active: page === pagination.page }">
            <button class="page-link" @click="changePage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: pagination.page >= pagination.pages }">
            <button class="page-link" @click="changePage(pagination.page + 1)" 
                    :disabled="pagination.page >= pagination.pages">
              Next
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Spot Details Modal -->
    <div class="modal fade" id="spotDetailsModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Spot {{ selectedSpot?.spot_number }} Details
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedSpot">
              <!-- Current Status -->
              <div class="mb-4">
                <h6>Current Status</h6>
                <span class="badge fs-6" :class="getStatusBadgeClass(selectedSpot.status)">
                  {{ getStatusText(selectedSpot.status) }}
                </span>
              </div>

              <!-- Vehicle Details (if occupied) -->
              <div v-if="selectedSpot.current_occupancy" class="mb-4">
                <h6>Current Vehicle</h6>
                <div class="card">
                  <div class="card-body">
                    <h5>🚗 {{ selectedSpot.current_occupancy.vehicle_number }}</h5>
                    <p><strong>Owner:</strong> {{ selectedSpot.current_occupancy.user_details?.full_name }}</p>
                    <p><strong>Phone:</strong> {{ selectedSpot.current_occupancy.user_details?.phone_number }}</p>
                    <p><strong>Email:</strong> {{ selectedSpot.current_occupancy.user_details?.email }}</p>
                    <p><strong>Parked Since:</strong> {{ formatDateTime(selectedSpot.current_occupancy.parking_since) }}</p>
                    <p><strong>Duration:</strong> {{ formatDuration(selectedSpot.current_occupancy.duration_hours) }}</p>
                    <p><strong>Estimated Cost:</strong> ${{ selectedSpot.current_occupancy.estimated_cost.toFixed(2) }}</p>
                  </div>
                </div>
              </div>

              <!-- Recent History -->
              <div v-if="selectedSpot.recent_history?.length">
                <h6>Recent History</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Vehicle</th>
                        <th>User</th>
                        <th>Duration</th>
                        <th>Cost</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="history in selectedSpot.recent_history.slice(0, 5)" :key="history.reservation_id">
                        <td>{{ history.vehicle_number }}</td>
                        <td>{{ history.user_name }}</td>
                        <td>{{ history.duration_hours ? formatDuration(history.duration_hours) : 'In progress' }}</td>
                        <td>${{ history.cost ? history.cost.toFixed(2) : 'TBD' }}</td>
                        <td>
                          <span class="badge" :class="history.status === 'completed' ? 'bg-success' : 'bg-warning'">
                            {{ history.status }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button v-if="selectedSpot?.status === 'O'" 
                    type="button" class="btn btn-danger"
                    @click="forceReleaseSpot(selectedSpot)">
              Force Release
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Force Release Modal -->
    <div class="modal fade" id="forceReleaseModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Force Release Parking Spot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to force release spot <strong>{{ spotToRelease?.spot_number }}</strong>?</p>
            <p>This will complete the current reservation and charge the user.</p>
            <div class="mb-3">
              <label class="form-label">Reason for force release:</label>
              <textarea v-model="releaseReason" class="form-control" rows="3" 
                        placeholder="Enter reason for force release..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmForceRelease" :disabled="!releaseReason.trim()">
              Confirm Release
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Modal } from 'bootstrap'

export default {
  name: 'ParkingSpotMonitor',
  setup() {
    const authStore = useAuthStore()
    
    const loading = ref(false)
    const error = ref(null)
    const spots = ref([])
    const parkingLots = ref([])
    const summary = ref({})
    const pagination = ref({})
    
    const selectedLot = ref('')
    const statusFilter = ref('')
    const searchTerm = ref('')
    const showOccupiedOnly = ref(false)
    const selectedSpot = ref(null)
    const spotToRelease = ref(null)
    const releaseReason = ref('')
    
    const filteredSpots = computed(() => {
      let filtered = spots.value
      
      if (showOccupiedOnly.value) {
        filtered = filtered.filter(spot => spot.status === 'O')
      }
      
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        filtered = filtered.filter(spot => 
          spot.spot_number.toLowerCase().includes(term) ||
          (spot.vehicle_details?.vehicle_number?.toLowerCase().includes(term)) ||
          (spot.vehicle_details?.owner_name?.toLowerCase().includes(term))
        )
      }
      
      return filtered
    })
    
    const occupiedCount = computed(() => 
      spots.value.filter(spot => spot.status === 'O').length
    )
    
    const loadParkingSpots = async (page = 1) => {
      try {
        loading.value = true
        error.value = null
        
        const params = new URLSearchParams()
        if (selectedLot.value) params.append('lot_id', selectedLot.value)
        if (statusFilter.value) params.append('status', statusFilter.value)
        params.append('page', page.toString())
        params.append('per_page', '50')
        
        const response = await fetch(`/api/admin/parking-spots/status?${params}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error('Failed to load parking spots')
        }
        
        const data = await response.json()
        spots.value = data.spots
        summary.value = data.summary
        pagination.value = data.pagination
        
      } catch (err) {
        error.value = err.message
        console.error('Error loading parking spots:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadParkingLots = async () => {
      try {
        const response = await fetch('/api/admin/parking-lots', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          parkingLots.value = data.parking_lots || []
        }
      } catch (err) {
        console.error('Error loading parking lots:', err)
      }
    }
    
    const refreshData = () => {
      loadParkingSpots(1)
    }
    
    const filterSpots = () => {
      loadParkingSpots(1)
    }
    
    const changePage = (page) => {
      if (page >= 1 && page <= pagination.value.pages) {
        loadParkingSpots(page)
      }
    }
    
    const showSpotDetails = async (spot) => {
      try {
        const response = await fetch(`/api/admin/parking-spots/${spot.id}/details`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          selectedSpot.value = await response.json()
          const modal = new Modal(document.getElementById('spotDetailsModal'))
          modal.show()
        }
      } catch (err) {
        console.error('Error loading spot details:', err)
      }
    }
    
    const forceReleaseSpot = (spot) => {
      spotToRelease.value = spot
      releaseReason.value = ''
      const modal = new Modal(document.getElementById('forceReleaseModal'))
      modal.show()
    }
    
    const confirmForceRelease = async () => {
      try {
        const response = await fetch(`/api/admin/parking-spots/${spotToRelease.value.id}/force-release`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            reason: releaseReason.value.trim()
          })
        })
        
        if (response.ok) {
          const result = await response.json()
          alert(`Successfully released spot ${spotToRelease.value.spot_number}. Final cost: $${result.final_cost}`)
          
          // Close modal and refresh data
          const modal = Modal.getInstance(document.getElementById('forceReleaseModal'))
          modal.hide()
          loadParkingSpots(pagination.value.page || 1)
        } else {
          throw new Error('Failed to force release spot')
        }
      } catch (err) {
        alert('Error: ' + err.message)
        console.error('Error force releasing spot:', err)
      }
    }
    
    const getSpotCardClass = (status) => {
      switch (status) {
        case 'A': return 'border-success'
        case 'O': return 'border-danger'
        case 'R': return 'border-warning'
        default: return 'border-secondary'
      }
    }
    
    const getSpotIcon = (status) => {
      switch (status) {
        case 'A': return 'fas fa-check-circle text-success'
        case 'O': return 'fas fa-car text-danger'
        case 'R': return 'fas fa-clock text-warning'
        default: return 'fas fa-question-circle text-secondary'
      }
    }
    
    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'A': return 'bg-success'
        case 'O': return 'bg-danger'
        case 'R': return 'bg-warning'
        default: return 'bg-secondary'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'A': return 'Available'
        case 'O': return 'Occupied'
        case 'R': return 'Reserved'
        default: return 'Unknown'
      }
    }
    
    const formatDuration = (hours) => {
      if (hours < 1) {
        return `${Math.round(hours * 60)} min`
      } else if (hours < 24) {
        return `${hours.toFixed(1)} hrs`
      } else {
        const days = Math.floor(hours / 24)
        const remainingHours = Math.round(hours % 24)
        return `${days}d ${remainingHours}h`
      }
    }
    
    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString()
    }
    
    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString()
    }
    
    const getPageNumbers = () => {
      const pages = []
      const total = pagination.value.pages
      const current = pagination.value.page
      
      for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
        pages.push(i)
      }
      
      return pages
    }
    
    onMounted(() => {
      loadParkingSpots()
      loadParkingLots()
      
      // Auto-refresh every 30 seconds
      setInterval(() => {
        if (!loading.value) {
          loadParkingSpots(pagination.value.page || 1)
        }
      }, 30000)
    })
    
    return {
      loading,
      error,
      spots,
      parkingLots,
      summary,
      pagination,
      selectedLot,
      statusFilter,
      searchTerm,
      showOccupiedOnly,
      selectedSpot,
      spotToRelease,
      releaseReason,
      filteredSpots,
      occupiedCount,
      refreshData,
      filterSpots,
      changePage,
      showSpotDetails,
      forceReleaseSpot,
      confirmForceRelease,
      getSpotCardClass,
      getSpotIcon,
      getStatusBadgeClass,
      getStatusText,
      formatDuration,
      formatTime,
      formatDateTime,
      getPageNumbers
    }
  }
}
</script>

<style scoped>
.parking-spot-monitor {
  padding: 20px;
}

.parking-spot-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.parking-spot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.vehicle-info {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
}

.alert-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.parking-spots-grid {
  min-height: 400px;
}

.badge.fs-6 {
  font-size: 1rem !important;
}

@media (max-width: 768px) {
  .parking-spot-monitor {
    padding: 10px;
  }
  
  .card-body {
    padding: 0.75rem;
  }
}
</style>
