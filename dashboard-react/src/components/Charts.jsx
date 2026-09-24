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

    const labels =
        posts.map(
            post =>
                post.title ||
                `Post ${post.post_id}`
        );


    const likes =
        posts.map(
            post =>
                post.likes ?? 0
        );


    const comments =
        posts.map(
            post =>
                post.comments ?? 0
        );


    const views =
        posts.map(
            post =>
                post.views ?? 0
        );


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


    return (

        <section className="charts-grid">


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


        </section>

    );

}


export default Charts;