<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Users Management</h1>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search users..." 
          v-model="searchQuery"
          style="width: 300px;">
        <select class="form-select" v-model="roleFilter" style="width: 150px;">
          <option value="">All Users</option>
          <option value="user">Active Users</option>
        </select>
        <button class="btn btn-outline-secondary" @click="fetchUsers()">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
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
              <h2 class="card-text">{{ regularUsers }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-success mb-3">
            <div class="card-body">
              <h5 class="card-title">Active Users</h5>
              <h2 class="card-text">{{ regularUsers }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-info mb-3">
            <div class="card-body">
              <h5 class="card-title">Registered Users</h5>
              <h2 class="card-text">{{ regularUsers }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-white bg-warning mb-3">
            <div class="card-body">
              <h5 class="card-title">Total Reservations</h5>
              <h2 class="card-text">{{ totalReservations }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Registered Users</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th class="text-center">ID</th>
                  <th class="text-center">Username</th>
                  <th class="text-center">Email</th>
                  <th class="text-center">Full Name</th>
                  <th class="text-center">Phone</th>
                  <th class="text-center">Address</th>
                  <th class="text-center">PIN Code</th>
                  <th class="text-center">Registered</th>
                  <th class="text-center">Details</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td class="text-center">#{{ user.id }}</td>
                  <td class="text-center">{{ user.username }}</td>
                  <td class="text-center">{{ user.email }}</td>
                  <td class="text-center">{{ user.full_name || '-' }}</td>
                  <td class="text-center">{{ user.phone_number || '-' }}</td>
                  <td class="text-center">{{ user.address || '-' }}</td>
                  <td class="text-center">{{ user.pin_code || '-' }}</td>
                  <td class="text-center">{{ formatDate(user.created_at) }}</td>
                  <td class="text-center">
                    <button 
                      class="btn btn-sm btn-outline-info" 
                      @click="viewUserDetails(user)"
                      title="View details">
                      <i class="bi bi-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="d-flex justify-content-between align-items-center mt-3">
            <div>
              Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredUsers.length) }} of {{ filteredUsers.length }} users
            </div>
            <nav>
              <ul class="pagination pagination-sm mb-0">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <button class="page-link" @click="currentPage--" :disabled="currentPage === 1">
                    Previous
                  </button>
                </li>
                <li v-for="page in totalPages" :key="page" 
                    class="page-item" :class="{ active: page === currentPage }">
                  <button class="page-link" @click="currentPage = page">{{ page }}</button>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <button class="page-link" @click="currentPage++" :disabled="currentPage === totalPages">
                    Next
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <div class="modal fade" :class="{ show: showUserDetails }" style="display: block;" v-if="showUserDetails" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button type="button" class="btn-close" @click="closeUserDetails"></button>
          </div>
          <div class="modal-body" v-if="selectedUser">
            <div class="row">
              <div class="col-md-6">
                <h6 class="text-primary">Personal Information</h6>
                <p><strong>ID:</strong> #{{ selectedUser.id }}</p>
                <p><strong>Username:</strong> {{ selectedUser.username }}</p>
                <p><strong>Email:</strong> {{ selectedUser.email }}</p>
                <p><strong>Full Name:</strong> {{ selectedUser.full_name || 'Not provided' }}</p>
                <p><strong>Phone Number:</strong> {{ selectedUser.phone_number || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="text-primary">Account Information</h6>
                <p><strong>Address:</strong> {{ selectedUser.address || 'Not provided' }}</p>
                <p><strong>PIN Code:</strong> {{ selectedUser.pin_code || 'Not provided' }}</p>
                <p><strong>Registered:</strong> {{ formatDate(selectedUser.created_at) }}</p>
                <p v-if="selectedUser.updated_at"><strong>Last Updated:</strong> {{ formatDate(selectedUser.updated_at) }}</p>
              </div>
            </div>
            
            <!-- User Statistics -->
            <div class="row mt-3" v-if="selectedUser.statistics">
              <div class="col-12">
                <h6 class="text-primary">User Statistics</h6>
                <div class="row">
                  <div class="col-md-4">
                    <div class="card text-center">
                      <div class="card-body">
                        <h5 class="card-title">{{ selectedUser.statistics.total_reservations || 0 }}</h5>
                        <p class="card-text">Total Reservations</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="card text-center">
                      <div class="card-body">
                        <h5 class="card-title">{{ selectedUser.statistics.active_reservations || 0 }}</h5>
                        <p class="card-text">Active Reservations</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="card text-center">
                      <div class="card-body">
                        <h5 class="card-title">{{ formatINR(selectedUser.statistics.total_spent || 0) }}</h5>
                        <p class="card-text">Total Spent</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeUserDetails">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showUserDetails"></div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { formatINR } from '@/utils/currency'
import api from '@/services/api'

export default {
  name: 'AdminUsersView',
  setup() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const loading = ref(true)
    const error = ref('')
    const users = ref([])
    const searchQuery = ref('')
    const roleFilter = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const showUserDetails = ref(false)
    const selectedUser = ref(null)

    const currentAdminId = computed(() => authStore.user?.id)

    const filteredUsers = computed(() => {
      // First filter out admin users
      let filtered = users.value.filter(user => user.role !== 'admin')

      // Filter by search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          (user.full_name && user.full_name.toLowerCase().includes(query)) ||
          (user.phone_number && user.phone_number.includes(query))
        )
      }

      // Filter by role (though now it will only be 'user' since we filtered out admins)
      if (roleFilter.value) {
        filtered = filtered.filter(user => user.role === roleFilter.value)
      }

      return filtered
    })

    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredUsers.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredUsers.value.length / itemsPerPage.value)
    })

    const activeUsers = computed(() => {
      return users.value.filter(user => user.role !== 'admin').length // Only count non-admin users
    })

    const regularUsers = computed(() => {
      return users.value.filter(user => user.role === 'user').length
    })

    const adminUsers = computed(() => {
      return users.value.filter(user => user.role === 'admin').length
    })

    const totalReservations = computed(() => {
      // This could be enhanced to show actual reservation count if available
      return 0 // Placeholder for now
    })

    const fetchUsers = async () => {
      loading.value = true
      try {
        console.log('Fetching users...')
        const response = await api.get('/admin/users')
        console.log('Users response:', response.data)
        users.value = response.data
      } catch (err) {
        console.error('Error fetching users:', err)
        if (err.response?.status === 401) {
          error.value = 'Authentication failed. Please login as admin.'
        } else if (err.response?.status === 403) {
          error.value = 'Access denied. Admin privileges required.'
        } else {
          error.value = `Failed to load users: ${err.response?.data?.error || err.message}`
        }
      } finally {
        loading.value = false
      }
    }

    const viewUserDetails = async (user) => {
      selectedUser.value = user
      
      // Try to fetch additional user statistics
      try {
        const response = await api.get(`/admin/users/${user.id}/statistics`)
        selectedUser.value.statistics = response.data
      } catch (err) {
        console.log('Could not fetch user statistics:', err)
        selectedUser.value.statistics = null
      }
      
      showUserDetails.value = true
    }

    const closeUserDetails = () => {
      showUserDetails.value = false
      selectedUser.value = null
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) return '-'
        return date.toLocaleString()
      } catch (error) {
        return '-'
      }
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      loading,
      error,
      users,
      searchQuery,
      roleFilter,
      currentPage,
      itemsPerPage,
      showUserDetails,
      selectedUser,
      currentAdminId,
      filteredUsers,
      paginatedUsers,
      totalPages,
      activeUsers,
      regularUsers,
      adminUsers,
      totalReservations,
      fetchUsers,
      viewUserDetails,
      closeUserDetails,
      formatDate,
      formatINR
    }
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.75em;
}

.btn-group .btn {
  margin-right: 2px;
}

.card-title {
  font-size: 0.9rem;
}

.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
