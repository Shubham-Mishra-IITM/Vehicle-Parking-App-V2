import Vue from 'vue';
import Vuex from 'vuex';
import api from '../services/api';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    parkingLots: [],
    reservations: [],
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user;
    },
    SET_PARKING_LOTS(state, parkingLots) {
      state.parkingLots = parkingLots;
    },
    ADD_RESERVATION(state, reservation) {
      state.reservations.push(reservation);
    },
    REMOVE_RESERVATION(state, reservationId) {
      state.reservations = state.reservations.filter(res => res.id !== reservationId);
    },
  },
  actions: {
    async fetchParkingLots({ commit }) {
      const response = await api.getParkingLots();
      commit('SET_PARKING_LOTS', response.data);
    },
    async reserveParkingSpot({ commit }, spotId) {
      const response = await api.reserveSpot(spotId);
      commit('ADD_RESERVATION', response.data);
    },
    async releaseParkingSpot({ commit }, reservationId) {
      await api.releaseSpot(reservationId);
      commit('REMOVE_RESERVATION', reservationId);
    },
    setUser({ commit }, user) {
      commit('SET_USER', user);
    },
  },
  getters: {
    isAuthenticated(state) {
      return !!state.user;
    },
    availableParkingLots(state) {
      return state.parkingLots.filter(lot => lot.spots.some(spot => spot.status === 'A'));
    },
  },
});