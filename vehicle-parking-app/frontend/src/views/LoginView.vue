<template>
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            <div class="card shadow-sm">
                <div class="card-body">
                    <h2 class="card-title text-center mb-4">Login</h2>
                    <form @submit.prevent="handleLogin">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" v-model="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" v-model="password" required>
                        </div>
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="isAdmin" v-model="isAdmin">
                            <label class="form-check-label" for="isAdmin">Login as Admin</label>
                        </div>
                        <div v-if="error" class="alert alert-danger">{{ error }}</div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                Login
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
const password = ref('');
const isAdmin = ref(false);
const loading = ref(false);
const error = ref(null);

const router = useRouter();
const authStore = useAuthStore();

const handleLogin = async () => {
    loading.value = true;
    error.value = null;
    try {
        await authStore.login({ username: username.value, password: password.value }, isAdmin.value);
        if (isAdmin.value) {
            router.push('/admin');
        } else {
            router.push('/dashboard');
        }
    } catch (err) {
        error.value = 'Login failed. Please check your credentials.';
        console.error(err);
    } finally {
        loading.value = false;
    }
};
</script>
