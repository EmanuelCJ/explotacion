<template>
    <div class="login-container">
        <div class="login-form-wrapper">
            <div class="logo-section">
                <img src="@/assets/logo.png" alt="Company Logo" class="company-logo" />
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="input-group">
                    <input
                        v-model="username"
                        type="text"
                        class="input-field"
                        placeholder=" "
                        required
                    />
                    <label class="input-label">Username</label>
                </div>

                <div class="input-group">
                    <input
                        v-model="password"
                        type="password"
                        class="input-field"
                        placeholder=" "
                        required
                    />
                    <label class="input-label">Password</label>
                </div>

                <div class="form-footer">
                    <router-link to="/forgot-password" class="forgot-link">
                        Forgot Password?
                    </router-link>
                    <button type="submit" class="login-button" :disabled="loading">
                        {{ loading ? "Loading..." : "Sign In" }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import axios from "axios";

export default {
    name: "LoginComponent",
    data() {
        return {
            username: "",
            password: "",
            loading: false,
            error: null,
        };
    },
    methods: {
        async handleLogin() {
            this.loading = true;
            this.error = null;

            try {
                const response = await axios.post(
                    `${process.env.VUE_APP_API_URL}/login`,
                    {
                        username: this.username,
                        password: this.password,
                    },
                    {
                        withCredentials: true,
                    }
                );

                if (response.status === 200) {
                    this.$router.push("/dashboard");
                }
            } catch (err) {
                this.error = err.response?.data?.message || "Login failed";
                console.error("Login error:", err);
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-image: url("@/assets/background.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.login-form-wrapper {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.logo-section {
    text-align: center;
    margin-bottom: 30px;
}

.company-logo {
    max-width: 120px;
    height: auto;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.input-group {
    position: relative;
}

.input-field {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.9);
    font-size: 16px;
    transition: all 0.3s ease;
    outline: none;
}

.input-field:focus {
    border-color: rgba(255, 255, 255, 0.8);
    background: white;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.input-label {
    position: absolute;
    left: 15px;
    top: 12px;
    font-size: 16px;
    color: #666;
    pointer-events: none;
    transition: all 0.3s ease;
    background: transparent;
}

.input-field:focus ~ .input-label,
.input-field:not(:placeholder-shown) ~ .input-label {
    top: -10px;
    font-size: 12px;
    color: #333;
    background: rgba(255, 255, 255, 0.9);
    padding: 0 5px;
}

.form-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
}

.forgot-link {
    color: #333;
    text-decoration: none;
    font-size: 14px;
    transition: color 0.3s ease;
}

.forgot-link:hover {
    color: #0066cc;
    text-decoration: underline;
}

.login-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 600px) {
    .login-form-wrapper {
        padding: 30px 20px;
        max-width: 95%;
    }

    .company-logo {
        max-width: 100px;
    }

    .input-field {
        padding: 10px 12px;
        font-size: 14px;
    }

    .login-button {
        padding: 10px 20px;
        font-size: 14px;
    }
}
</style>