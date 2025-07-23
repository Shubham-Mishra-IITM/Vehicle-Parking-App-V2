<template>
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h2 class="card-title text-center mb-4">Create an Account</h2>
                    <form @submit.prevent="handleRegister">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" v-model="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" v-model="email" required>
                        </div>
                        <div class="mb-3">
                            <label for="phone" class="form-label">Phone Number</label>
                            <input type="tel" class="form-control" id="phone" v-model="phone_number" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" v-model="password" required>
                        </div>
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                Register
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const username = ref('');
const email = ref('');
const phone_number = ref('');
const password = ref('');
const loading = ref(false);
const error = ref(null);

const router = useRouter();
const authStore = useAuthStore();

const handleRegister = async () => {
    loading.value = true;
    error.value = null;
    try {
        await authStore.register({
            username: username.value,
            email: email.value,
            phone_number: phone_number.value,
            password: password.value,
        });
        router.push('/dashboard');
    } catch (err) {
        error.value = 'Registration failed. Please try again.';
        console.error(err);
    } finally {
        loading.value = false;
    }
};
</script>
