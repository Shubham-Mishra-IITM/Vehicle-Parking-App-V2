<template>
  <div>
    <h1>Admin Dashboard</h1>

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

      <!-- Parking Lots Management -->
      <div class="row">
        <div class="col-12">
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
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api'

export default {
  name: 'AdminDashboardView',
  setup() {
    const notificationStore = useNotificationStore()
    const loading = ref(true)
    const error = ref('')
    const stats = ref({})
    const parkingLots = ref([])
    const parkingLotsLoading = ref(false)
    const showCreateModal = ref(false)
    const editingLot = ref(null)
    const saving = ref(false)
    
    const lotForm = ref({
      prime_location_name: '',
      address: '',
      pin_code: '',
      price: '',
      number_of_spots: '',
      description: ''
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

    onMounted(() => {
      fetchStats()
      fetchParkingLots()
    })

    return {
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
      deleteLot
    }
  }
}
</script>
