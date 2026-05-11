const API_BASE_URL = "https://api-support.anasxonummataliy.dev/api"


const api = {

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    console.log("API Request:", url, options)

    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include",
      ...options,
    }

    const accessToken = localStorage.getItem("access_token")
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    try {
      const response = await fetch(url, config)
      console.log("API Response:", response.status, response.statusText)


      if (response.status === 401 && accessToken) {
        console.log("Token expired, trying to refresh...")
        const refreshed = await this.refreshToken()
        if (refreshed) {
          config.headers.Authorization = `Bearer ${localStorage.getItem("access_token")}`
          return await fetch(url, config)
        } else {
          localStorage.removeItem("access_token")
          localStorage.removeItem("currentUser")
          window.location.href = "index.html"
          return response
        }
      }

      return response
    } catch (error) {
      console.error("API request failed:", error)

      return this.getMockResponse(endpoint, options)
    }
  },


  async login(email, password) {
    console.log("API login called with:", email)
    const response = await this.request("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
    return response
  },

  async register(userData) {
    console.log("API register called with:", userData)
    const response = await this.request("/register", {
      method: "POST",
      body: JSON.stringify(userData),
    })
    return response
  },

  async refreshToken() {
    try {
      const response = await this.request("/refresh", {
        method: "POST",
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem("access_token", data.access_token)
        return true
      }
      return false
    } catch (error) {
      console.error("Token refresh failed:", error)
      return false
    }
  },

  async getCurrentUser() {
    const response = await this.request("/me")
    return response
  },


  async createSupportRequest(requestData) {
    const response = await this.request("/support_request", {
      method: "POST",
      body: JSON.stringify(requestData),
    })
    return response
  },

  async createSupportRequestWithUser(data) {
    console.log("Creating support request with user:", data)
    const response = await this.request("/support_request_with_user", {
      method: "POST",
      body: JSON.stringify(data),
    })
    return response
  },

  async getSupportRequests() {
    const response = await this.request("/support_request")
    return response
  },

  async updateSupportStatus(requestId, status) {
    const response = await this.request(`/support_request/status/${requestId}`, {
      method: "PUT",
      body: JSON.stringify(status),
    })
    return response
  },

  async sendSupportMaster(requestId) {
    const response = await this.request(`/support_request/send_master/${requestId}`, {
      method: "POST",
    })
    return response
  },

  async updateSupportMaster(requestId, data) {
    const response = await this.request(`/support_request/master/${requestId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    })
    return response
  },


  async getUsers() {
    const response = await this.request("/users")
    return response
  },

  async updateUser(userId, userData) {
    console.log("Updating user:", userId, userData)
    const response = await this.request(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(userData),
    })
    return response
  },

  async createUser(userData) {
    const response = await this.request("/users", {
      method: "POST",
      body: JSON.stringify(userData),
    })
    return response
  },

  async deleteUser(userId) {
    const response = await this.request(`/users/${userId}`, {
      method: "DELETE",
    })
    return response
  },


  async getComponents() {
    const response = await this.request("/components")
    return response
  },

  async createComponent(componentData) {
    const response = await this.request("/components", {
      method: "POST",
      body: JSON.stringify(componentData),
    })
    return response
  },

  async updateUserMe(userData){
    const response = await this.request("/user", {
      method: "PATCH",
      body: JSON.stringify(userData),
    })
    return response
  },

  async updateComponent(componentId, componentData) {
    const response = await this.request(`/components/${componentId}`, {
      method: "PATCH",
      body: JSON.stringify(componentData),
    })
    return response
  },

  async deleteComponent(componentId) {
    const response = await this.request(`/components/${componentId}`, {
      method: "DELETE",
    })
    return response
  },


  getMockResponse(endpoint, options) {
    console.log("Using mock data for:", endpoint)

    if (endpoint === "/login" && options.method === "POST") {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            access_token: "mock_token_" + Date.now(),
            user: {
              id: 1,
              first_name: "Test",
              last_name: "User",
              email: "test@example.com",
              role: "master",
            },
          }),
      })
    }

    if (endpoint === "/me") {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 1,
            first_name: "Test",
            last_name: "Master",
            email: "master@example.com",
            phone: "+998901234567",
            role: "master",
          }),
      })
    }

    if (endpoint === "/support_request") {
      if (options.method === "POST") {
        return Promise.resolve({ ok: true })
      }
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: "1",
              device_model: "Laptop Dell",
              problem_area: "Screen",
              status: "checked",
              issue_type: "hardware",
              description: "Ekran miltillaydi",
              location: "Tashkent",
              created_at: new Date().toISOString(),
              user_name: "John Doe",
              component_id: null,
              quantity: null,
              price: null,
              end_date: null,
            },
            {
              id: "2",
              device_model: "MacBook Pro",
              problem_area: "Keyboard",
              status: "in_progress",
              issue_type: "hardware",
              description: "Klaviatura ishlamayapti",
              location: "Samarkand",
              created_at: new Date().toISOString(),
              user_name: "Jane Smith",
              component_id: "1",
              quantity: 1,
              price: 150.0,
              end_date: "2024-01-15T10:00:00.000Z",
            },
            {
              id: "3",
              device_model: "HP Desktop",
              problem_area: "RAM",
              status: "completed",
              issue_type: "hardware",
              description: "RAM yetishmayapti",
              location: "Bukhara",
              created_at: new Date().toISOString(),
              user_name: "Bob Johnson",
              component_id: "2",
              quantity: 2,
              price: 160.0,
              end_date: "2024-01-10T15:30:00.000Z",
            },
          ]),
      })
    }

    if (endpoint === "/components") {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: "1",
              title: "Klaviatura",
              description: "Laptop klaviaturasi",
              price: 50,
              in_stock: 10,
            },
            {
              id: "2",
              title: "RAM 8GB",
              description: "DDR4 8GB RAM",
              price: 80,
              in_stock: 15,
            },
            {
              id: "3",
              title: "SSD 256GB",
              description: "SATA SSD 256GB",
              price: 120,
              in_stock: 8,
            },
          ]),
      })
    }

    if (endpoint.includes("/support_request/master/") && options.method === "PATCH") {
      console.log("Mock: Updating support request master data:", options.body)
      return Promise.resolve({ ok: true })
    }

    if (endpoint.includes("/support_request/status/") && options.method === "PUT") {
      return Promise.resolve({ ok: true })
    }


    return Promise.resolve({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: "API endpoint not found" }),
    })
  },
}


window.api = api
