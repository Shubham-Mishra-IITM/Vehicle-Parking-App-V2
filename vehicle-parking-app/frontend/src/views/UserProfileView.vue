<template>
  <div>
    <h1>User Profile</h1>
    
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Profile Information</h5>
          </div>
          <div class="card-body">
            <div v-if="profileError" class="alert alert-danger mb-3">{{ profileError }}</div>
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Username <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="profileForm.username" 
                    required
                    minlength="3"
                    maxlength="80">
                  <div class="form-text">Username must be 3-80 characters long</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="profileForm.full_name" 
                    placeholder="Enter your full name"
                    maxlength="200">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email Address <span class="text-danger">*</span></label>
                  <input 
                    type="email" 
                    class="form-control" 
                    v-model="profileForm.email" 
                    required
                    maxlength="120">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone Number</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    v-model="profileForm.phone_number" 
                    placeholder="Enter your phone number"
                    maxlength="15">
                </div>
              </div>
              <div class="row">
                <div class="col-md-8 mb-3">
                  <label class="form-label">Address</label>
                  <textarea 
                    class="form-control" 
                    v-model="profileForm.address" 
                    rows="3" 
                    placeholder="Enter your complete address"></textarea>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">PIN Code</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="profileForm.pin_code" 
                    placeholder="Enter PIN code"
                    maxlength="10">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Role</label>
                <input type="text" class="form-control" :value="authStore.user?.role" disabled>
                <div class="form-text">Your account role cannot be changed</div>
              </div>
              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary" :disabled="updating">
                  <span v-if="updating" class="spinner-border spinner-border-sm me-1"></span>
                  <i class="bi bi-check-circle me-1"></i>
                  Update Profile
                </button>
                <button type="button" class="btn btn-outline-secondary" @click="loadProfile" :disabled="updating">
                  <i class="bi bi-arrow-clockwise me-1"></i>
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Section -->
    <div class="row mt-4">
      <div class="col-md-12">
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
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api'

export default {
  name: 'UserProfileView',
  setup() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const updating = ref(false)
    const changingPassword = ref(false)
    const passwordError = ref('')
    const profileError = ref('')
    const vehicles = ref([])
    const showAddVehicle = ref(false)
    const addingVehicle = ref(false)
    
    const profileForm = ref({
      username: '',
      full_name: '',
      email: '',
      phone_number: '',
      address: '',
      pin_code: ''
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
          full_name: authStore.user.full_name || '',
          email: authStore.user.email || '',
          phone_number: authStore.user.phone_number || '',
          address: authStore.user.address || '',
          pin_code: authStore.user.pin_code || ''
        }
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
      profileError.value = ''
      updating.value = true
      
      try {
        // Basic validation
        if (!profileForm.value.username || profileForm.value.username.length < 3) {
          profileError.value = 'Username must be at least 3 characters long'
          return
        }
        
        if (!profileForm.value.email) {
          profileError.value = 'Email is required'
          return
        }
        
        const response = await api.put('/user/profile', profileForm.value)
        
        // Update the user data in the auth store
        authStore.user = { ...authStore.user, ...response.data.user }
        
        // Show success notification
        notificationStore.success('Profile updated successfully!')
        
        // Reload profile to ensure frontend is in sync
        loadProfile()
      } catch (err) {
        console.error('Error updating profile:', err)
        const errorMessage = err.response?.data?.error || 'Failed to update profile'
        profileError.value = errorMessage
        notificationStore.error(errorMessage)
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

      if (passwordForm.value.new_password.length < 6) {
        passwordError.value = 'Password must be at least 6 characters long'
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
        
        notificationStore.success('Password changed successfully!')
      } catch (err) {
        passwordError.value = err.response?.data?.error || err.response?.data?.message || 'Failed to change password'
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
        notificationStore.success('Vehicle added successfully!')
      } catch (err) {
        console.error('Error adding vehicle:', err)
        const errorMessage = err.response?.data?.error || 'Failed to add vehicle'
        notificationStore.error(errorMessage)
      } finally {
        addingVehicle.value = false
      }
    }

    const removeVehicle = async (vehicleId) => {
      if (!confirm('Are you sure you want to remove this vehicle?')) return
      
      try {
        await api.delete(`/user/vehicles/${vehicleId}`)
        await fetchVehicles()
        notificationStore.success('Vehicle removed successfully!')
      } catch (err) {
        console.error('Error removing vehicle:', err)
        const errorMessage = err.response?.data?.error || 'Failed to remove vehicle'
        notificationStore.error(errorMessage)
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
      fetchVehicles()
    })

    return {
      authStore,
      updating,
      changingPassword,
      passwordError,
      profileError,
      vehicles,
      showAddVehicle,
      addingVehicle,
      profileForm,
      passwordForm,
      vehicleForm,
      updateProfile,
      loadProfile,
      changePassword,
      addVehicle,
      removeVehicle,
      closeVehicleModal,
      formatDate
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.form-label {
  font-weight: 500;
  color: #495057;
}

.form-control:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.text-danger {
  color: #dc3545 !important;
}

.form-text {
  font-size: 0.875em;
  color: #6c757d;
}

.badge {
  font-size: 0.875em;
}

.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}

.btn-group .btn {
  margin-right: 0.25rem;
}
</style>