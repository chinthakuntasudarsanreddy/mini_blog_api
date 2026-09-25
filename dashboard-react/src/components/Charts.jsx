import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";

import {
    Bar,
    Line
} from "react-chartjs-2";


ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);


function Charts({ posts }) {

    const labels = posts.map(
        post =>
            post.title ||
            `Post ${post.post_id}`
    );


    // Likes
    const likes = posts.map(
        post =>
            post.likes ?? 0
    );


    // Comments
    const comments = posts.map(
        post =>
            post.comments ?? 0
    );


    // Views
    const views = posts.map(
        post =>
            post.views ?? 0
    );


    // Subscription plans
    const subscriptions = posts.map(
        post =>
            post.subscription_plan ||
            "Basic"
    );


    const subscriptionCounts = subscriptions.reduce(
        (acc, plan) => {

            acc[plan] =
                (acc[plan] || 0) + 1;

            return acc;

        },
        {}
    );


    // Likes chart
    const likesData = {

        labels,

        datasets: [
            {
                label: "Likes",

                data: likes,

                borderWidth: 1
            }
        ]

    };


    // Comments chart
    const commentsData = {

        labels,

        datasets: [
            {
                label: "Comments",

                data: comments,

                borderWidth: 1
            }
        ]

    };


    // Views chart
    const viewsData = {

        labels,

        datasets: [
            {
                label: "Views",

                data: views,

                borderWidth: 2,

                tension: 0.3
            }
        ]

    };


    // Subscription chart
    const subscriptionsData = {

        labels: Object.keys(subscriptionCounts),

        datasets: [
            {
                label: "Subscriptions",

                data: Object.values(subscriptionCounts),

                borderWidth: 2,

                tension: 0.3
            }
        ]

    };


    return (

        <section className="charts-grid">


            {/* Likes */}

            <div className="chart-card">

                <h2>
                    Likes by Post
                </h2>

                <div className="chart-container">

                    <Bar
                        data={likesData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    />

                </div>

            </div>


            {/* Comments */}

            <div className="chart-card">

                <h2>
                    Comments by Post
                </h2>

                <div className="chart-container">

                    <Bar
                        data={commentsData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    />

                </div>

            </div>


            {/* Views */}

            <div className="chart-card">

                <h2>
                    Views
                </h2>

                <div className="chart-container">

                    <Line
                        data={viewsData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    />

                </div>

            </div>


            {/* Subscriptions */}

            <div className="chart-card">

                <h2>
                    Subscription Plans
                </h2>

                <div className="chart-container">

                    <Line
                        data={subscriptionsData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false
                        }}
                    />

                </div>

            </div>


        </section>

    );

}


export default Charts;