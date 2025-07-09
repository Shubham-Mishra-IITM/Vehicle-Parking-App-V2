<template>
  <div class="register">
    <h2>Register</h2>
    <form @submit.prevent="registerUser">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <input type="password" v-model="confirmPassword" id="confirmPassword" required />
      </div>
      <button type="submit">Register</button>
      <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      errorMessage: ''
    };
  },
  methods: {
    async registerUser() {
      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        return;
      }
      try {
        const response = await this.$http.post('/api/register', {
          username: this.username,
          password: this.password
        });
        if (response.data.success) {
          this.$router.push('/login');
        } else {
          this.errorMessage = response.data.message;
        }
      } catch (error) {
        this.errorMessage = "An error occurred during registration.";
      }
    }
  }
};
</script>

<style scoped>
.register {
  max-width: 400px;
  margin: auto;
}
.form-group {
  margin-bottom: 15px;
}
.error {
  color: red;
}
</style>