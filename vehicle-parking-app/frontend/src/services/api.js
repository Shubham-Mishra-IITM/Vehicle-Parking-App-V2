import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default {
    // Generic HTTP methods
    get(url) {
        return apiClient.get(url);
    },
    post(url, data) {
        return apiClient.post(url, data);
    },
    put(url, data) {
        return apiClient.put(url, data);
    },
    delete(url) {
        return apiClient.delete(url);
    },

    // Auth
    login(credentials) {
        return apiClient.post('/auth/login', credentials);
    },
    adminLogin(credentials) {
        return apiClient.post('/auth/admin-login', credentials);
    },
    register(data) {
        return apiClient.post('/auth/register', data);
    },

    // User
    getProfile() {
        return apiClient.get('/user/profile');
    },
    getUserReservations() {
        return apiClient.get('/user/reservations');
    },
    createReservation(data) {
        return apiClient.post('/user/reservations', data);
    },

    // Admin
    getAdminDashboard() {
        return apiClient.get('/admin/dashboard');
    },
    getParkingLots() {
        return apiClient.get('/admin/parking-lots');
    },
    createParkingLot(data) {
        return apiClient.post('/admin/parking-lots', data);
    },

    // Public
    getPublicParkingLots() {
        return apiClient.get('/parking/lots');
    }
};
