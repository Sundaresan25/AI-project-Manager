```markdown
# Frontend Architecture Document: Food Delivery App

This document outlines the frontend architecture for the Food Delivery App, focusing on a React-based implementation for the Customer Web App, Restaurant Dashboard, and Admin Dashboard, and a React Native approach for the Customer Mobile App and Delivery Driver App (though the core React principles will apply to both). The design emphasizes accessibility, maintainability, clean component boundaries, and user-focused flows, aligning with the project's MVP requirements.

## 1. React Project Folder Structure

A consistent and logical folder structure is crucial for maintainability, especially as the application grows. We will adopt a feature-first approach, grouping related files by their domain.

``````

## 2. Routing Map

We will use `react-router-dom` for client-side routing. Authentication guards will protect routes based on user roles.

### Public Routes:
*   `/` (Redirects to `/login` if unauthenticated, or `/customer/home` / `/restaurant/dashboard` etc. if authenticated)
*   `/login`
*   `/register` (with role selection/separate paths like `/register/customer`, `/register/restaurant`, `/register/driver`)
*   `/forgot-password`
*   `/reset-password/:token`

### Authenticated Routes (Protected by `AuthGuard`):

#### Customer Routes:
*   `/customer/home` (Restaurant list, search)
*   `/customer/restaurants/:id` (Restaurant detail, menu)
*   `/customer/cart`
*   `/customer/checkout`
*   `/customer/orders` (Order history)
*   `/customer/orders/:id` (Order tracking)
*   `/customer/profile`

#### Restaurant Routes:
*   `/restaurant/dashboard` (Incoming orders, quick stats)
*   `/restaurant/menu` (Menu item management)
*   `/restaurant/orders` (Current and past orders)
*   `/restaurant/profile` (Restaurant profile management, operating hours)

#### Delivery Driver Routes (Conceptual for React Native, but web equivalent):
*   `/driver/dashboard` (Available deliveries, current delivery)
*   `/driver/deliveries` (Delivery history, earnings)
*   `/driver/profile`

#### Admin Routes:
*   `/admin/dashboard` (Overview)
*   `/admin/users` (Manage customers, restaurants, drivers)
*   `/admin/restaurants/pending` (Approve new restaurants)
*   `/admin/orders` (Monitor all orders)

### Route Guards:
*   **`AuthGuard`**: Checks if a user is authenticated. If not, redirects to `/login`.
*   **`RoleGuard`**: Checks if the authenticated user has the required role(s) for the route. If not, redirects to a forbidden page or their respective dashboard.

``````

## 3. Pages

Pages are top-level components that represent a full view or screen in the application. They orchestrate data fetching, state management, and compose smaller components.

### Customer Pages:
*   **`HomePage.jsx`**: Displays a list of nearby restaurants, search bar, filters (cuisine, rating).
*   **`RestaurantListPage.jsx`**: Dedicated page for browsing and filtering restaurants.
*   **`RestaurantDetailPage.jsx`**: Shows restaurant details, menu categories, and menu items. Allows adding items to cart.
*   **`CartPage.jsx`**: Displays current cart items, allows quantity adjustments, removal, and shows summary (subtotal, fees).
*   **`CheckoutPage.jsx`**: Collects delivery address, payment method, and finalizes the order.
*   **`OrderTrackingPage.jsx`**: Shows real-time order status updates (e.g., "Preparing", "Out for Delivery").
*   **`OrderHistoryPage.jsx`**: Lists past orders with details.
*   **`CustomerProfilePage.jsx`**: Allows customers to view/edit their profile, saved addresses (MVP: single address).

### Restaurant Pages:
*   **`RestaurantDashboardPage.jsx`**: Overview of new incoming orders, current active orders, and quick stats.
*   **`MenuManagementPage.jsx`**: Interface for adding, editing, deleting, and marking menu items as out of stock.
*   **`OrderManagementPage.jsx`**: Detailed view of incoming and active orders, with actions to accept/reject/update status.
*   **`RestaurantProfilePage.jsx`**: Manage restaurant details, operating hours, logo.

### Delivery Driver Pages (Conceptual for React Native):
*   **`DriverDashboardPage.jsx`**: Displays available delivery requests, current accepted delivery.
*   **`AvailableDeliveriesPage.jsx`**: List of pending delivery requests with pickup/drop-off info.
*   **`CurrentDeliveryPage.jsx`**: Shows route, customer details, and allows updating delivery status.
*   **`DeliveryHistoryPage.jsx`**: Lists completed deliveries and earnings.
*   **`DriverProfilePage.jsx`**: Driver profile management.

### Admin Pages:
*   **`AdminDashboardPage.jsx`**: High-level overview of platform activity (users, orders, revenue).
*   **`UserManagementPage.jsx`**: List and manage (view, suspend) customer, restaurant, and driver accounts.
*   **`RestaurantApprovalPage.jsx`**: List of restaurants awaiting approval, with approve/reject actions.
*   **`AdminOrderMonitoringPage.jsx`**: View all active and past orders across the platform.

## 4. Components

Components are the building blocks of the UI. They should be small, focused, and reusable.

### Common/UI Components (`src/components/common` & `src/components/ui`):
*   **`Button`**: Primary, secondary, danger, disabled states.
*   **`Input`**: Text, email, password, number inputs with labels and error states.
*   **`Textarea`**: Multiline text input.
*   **`Select`**: Dropdown for choices (e.g., cuisine type).
*   **`Checkbox` / `Radio`**: Form elements.
*   **`Modal`**: For confirmations, forms, or detailed views.
*   **`Spinner` / `LoadingIndicator`**: For asynchronous operations.
*   **`Alert` / `Toast`**: For displaying success, error, or info messages.
*   **`Card`**: Generic container for content.
*   **`Avatar`**: User/restaurant profile images.
*   **`StarRating`**: For displaying ratings.
*   **`Pagination`**: For lists of items.
*   **`Table`**: For displaying tabular data (e.g., orders, users).
*   **`Badge`**: For status indicators (e.g., "New Order", "Delivered").

### Layout Components (`src/components/layout`):
*   **`Header`**: Application header with logo, navigation, user menu.
*   **`Footer`**: Application footer with copyright, links.
*   **`Sidebar` / `Navbar`**: Navigation components for dashboards.
*   **`PageLayout`**: Wrapper for consistent page structure (header, content, footer).

### Feature-Specific Components (`src/pages/<feature>/components` or directly in page files):
*   **`RestaurantCard`**: Displays a single restaurant's summary (name, cuisine, rating, delivery time).
*   **`MenuItemCard`**: Displays a single menu item with name, description, price, add-to-cart button.
*   **`CartItem`**: Displays an item in the cart, with quantity controls.
*   **`OrderSummary`**: Displays breakdown of cart/order total.
*   **`OrderCard`**: Displays a summary of a single order in history/dashboard.
*   **`OrderDetails`**: Detailed view of an order.
*   **`DeliveryStatusTracker`**: Visual timeline of order status.
*   **`RestaurantForm`**: Form for restaurant profile management.
*   **`MenuItemForm`**: Form for adding/editing menu items.
*   **`UserTable`**: Table for displaying and managing users (Admin).
*   **`DeliveryRequestCard`**: Displays an available delivery request for drivers.

## 5. Dashboard Behavior

Dashboards are central to each user role, providing an overview and actionable insights.

### Customer Dashboard (Home Page):
*   **Restaurant Browsing:** Displays a dynamic list of restaurants. Users can scroll, search by name, and filter by cuisine type.
*   **Interactive Elements:** Clicking a restaurant card navigates to its detail page. "Add to Cart" buttons on menu items.
*   **Order Tracking:** A prominent section or notification for the most recent active order, linking to the `OrderTrackingPage`.
*   **Notifications:** Display toast notifications for order status updates (e.g., "Order Accepted!", "Out for Delivery!").

### Restaurant Dashboard:
*   **Real-time Order Notifications:** New incoming orders will trigger a visual and auditory alert (e.g., a flashing card, a sound).
*   **Order Management:**
    *   **New Orders Tab:** Displays orders awaiting acceptance. Each order card will have "Accept" and "Reject" buttons.
    *   **Active Orders Tab:** Displays orders currently being prepared or ready for pickup. Each order card will have "Update Status" (e.g., "Preparing", "Ready for Pickup") buttons.
    *   **Order Details:** Clicking an order card opens a modal or navigates to a detail page showing customer info, delivery address, and ordered items.
*   **Menu Management Link:** Easy access to the `MenuManagementPage`.
*   **Profile Management Link:** Easy access to `RestaurantProfilePage`.
*   **Loading/Empty/Error States:** Clearly indicate when data is loading, no new orders are available, or an error occurred during data fetching.

### Delivery Driver Dashboard (Conceptual for React Native):
*   **Available Deliveries:** A list of new delivery requests, showing pickup/drop-off locations, estimated earnings. Each request will have "Accept" and "Decline" buttons.
*   **Current Delivery:** Once a delivery is accepted, it moves to a "Current Delivery" section, showing the route (via map integration), customer details, and "Picked Up" / "Delivered" buttons.
*   **Earnings Overview:** A summary of daily/weekly earnings.
*   **Status Updates:** Drivers update the status of the delivery (e.g., "Picked Up", "On the Way", "Delivered"), which triggers notifications to the customer and restaurant.

### Admin Dashboard:
*   **Overview Widgets:** Cards displaying key metrics like total users, active restaurants, total orders (MVP: basic counts).
*   **User Management:** A table listing all users (customers, restaurants, drivers) with options to view details or suspend accounts.
*   **Restaurant Approval:** A dedicated section or table for new restaurant registrations awaiting approval, with "Approve" and "Suspend" actions.
*   **Order Monitoring:** A table showing all active orders with their current status.
*   **Search and Filter:** Functionality to search and filter users, restaurants, and orders.

## 6. Authentication UI

The authentication UI will be clean, intuitive, and provide clear feedback to the user.

### Login Page (`LoginPage.jsx`):
*   **Fields:** Email, Password.
*   **Actions:** "Login" button.
*   **Links:** "Forgot Password?", "Don't have an account? Register".
*   **Validation:** Client-side validation for email format and password length.
*   **Error Handling:** Display clear error messages for invalid credentials or API errors.
*   **Loading State:** Disable button and show spinner during API call.

### Registration Page (`RegisterPage.jsx`):
*   **Fields:**
    *   **Common:** Email, Password, Confirm Password.
    *   **Role Selection:** A clear way to select the user role (Customer, Restaurant, Driver). This could be radio buttons, a dropdown, or separate registration paths (e.g., `/register/customer`).
    *   **Role-Specific (MVP):**
        *   Customer: First Name, Last Name.
        *   Restaurant: Restaurant Name, Address, Cuisine Type.
        *   Driver: First Name, Last Name, Phone Number.
*   **Actions:** "Register" button.
*   **Links:** "Already have an account? Login".
*   **Validation:** Client-side validation for all fields, password matching, and email uniqueness (checked on blur or submit).
*   **Error Handling:** Display specific error messages (e.g., "Email already exists", "Passwords do not match").
*   **Loading State:** Disable button and show spinner during API call.

### Forgot Password Page (`ForgotPasswordPage.jsx`):
*   **Fields:** Email.
*   **Actions:** "Send Reset Link" button.
*   **Feedback:** Informative message after submission (e.g., "If an account with that email exists, a reset link has been sent.").

### Reset Password Page (`ResetPasswordPage.jsx`):
*   **Fields:** New Password, Confirm New Password.
*   **Actions:** "Reset Password" button.
*   **Validation:** Client-side validation for password strength and matching.
*   **Success/Error:** Clear messages upon successful reset or failure.

### General Authentication UI Principles:
*   **Consistent Branding:** Use consistent colors, typography, and layout.
*   **Accessibility:** Ensure all form fields have proper labels, focus management, and keyboard navigation.
*   **Responsiveness:** Adapt layout for different screen sizes.
*   **Session Persistence:** After successful login, store the JWT access token securely (e.g., in `localStorage` for web, secure storage for mobile) and use it for subsequent API calls. Handle refresh tokens if implemented by the backend.

## 7. API Client Structure

The frontend will interact with the FastAPI backend through a centralized API client, built using `axios`. This approach promotes consistency, error handling, and easier maintenance.

``````

### Service Modules (`src/services/*.js`):
Each backend service will have a corresponding frontend service module that uses `apiClient` to make specific API calls. This provides a clean abstraction layer.

``````

## 8. State Management Plan

For the MVP, a combination of React Context API and a lightweight state management library like Zustand will be used. This provides a good balance between simplicity and scalability.

### Global State (Zustand):
*   **`authStore.js`**: Manages user authentication status, `accessToken`, `userRole`, and user details.
    *   Actions: `login`, `logout`, `setAuthData`.
    *   Persists `accessToken` and `userRole` to `localStorage` for session persistence.
*   **`cartStore.js`**: Manages the customer's shopping cart.
    *   State: `items` (array of `{ menuItemId, quantity, price, name }`), `totalAmount`.
    *   Actions: `addItem`, `removeItem`, `updateItemQuantity`, `clearCart`.
    *   Persists cart state to `localStorage`.
*   **`notificationStore.js`**: Manages global toast notifications.
    *   State: `notifications` (array of `{ id, message, type }`).
    *   Actions: `addNotification`, `removeNotification`.

### Component-Level State (React `useState` & `useReducer`):
*   For UI-specific state that doesn't need to be shared globally (e.g., form input values, modal visibility, loading states within a component).
*   `useReducer` can be used for more complex local state logic.

### Data Fetching & Caching (React Query / SWR - Future Consideration):
For more advanced data fetching, caching, and synchronization with the backend, libraries like React Query or SWR would be beneficial. For MVP, direct `axios` calls within `useEffect` or event handlers are sufficient, with loading and error states managed locally.

``````

## 9. Accessibility and Responsive Design Guidance

### Accessibility (A11y):
*   **Semantic HTML:** Use appropriate HTML5 semantic elements (e.g., `<nav>`, `<main>`, `<aside>`, `<article>`, `<section>`, `<header>`, `<footer>`) to convey meaning and structure to assistive technologies.
*   **ARIA Attributes:** Employ ARIA (Accessible Rich Internet Applications) attributes when native HTML semantics are insufficient (e.g., `aria-label`, `aria-describedby`, `role`, `aria-live` for dynamic content updates).
*   **Keyboard Navigation:** Ensure all interactive elements (buttons, links, form fields, modals) are reachable and operable via keyboard (`Tab`, `Enter`, `Space`, arrow keys). Manage focus effectively, especially for modals and dynamic content.
*   **Color Contrast:** Adhere to WCAG 2.1 guidelines for minimum color contrast ratios (at least 4.5:1 for normal text, 3:1 for large text and UI components) to ensure readability for users with low vision.
*   **Form Labels:** All form inputs must have associated `<label>` elements, using the `for` attribute linked to the input's `id`. Placeholder text is not a substitute for labels.
*   **Image Alt Text:** Provide descriptive `alt` text for all meaningful images (`<img alt="Description of image">`). Decorative images can have empty `alt=""`.
*   **Focus Indicators:** Ensure visible focus indicators (outline) are present for all interactive elements when navigated via keyboard.
*   **Screen Reader Compatibility:** Test with screen readers (e.g., NVDA, JAWS, VoiceOver) to ensure content is announced correctly and navigation is logical.
*   **Error Messages:** Associate error messages with their respective form fields using `aria-describedby` and provide clear, actionable feedback.

### Responsive Design:
*   **Mobile-First Approach:** Design and develop for smaller screens first, then progressively enhance for larger screens. This forces a focus on essential content and performance.
*   **Flexible Layouts:** Utilize CSS Flexbox and Grid for creating adaptable and responsive layouts that adjust gracefully to different screen sizes.
*   **Relative Units:** Use relative units like `rem` for font sizes, `em` for spacing, and `vw`/`vh` for viewport-relative dimensions where appropriate, instead of fixed `px` values.
*   **Media Queries:** Employ CSS Media Queries to apply specific styles based on screen width, height, orientation, or resolution.
*   **Fluid Images and Media:** Ensure images and other media are fluid (`max-width: 100%; height: auto;`) to prevent overflow on smaller screens.
*   **Viewport Meta Tag:** Include `<meta name="viewport" content="width=device-width, initial-scale=1.0">` in `public/index.html` to ensure proper scaling on mobile devices.
*   **Touch Targets:** Ensure interactive elements (buttons, links) have sufficiently large touch targets (at least 48x48 CSS pixels) for mobile users.
*   **Testing:** Regularly test the application on various devices and screen sizes (using browser developer tools or actual devices) to verify responsiveness.

## 10. Frontend Test Plan

A robust frontend test plan ensures the application is reliable, functions as expected, and maintains quality over time.

### 10.1. Unit Tests
*   **Scope:** Individual React components (presentational and container), custom hooks, utility functions, and Redux/Zustand stores.
*   **Tools:**
    *   **Jest:** Test runner and assertion library.
    *   **React Testing Library (RTL):** For testing React components, focusing on user behavior rather than implementation details.
*   **Strategy:**
    *   **Components:** Test rendering, props handling, event interactions (clicks, input changes), and conditional rendering. Mock API calls and global state.
    *   **Hooks:** Test the logic and return values of custom hooks in isolation.
    *   **Utilities:** Test pure functions with various inputs and expected outputs.
    *   **State Stores:** Test state updates and selectors.
*   **Example (Component Test with RTL):**
    ```
food-delivery-frontend/
├── public/
│   ├── index.html
│   └── ... (static assets like manifest.json, favicons)
├── src/
│   ├── assets/                 # Images, icons, fonts
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   ├── components/             # Reusable UI components (presentational, generic)
│   │   ├── common/             # Highly reusable, generic components (Button, Input, Modal)
│   │   │   ├── Button/
│   │   │   │   ├── Button.jsx
│   │   │   │   └── Button.module.css
│   │   │   ├── Input/
│   │   │   └── ...
│   │   ├── layout/             # Layout-specific components (Header, Footer, Sidebar, Navbar)
│   │   │   ├── Header.jsx
│   │   │   └── Footer.jsx
│   │   └── ui/                 # More complex, but still generic UI components (e.g., StarRating, Carousel)
│   │       ├── StarRating.jsx
│   │       └── ...
│   ├── contexts/               # React Context API for global state (e.g., AuthContext, CartContext)
│   │   ├── AuthContext.jsx
│   │   └── CartContext.jsx
│   ├── hooks/                  # Reusable custom React hooks (e.g., useAuth, useDebounce)
│   │   ├── useAuth.js
│   │   └── useDebounce.js
│   ├── pages/                  # Top-level components representing distinct views/routes
│   │   ├── auth/               # Authentication related pages
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── ForgotPasswordPage.jsx
│   │   ├── customer/           # Customer-specific pages
│   │   │   ├── HomePage.jsx
│   │   │   ├── RestaurantListPage.jsx
│   │   │   ├── RestaurantDetailPage.jsx
│   │   │   ├── CartPage.jsx
│   │   │   ├── CheckoutPage.jsx
│   │   │   ├── OrderTrackingPage.jsx
│   │   │   ├── OrderHistoryPage.jsx
│   │   │   └── CustomerProfilePage.jsx
│   │   ├── restaurant/         # Restaurant-specific pages
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── MenuManagementPage.jsx
│   │   │   ├── OrderManagementPage.jsx
│   │   │   └── RestaurantProfilePage.jsx
│   │   ├── driver/             # Delivery Driver-specific pages (for React Native app, but conceptually similar)
│   │   │   ├── DriverDashboardPage.jsx
│   │   │   ├── AvailableDeliveriesPage.jsx
│   │   │   └── DriverProfilePage.jsx
│   │   ├── admin/              # Admin-specific pages
│   │   │   ├── AdminDashboardPage.jsx
│   │   │   ├── UserManagementPage.jsx
│   │   │   └── RestaurantApprovalPage.jsx
│   │   └── NotFoundPage.jsx
│   ├── services/               # API client modules, interacting with the backend
│   │   ├── apiClient.js        # Axios instance, interceptors
│   │   ├── authService.js
│   │   ├── userService.js
│   │   ├── restaurantService.js
│   │   ├── orderService.js
│   │   └── driverService.js
│   ├── store/                  # State management (e.g., Zustand stores or Redux slices)
│   │   ├── authStore.js
│   │   ├── cartStore.js
│   │   └── ...
│   ├── styles/                 # Global styles, variables, utility classes
│   │   ├── index.css           # Global CSS resets, base styles
│   │   ├── variables.css       # CSS variables for colors, typography, spacing
│   │   └── utilities.css       # Helper classes
│   ├── utils/                  # Utility functions (e.g., formatters, validators)
│   │   ├── helpers.js
│   │   └── validators.js
│   ├── App.jsx                 # Main application component, handles routing
│   ├── index.js                # Entry point for React application
│   └── reportWebVitals.js
├── .env                        # Environment variables
├── .eslintrc.js                # ESLint configuration
├── .prettierrc                 # Prettier configuration
├── package.json
├── README.md
└── ...
jsx
// Example in App.jsx or a dedicated Router.jsx
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
// ... import other pages

const AuthGuard = ({ allowedRoles }) => {
  const { isAuthenticated, userRole, isLoading } = useAuth();

  if (isLoading) return <div>Loading authentication...</div>; // Or a spinner

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(userRole)) {
    // Redirect to a forbidden page or user's dashboard
    return <Navigate to={`/${userRole}/dashboard`} replace />;
  }

  return <Outlet />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<Navigate to="/customer/home" replace />} /> {/* Default redirect */}

        {/* Customer Protected Routes */}
        <Route element={<AuthGuard allowedRoles={['customer']} />}>
          <Route path="/customer/home" element={<CustomerHomePage />} />
          <Route path="/customer/restaurants/:id" element={<RestaurantDetailPage />} />
          <Route path="/customer/cart" element={<CartPage />} />
          <Route path="/customer/checkout" element={<CheckoutPage />} />
          <Route path="/customer/orders" element={<OrderHistoryPage />} />
          <Route path="/customer/orders/:id" element={<OrderTrackingPage />} />
          <Route path="/customer/profile" element={<CustomerProfilePage />} />
        </Route>

        {/* Restaurant Protected Routes */}
        <Route element={<AuthGuard allowedRoles={['restaurant']} />}>
          <Route path="/restaurant/dashboard" element={<RestaurantDashboardPage />} />
          <Route path="/restaurant/menu" element={<MenuManagementPage />} />
          <Route path="/restaurant/orders" element={<OrderManagementPage />} />
          <Route path="/restaurant/profile" element={<RestaurantProfilePage />} />
        </Route>

        {/* Admin Protected Routes */}
        <Route element={<AuthGuard allowedRoles={['admin']} />}>
          <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
          <Route path="/admin/users" element={<UserManagementPage />} />
          <Route path="/admin/restaurants/pending" element={<RestaurantApprovalPage />} />
          <Route path="/admin/orders" element={<AdminOrderMonitoringPage />} />
        </Route>

        {/* Catch-all for 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
}
javascript
// src/services/apiClient.js
import axios from 'axios';
import { authStore } from '../store/authStore'; // Assuming Zustand for auth state

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = authStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh (if applicable)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Handle 401 Unauthorized errors (e.g., token expired)
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // In a real app, you'd attempt to refresh the token here
      // For MVP, simply log out the user
      authStore.getState().logout();
      window.location.href = '/login'; // Redirect to login
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
javascript
// src/services/authService.js
import apiClient from './apiClient';

export const login = async (email, password) => {
  const response = await apiClient.post('/auth/login', new URLSearchParams({ username: email, password: password }));
  return response.data;
};

export const register = async (userData, role) => {
  const response = await apiClient.post(`/auth/register?role=${role}`, userData);
  return response.data;
};

// src/services/restaurantService.js
import apiClient from './apiClient';

export const getRestaurants = async (params) => {
  const response = await apiClient.get('/restaurants', { params });
  return response.data;
};

export const getRestaurantDetails = async (id) => {
  const response = await apiClient.get(`/restaurants/${id}`);
  return response.data;
};

export const getRestaurantMenu = async (id) => {
  const response = await apiClient.get(`/restaurants/${id}/menu`);
  return response.data;
};

// ... other service functions for menu management, orders, etc.
javascript
// src/store/authStore.js (Example using Zustand)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const authStore = create(
  persist(
    (set) => ({
      accessToken: null,
      userRole: null,
      user: null,
      isAuthenticated: false,
      login: (token, role, userData) => set({ accessToken: token, userRole: role, user: userData, isAuthenticated: true }),
      logout: () => set({ accessToken: null, userRole: null, user: null, isAuthenticated: false }),
      setUser: (userData) => set({ user: userData }),
    }),
    {
      name: 'auth-storage', // name of the item in localStorage
      getStorage: () => localStorage,
    }
  )
);

// src/contexts/AuthContext.jsx (Example using React Context for hooks)
import React, { createContext, useContext, useEffect, useState } from 'react';
import { authStore } from '../store/authStore';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const { accessToken, userRole, user, isAuthenticated, login, logout, setUser } = authStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Perform initial check, e.g., validate token with backend if needed
    setIsLoading(false); // For MVP, assume token from localStorage is valid initially
  }, []);

  const value = {
    accessToken,
    userRole,
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
javascript
    // src/components/common/Button/Button.test.jsx
    import { render, screen, fireEvent } from '@testing-library/react';
    import Button from './Button';

    test('renders button with correct text', () => {
      render(<Button>Click Me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    test('calls onClick handler when clicked', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Test Button</Button>);
      fireEvent.click(screen.getByRole('button', { name: /test button/i }));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    test('button is disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled Button</Button>);
      expect(screen.getByRole('button', { name: /disabled button/i })).toBeDisabled();
    });
    ```

### 10.2. Integration Tests
*   **Scope:** Interactions between multiple components, pages, and API services (mocked). Focus on user flows within a specific feature.
*   **Tools:** Jest, React Testing Library.
*   **Strategy:**
    *   **Pages:** Test how components on a page interact, how data flows from API calls (mocked) to UI, and user interactions that span multiple components.
    *   **Routing:** Test navigation between pages.
    *   **Forms:** Test complete form submission flows, including validation and API interaction (mocked).
*   **Example (Page Integration Test):**
    ```javascript
    // src/pages/auth/LoginPage.test.jsx
    import { render, screen, fireEvent, waitFor } from '@testing-library/react';
    import { BrowserRouter as Router } from 'react-router-dom';
    import LoginPage from './LoginPage';
    import * as authService from '../../services/authService'; // Mock this service

    jest.mock('../../services/authService'); // Mock the entire module

    test('allows user to log in successfully', async () => {
      authService.login.mockResolvedValue({ access_token: 'fake-token', token_type: 'bearer' });

      render(
        <Router>
          <LoginPage />
        </Router>
      );

      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
      fireEvent.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith('test@example.com', 'password123');
        // In a real test, you'd assert navigation or global state update
        // For now, just check service call
      });
    });
    ```

### 10.3. End-to-End (E2E) Tests
*   **Scope:** Simulate real user journeys across the entire application, interacting with the deployed frontend and a running backend (test environment).
*   **Tools:**
    *   **Cypress:** Popular E2E testing framework.
*   **Strategy:**
    *   **Critical User Flows:** Test the most important paths (e.g., Customer: register -> login -> browse -> add to cart -> checkout -> track order).
    *   **Cross-Browser Testing:** Ensure functionality across different browsers.
    *   **Data Setup/Teardown:** Use Cypress commands or backend API calls to set up and clean up test data before/after each test.
    *   **Visual Regression (Optional):** Integrate tools to detect unintended UI changes.
*   **Example (Cypress Test):**
    ```javascript
    // cypress/e2e/customer_order_flow.cy.js
    describe('Customer Order Flow', () => {
      beforeEach(() => {
        // Seed test data or log in a test user
        cy.visit('/login');
        cy.get('input[name="email"]').type('customer@example.com');
        cy.get('input[name="password"]').type('password123');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/customer/home');
      });

      it('allows a customer to browse, add to cart, and place an order', () => {
        cy.get('[data-testid="restaurant-card"]').first().click(); // Click first restaurant
        cy.url().should('include', '/customer/restaurants/');

        cy.get('[data-testid="menu-item-card"]').first().find('button[name="add-to-cart"]').click();
        cy.get('[data-testid="cart-count"]').should('contain', '1');

        cy.get('[data-testid="cart-icon"]').click();
        cy.url().should('include', '/customer/cart');
        cy.get('button[name="proceed-to-checkout"]').click();
        cy.url().should('include', '/customer/checkout');

        // Fill in delivery address and payment (mocked or test credentials)
        cy.get('input[name="deliveryAddress"]').type('123 Test St, Test City');
        cy.get('button[name="place-order"]').click();

        cy.url().should('include', '/customer/orders/'); // Should navigate to order tracking
        cy.contains('Order Placed').should('be.visible');
      });
    });
    ```

### 10.4. Performance Testing (Manual/Automated)
*   **Scope:** Page load times, rendering performance, API response times from the client perspective.
*   **Tools:** Browser Developer Tools (Lighthouse, Performance tab), WebPageTest.
*   **Strategy:**
    *   Monitor critical rendering path, bundle sizes, and network requests.
    *   Identify and optimize slow components or large data fetches.

### 10.5. Accessibility Testing (Manual/Automated)
*   **Scope:** Adherence to WCAG guidelines.
*   **Tools:**
    *   **Automated:** Axe-core (integrated with Jest/Cypress), Lighthouse.
    *   **Manual:** Keyboard navigation, screen reader testing (NVDA, VoiceOver), color contrast checkers.
*   **Strategy:**
    *   Integrate automated checks into CI/CD.
    *   Conduct regular manual audits for complex interactions.

### 10.6. Test Data Management
*   For integration and E2E tests, ensure a clean and consistent test environment. This might involve:
    *   Using a dedicated test database that is reset before each test suite.
    *   Using API calls to seed specific test data (e.g., create a test user, a test restaurant) before tests run.
    *   Mocking external services (payment gateways, mapping APIs) to ensure tests are fast and deterministic.

This comprehensive frontend plan provides a solid foundation for developing a robust, accessible, and maintainable Food Delivery App.
```