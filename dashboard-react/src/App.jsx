import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import axios from "axios";

import AISupport from "./components/AISupport";
import Header from "./components/Header";
import StatCard from "./components/StatCard";
import Charts from "./components/Charts";
import Notifications from "./components/Notifications";

import {
    getDashboardData,
    getNotifications
} from "./api/api";

import Login from "./Login";

const API_URL = import.meta.env.VITE_API_URL;

function App() {

    const {
        isAuthenticated,
        isLoading: authLoading,
        user,
        getAccessTokenSilently,
        logout
    } = useAuth0();

    const [dashboard, setDashboard] = useState({
        user_id: 0,
        total_posts: 0,
        total_comments: 0,
        total_likes_received: 0,
        posts: []
    });

    const [notifications, setNotifications] = useState([]);

    const [loading, setLoading] = useState(true);

    const [backendUser, setBackendUser] = useState(null);

    const [authError, setAuthError] = useState("");

    const [backendAuthenticated, setBackendAuthenticated] =
        useState(false);


    /*
     * Authenticate Auth0 user with backend
     */
    useEffect(() => {

        async function authenticateBackend() {

            if (!isAuthenticated) {
                setBackendAuthenticated(false);
                return;
            }

            try {

                setAuthError("");

                /*
                 * Get Auth0 access token
                 */
                const token =
                    await getAccessTokenSilently();

                console.log(
                    "Auth0 token received:",
                    !!token
                );


                /*
                 * Save token
                 */
                localStorage.setItem(
                    "access_token",
                    token
                );


                /*
                 * Send Auth0 token to backend
                 */
                const response =
                    await axios.get(
                        `${API_URL}/auth0/me`,
                        {
                            headers: {
                                Authorization:
                                    `Bearer ${token}`
                            }
                        }
                    );


                console.log(
                    "Backend authentication:",
                    response.data
                );


                /*
                 * Save backend user
                 */
                setBackendUser(
                    response.data
                );


                /*
                 * Backend authentication successful
                 */
                setBackendAuthenticated(true);


            } catch (error) {

                console.error(
                    "Authentication error:",
                    error
                );


                setBackendAuthenticated(false);


                setAuthError(
                    error.response?.data?.detail ||
                    "Unable to connect to the backend."
                );

            }

        }


        authenticateBackend();

    }, [
        isAuthenticated,
        getAccessTokenSilently
    ]);


    /*
     * Load dashboard data
     */
    async function loadDashboard() {

        if (!backendAuthenticated) {
            return;
        }

        try {

            setLoading(true);


            /*
             * Dashboard
             */
            const data =
                await getDashboardData();


            setDashboard(data);


            /*
             * Notifications
             */
            const notificationData =
                await getNotifications();


            setNotifications(
                notificationData
            );


        } catch (error) {

            console.error(
                "Dashboard error:",
                error
            );

        } finally {

            setLoading(false);

        }

    }


    /*
     * Load dashboard only AFTER
     * backend authentication succeeds
     */
    useEffect(() => {

        if (
            isAuthenticated &&
            backendAuthenticated
        ) {

            loadDashboard();

        }

    }, [
        isAuthenticated,
        backendAuthenticated
    ]);


    /*
     * Auth0 loading
     */
    if (authLoading) {

        return (

            <div className="auth-loading">

                Checking authentication...

            </div>

        );

    }


    /*
     * Not logged in
     */
    if (!isAuthenticated) {

        return <Login />;

    }


    /*
     * Authenticated dashboard
     */
    return (

        <div className="dashboard">

            <Header
                onRefresh={loadDashboard}
            />


            {/* USER INFORMATION */}

            <div
                style={{
                    padding: "15px 25px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                }}
            >

                <div>

                    <strong>

                        Welcome,{" "}

                        {
                            backendUser?.username ||
                            backendUser?.name ||
                            user?.name ||
                            user?.email
                        }

                    </strong>


                    {backendUser?.provider && (

                        <span
                            style={{
                                marginLeft: "10px",
                                fontSize: "13px",
                                color: "#666"
                            }}
                        >

                            Login: {backendUser.provider}

                        </span>

                    )}

                </div>


                <button
                    onClick={() =>
                        logout({
                            logoutParams: {
                                returnTo:
                                    window.location.origin
                            }
                        })
                    }
                    style={{
                        padding: "8px 15px",
                        border: "none",
                        borderRadius: "6px",
                        cursor: "pointer"
                    }}
                >

                    Logout

                </button>

            </div>


            {/* AUTH ERROR */}

            {authError && (

                <div
                    style={{
                        margin: "10px 25px",
                        padding: "12px",
                        background: "#ffe5e5",
                        color: "#b00020",
                        borderRadius: "6px"
                    }}
                >

                    {authError}

                </div>

            )}


            {/* DASHBOARD STATS */}

            <section className="stats-grid">

                <StatCard
                    title="User ID"
                    value={dashboard.user_id}
                />

                <StatCard
                    title="Total Posts"
                    value={dashboard.total_posts}
                />

                <StatCard
                    title="Total Comments"
                    value={dashboard.total_comments}
                />

                <StatCard
                    title="Total Likes"
                    value={
                        dashboard.total_likes_received
                    }
                />

            </section>


            {/* CHARTS */}

            {loading ? (

                <div className="loading">

                    Loading dashboard...

                </div>

            ) : (

                <Charts
                    posts={
                        dashboard.posts || []
                    }
                />

            )}


            {/* NOTIFICATIONS */}

            <Notifications
                notifications={
                    notifications
                }
                setNotifications={
                    setNotifications
                }
            />


            {/* AI SUPPORT */}

            <AISupport />

        </div>

    );
}

export default App;