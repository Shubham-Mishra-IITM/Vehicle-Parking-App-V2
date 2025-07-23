<template>
  <div>
    <h1>User Profile</h1>
    
    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Profile Information</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Username</label>
                  <input type="text" class="form-control" v-model="profileForm.username" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" v-model="profileForm.email" required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone Number</label>
                  <input type="tel" class="form-control" v-model="profileForm.phone_number" placeholder="Optional">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Role</label>
                  <input type="text" class="form-control" :value="authStore.user?.role" disabled>
                </div>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="updating">
                <span v-if="updating" class="spinner-border spinner-border-sm me-1"></span>
                Update Profile
              </button>
            </form>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Account Statistics</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <small class="text-muted">Member Since</small>
              <div>{{ formatDate(authStore.user?.created_at) }}</div>
            </div>
            <div class="mb-3">
              <small class="text-muted">Total Reservations</small>
              <div class="h4">{{ stats.total_reservations }}</div>
            </div>
            <div class="mb-3">
              <small class="text-muted">Total Spent</small>
              <div class="h4">${{ stats.total_spent }}</div>
            </div>
            <div class="mb-3">
              <small class="text-muted">Account Status</small>
              <div>
                <span :class="authStore.user?.is_active ? 'badge bg-success' : 'badge bg-danger'">
                  {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Section -->
    <div class="row mt-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Change Password</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input type="password" class="form-control" v-model="passwordForm.current_password" required>
              </div>
              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input type="password" class="form-control" v-model="passwordForm.new_password" required minlength="6">
              </div>
              <div class="mb-3">
                <label class="form-label">Confirm New Password</label>
                <input type="password" class="form-control" v-model="passwordForm.confirm_password" required>
              </div>
              <div v-if="passwordError" class="alert alert-danger">{{ passwordError }}</div>
              <button type="submit" class="btn btn-warning" :disabled="changingPassword">
                <span v-if="changingPassword" class="spinner-border spinner-border-sm me-1"></span>
                Change Password
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Vehicle Management -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">My Vehicles</h5>
            <button class="btn btn-primary btn-sm" @click="showAddVehicle = true">
              <i class="bi bi-plus"></i> Add Vehicle
            </button>
          </div>
          <div class="card-body">
            <div v-if="vehicles.length === 0" class="text-center text-muted">
              No vehicles added yet
            </div>
            <div v-else class="row">
              <div v-for="vehicle in vehicles" :key="vehicle.id" class="col-md-4 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h6>{{ vehicle.make }} {{ vehicle.model }}</h6>
                    <p class="mb-1"><strong>{{ vehicle.license_plate }}</strong></p>
                    <p class="mb-1 text-muted">{{ vehicle.color }} - {{ vehicle.year }}</p>
                    <button class="btn btn-sm btn-outline-danger" @click="removeVehicle(vehicle.id)">
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Vehicle Modal -->
    <div class="modal fade" :class="{ show: showAddVehicle }" style="display: block;" v-if="showAddVehicle" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Vehicle</h5>
            <button type="button" class="btn-close" @click="closeVehicleModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addVehicle">
              <div class="mb-3">
                <label class="form-label">License Plate</label>
                <input type="text" class="form-control" v-model="vehicleForm.license_plate" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Make</label>
                <input type="text" class="form-control" v-model="vehicleForm.make" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Model</label>
                <input type="text" class="form-control" v-model="vehicleForm.model" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Year</label>
                <input type="number" class="form-control" v-model="vehicleForm.year" min="1900" max="2030" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Color</label>
                <input type="text" class="form-control" v-model="vehicleForm.color" required>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeVehicleModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="addVehicle" :disabled="addingVehicle">
              <span v-if="addingVehicle" class="spinner-border spinner-border-sm me-1"></span>
              Add Vehicle
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showAddVehicle"></div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

export default {
  name: 'UserProfileView',
  setup() {
    const authStore = useAuthStore()
    const updating = ref(false)
    const changingPassword = ref(false)
    const passwordError = ref('')
    const stats = ref({})
    const vehicles = ref([])
    const showAddVehicle = ref(false)
    const addingVehicle = ref(false)
    
    const profileForm = ref({
      username: '',
      email: '',
      phone_number: ''
    })
    
    const passwordForm = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    const vehicleForm = ref({
      license_plate: '',
      make: '',
      model: '',
      year: '',
      color: ''
    })

    const loadProfile = () => {
      if (authStore.user) {
        profileForm.value = {
          username: authStore.user.username || '',
          email: authStore.user.email || '',
          phone_number: authStore.user.phone_number || ''
        }
      }
    }

    const fetchStats = async () => {
      try {
        const response = await api.get('/user/stats')
        stats.value = response.data
      } catch (err) {
        console.error('Error fetching stats:', err)
      }
    }

    const fetchVehicles = async () => {
      try {
        const response = await api.get('/user/vehicles')
        vehicles.value = response.data
      } catch (err) {
        console.error('Error fetching vehicles:', err)
      }
    }

    const updateProfile = async () => {
      updating.value = true
      try {
        const response = await api.put('/user/profile', profileForm.value)
        authStore.user = { ...authStore.user, ...response.data }
        alert('Profile updated successfully!')
      } catch (err) {
        console.error('Error updating profile:', err)
        alert('Failed to update profile')
      } finally {
        updating.value = false
      }
    }

    const changePassword = async () => {
      passwordError.value = ''
      
      if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
        passwordError.value = 'New passwords do not match'
        return
      }

      changingPassword.value = true
      try {
        await api.put('/user/change-password', {
          current_password: passwordForm.value.current_password,
          new_password: passwordForm.value.new_password
        })
        
        passwordForm.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
        
        alert('Password changed successfully!')
      } catch (err) {
        passwordError.value = err.response?.data?.message || 'Failed to change password'
      } finally {
        changingPassword.value = false
      }
    }

    const addVehicle = async () => {
      addingVehicle.value = true
      try {
        await api.post('/user/vehicles', vehicleForm.value)
        closeVehicleModal()
        await fetchVehicles()
        alert('Vehicle added successfully!')
      } catch (err) {
        console.error('Error adding vehicle:', err)
        alert('Failed to add vehicle')
      } finally {
        addingVehicle.value = false
      }
    }

    const removeVehicle = async (vehicleId) => {
      if (!confirm('Are you sure you want to remove this vehicle?')) return
      
      try {
        await api.delete(`/user/vehicles/${vehicleId}`)
        await fetchVehicles()
        alert('Vehicle removed successfully!')
      } catch (err) {
        console.error('Error removing vehicle:', err)
        alert('Failed to remove vehicle')
      }
    }

    const closeVehicleModal = () => {
      showAddVehicle.value = false
      vehicleForm.value = {
        license_plate: '',
        make: '',
        model: '',
        year: '',
        color: ''
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadProfile()
      fetchStats()
      fetchVehicles()
    })

    return {
      authStore,
      updating,
      changingPassword,
      passwordError,
      stats,
      vehicles,
      showAddVehicle,
      addingVehicle,
      profileForm,
      passwordForm,
      vehicleForm,
      updateProfile,
      changePassword,
      addVehicle,
      removeVehicle,
      closeVehicleModal,
      formatDate
    }
  }
}
</script>
