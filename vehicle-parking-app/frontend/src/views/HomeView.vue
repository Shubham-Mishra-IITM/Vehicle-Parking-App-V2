<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section bg-primary text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">Smart Parking Made Simple</h1>
            <p class="lead mb-4">
              Find, reserve, and pay for parking spots instantly. Never circle around looking for parking again.
            </p>
            <div class="d-flex gap-3">
              <router-link to="/parking-lots" class="btn btn-light btn-lg">
                <i class="bi bi-search"></i> Find Parking
              </router-link>
              <router-link to="/register" class="btn btn-outline-light btn-lg">
                Get Started
              </router-link>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="hero-image text-center">
              <i class="bi bi-car-front display-1"></i>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section py-5">
      <div class="container">
        <div class="row text-center mb-5">
          <div class="col-12">
            <h2 class="display-5 fw-bold mb-3">Why Choose Our Service?</h2>
            <p class="lead text-muted">Experience the future of parking with our innovative platform</p>
          </div>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card text-center p-4">
              <div class="feature-icon mb-3">
                <i class="bi bi-clock display-4 text-primary"></i>
              </div>
              <h4>Real-time Availability</h4>
              <p class="text-muted">See available parking spots in real-time and reserve instantly</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card text-center p-4">
              <div class="feature-icon mb-3">
                <i class="bi bi-credit-card display-4 text-success"></i>
              </div>
              <h4>Secure Payments</h4>
              <p class="text-muted">Pay securely online with multiple payment options</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card text-center p-4">
              <div class="feature-icon mb-3">
                <i class="bi bi-phone display-4 text-info"></i>
              </div>
              <h4>Mobile Friendly</h4>
              <p class="text-muted">Access from anywhere with our responsive web application</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Statistics Section -->
    <section class="stats-section bg-light py-5" v-if="stats">
      <div class="container">
        <div class="row text-center">
          <div class="col-md-3">
            <div class="stat-item">
              <h3 class="display-4 fw-bold text-primary">{{ stats.parking_lots_count || 0 }}</h3>
              <p class="text-muted">Parking Locations</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-item">
              <h3 class="display-4 fw-bold text-success">{{ stats.total_spots || 0 }}</h3>
              <p class="text-muted">Available Spots</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-item">
              <h3 class="display-4 fw-bold text-info">{{ stats.users_count || 0 }}</h3>
              <p class="text-muted">Happy Users</p>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-item">
              <h3 class="display-4 fw-bold text-warning">{{ stats.reservations_count || 0 }}</h3>
              <p class="text-muted">Bookings Made</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it Works Section -->
    <section class="how-it-works py-5">
      <div class="container">
        <div class="row text-center mb-5">
          <div class="col-12">
            <h2 class="display-5 fw-bold mb-3">How It Works</h2>
            <p class="lead text-muted">Simple steps to secure your parking spot</p>
          </div>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="step-card text-center">
              <div class="step-number bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                   style="width: 60px; height: 60px;">
                <span class="fw-bold">1</span>
              </div>
              <h4>Search Locations</h4>
              <p class="text-muted">Browse available parking lots in your desired area</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="step-card text-center">
              <div class="step-number bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                   style="width: 60px; height: 60px;">
                <span class="fw-bold">2</span>
              </div>
              <h4>Book Your Spot</h4>
              <p class="text-muted">Select your preferred time slot and reserve instantly</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="step-card text-center">
              <div class="step-number bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                   style="width: 60px; height: 60px;">
                <span class="fw-bold">3</span>
              </div>
              <h4>Park & Enjoy</h4>
              <p class="text-muted">Arrive at your reserved spot and enjoy hassle-free parking</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section bg-dark text-white py-5">
      <div class="container text-center">
        <h2 class="display-5 fw-bold mb-3">Ready to Park Smart?</h2>
        <p class="lead mb-4">Join thousands of users who have simplified their parking experience</p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/register" class="btn btn-primary btn-lg">
            Sign Up Now
          </router-link>
          <router-link to="/parking-lots" class="btn btn-outline-light btn-lg">
            Explore Locations
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

export default {
  name: 'HomeView',
  setup() {
    const stats = ref(null)
    const loading = ref(false)

    const fetchStats = async () => {
      try {
        loading.value = true
        const response = await api.get('/public/stats')
        stats.value = response.data
      } catch (error) {
        console.log('Stats not available:', error)
        // Don't show error to user, just continue without stats
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchStats()
    })

    return {
      stats,
      loading
    }
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
  min-height: 500px;
}

.hero-image {
  font-size: 8rem;
  opacity: 0.1;
}

.feature-card {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.step-card {
  padding: 2rem 1rem;
}

.stat-item h3 {
  font-size: 3rem;
}

.cta-section {
  background: linear-gradient(135deg, #212529 0%, #495057 100%);
}

@media (max-width: 768px) {
  .hero-section {
    min-height: 400px;
  }
  
  .hero-image {
    font-size: 4rem;
    margin-top: 2rem;
  }
  
  .stat-item h3 {
    font-size: 2rem;
  }
}
</style>
