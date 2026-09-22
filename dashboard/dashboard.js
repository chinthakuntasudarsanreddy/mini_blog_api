const API_URL = "http://127.0.0.1:8000";

let postsChart = null;
let engagementChart = null;
let userPostsChart = null;
let subscriptionChart = null;
 /*                                                                         
 -------------------------------------------------------------------------- 
 Load Dashboard                                                             
-------------------------------------------------------------------------- 
 */                                                                         

async function loadDashboard() {


const status = document.getElementById("dashboardStatus");

try {

    status.textContent = "Loading dashboard...";

    /*
     * The API uses JWT authentication.
     *
     * For now, the token is read from localStorage.
     * Make sure your login code stores the access token as:
     *
     * localStorage.setItem("access_token", token);
     */

   const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    localStorage.getItem("accessToken");

    if (!token) {
        status.textContent =
            "Please login first. Access token not found.";
        return;
    }

    const response = await fetch(
        `${API_URL}/user/dashboard`,
        {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    if (!response.ok) {

        if (response.status === 401) {
            throw new Error("Unauthorized. Please login again.");
        }

        throw new Error(
            `Dashboard API failed: ${response.status}`
        );
    }

    const data = await response.json();

    console.log("Dashboard API response:", data);

    updateStatistics(data);

    createPostsChart(data);
    createEngagementChart(data);
    createUserPostsChart(data);

    status.textContent = "Dashboard loaded successfully.";

} catch (error) {

    console.error("Dashboard error:", error);

    status.textContent = error.message;
}


}

 /*                                                                         
 -------------------------------------------------------------------------- 
 Load Dashboard                                                             
-------------------------------------------------------------------------- 
 */                                                                         

function updateStatistics(data) {


document.getElementById("totalUsers").textContent =
    data.user_id ?? 0;

document.getElementById("totalPosts").textContent =
    data.total_posts ?? 0;

document.getElementById("totalComments").textContent =
    data.total_comments ?? 0;

document.getElementById("totalLikes").textContent =
    data.total_likes ?? 0;


}

 /*                                                                         
 -------------------------------------------------------------------------- 
 Posts Chart                                                                
 -------------------------------------------------------------------------- 
 */                                                                         

function createPostsChart(data) {


const posts = data.posts || [];

const labels = posts.map(post =>
    post.title || `Post ${post.post_id}`
);

const values = posts.map(post =>
    post.likes ?? 0
);

if (postsChart) {
    postsChart.destroy();
}

const ctx =
    document.getElementById("postsChart");

postsChart = new Chart(ctx, {

    type: "bar",

    data: {
        labels: labels,

        datasets: [
            {
                label: "Likes",
                data: values
            }
        ]
    },

    options: {
        responsive: true,

        maintainAspectRatio: false,

        plugins: {
            legend: {
                display: true
            }
        },

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});


}

 /*                                                                         
 -------------------------------------------------------------------------- 
 Engagement Chart                                                           
 -------------------------------------------------------------------------- 
 */                                                                         

function createEngagementChart(data) {


const posts = data.posts || [];

const totalLikes = posts.reduce(
    (sum, post) => sum + (post.likes || 0),
    0
);

const totalComments = posts.reduce(
    (sum, post) => sum + (post.comments || 0),
    0
);

const totalViews = posts.reduce(
    (sum, post) => sum + (post.views || 0),
    0
);

if (engagementChart) {
    engagementChart.destroy();
}

const ctx =
    document.getElementById("engagementChart");

engagementChart = new Chart(ctx, {

    type: "doughnut",

    data: {

        labels: [
            "Likes",
            "Comments",
            "Views"
        ],

        datasets: [
            {
                label: "Engagement",
                data: [
                    totalLikes,
                    totalComments,
                    totalViews
                ]
            }
        ]
    },

    options: {
        responsive: true,

        maintainAspectRatio: false,

        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }
});


}

 /*                                                                         
 -------------------------------------------------------------------------- 
 Posts by User Chart                                                        
 -------------------------------------------------------------------------- 
 */                                                                         

function createUserPostsChart(data) {


const posts = data.posts || [];

const labels = posts.map(post =>
    post.title || `Post ${post.post_id}`
);

const values = posts.map(() =>
    1
);

if (userPostsChart) {
    userPostsChart.destroy();
}

const ctx =
    document.getElementById("userPostsChart");

userPostsChart = new Chart(ctx, {

    type: "line",

    data: {

        labels: labels,

        datasets: [
            {
                label: "Posts",
                data: values,

                tension: 0.3,

                fill: false
            }
        ]
    },

    options: {

        responsive: true,

        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
});


}

 /*                                                                         
 -------------------------------------------------------------------------- 
 Refresh Button                                                             
 -------------------------------------------------------------------------- 
 */                                                                         

document
.getElementById("refreshBtn")
.addEventListener(
"click",
loadDashboard
);
 /*                                                                         
 -------------------------------------------------------------------------- 
 Initial Load                                                               
 -------------------------------------------------------------------------- 
 */                                                                         

loadDashboard();
