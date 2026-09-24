
import { useEffect, useState } from "react";
import AISupport from "./components/AISupport";
import Header from "./components/Header";
import StatCard from "./components/StatCard";
import Charts from "./components/Charts";
import Notifications from "./components/Notifications";

import {
    getDashboardData,
    getNotifications
} from "./api/api";


function App() {

    const [dashboard, setDashboard] = useState({
        user_id: 0,
        total_posts: 0,
        total_comments: 0,
        total_likes_received: 0,
        posts: []
    });

    const [notifications, setNotifications] = useState([]);

    const [loading, setLoading] = useState(true);


    async function loadDashboard() {

        try {

            setLoading(true);

            const data =
                await getDashboardData();

            setDashboard(data);


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


    useEffect(() => {

        loadDashboard();

    }, []);


    return (

        <div className="dashboard">

            <Header
                onRefresh={loadDashboard}
            />


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


            <Notifications
                notifications={
                    notifications
                }

                setNotifications={
                    setNotifications
                }

            />


            {/* AI SUPPORT CHAT */}

            <AISupport />


        </div>

    );

}


export default App;
