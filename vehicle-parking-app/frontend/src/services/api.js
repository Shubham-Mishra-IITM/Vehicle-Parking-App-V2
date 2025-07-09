import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Adjust the URL as needed

const api = axios.create({
  baseURL: API_URL,
  timeout: 1000,
});

// Auth API calls
export const login = (credentials) => {
  return api.post('/auth/login', credentials);
};

export const register = (userData) => {
  return api.post('/auth/register', userData);
};

// Admin API calls
export const createParkingLot = (lotData) => {
  return api.post('/admin/parking-lots', lotData);
};

export const editParkingLot = (lotId, updatedData) => {
  return api.put(`/admin/parking-lots/${lotId}`, updatedData);
};

export const deleteParkingLot = (lotId) => {
  return api.delete(`/admin/parking-lots/${lotId}`);
};

export const getParkingLots = () => {
  return api.get('/parking-lots');
};

// User API calls
export const reserveParkingSpot = (reservationData) => {
  return api.post('/user/reserve', reservationData);
};

export const releaseParkingSpot = (spotId) => {
  return api.post(`/user/release/${spotId}`);
};

export const getUserReservations = (userId) => {
  return api.get(`/user/reservations/${userId}`);
};