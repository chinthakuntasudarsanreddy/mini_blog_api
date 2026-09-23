
// ============================================================
// MINI BLOG - ANALYTICS DASHBOARD
// ============================================================

const API_URL = "http://127.0.0.1:8000";

// Store Chart.js instances so they can be destroyed before
// creating a new chart.
let likesChart = null;
let commentsChart = null;
let viewsChart = null;
let subscriptionChart = null;


// ============================================================
// GET ACCESS TOKEN
// ============================================================

function getAccessToken() {
    return localStorage.getItem("access_token");
}


// ============================================================
// UPDATE STATISTICS CARDS
// ============================================================

function updateStatistics(data) {

    console.log("Updating dashboard statistics:", data);

    const userId = document.getElementById("userId");
    const totalPosts = document.getElementById("totalPosts");
    const totalComments = document.getElementById("totalComments");
    const totalLikes = document.getElementById("totalLikes");

    if (userId) {
        userId.textContent = data.user_id ?? 0;
    }

    if (totalPosts) {
        totalPosts.textContent = data.total_posts ?? 0;
    }

    if (totalComments) {
        totalComments.textContent = data.total_comments ?? 0;
    }

    if (totalLikes) {
        totalLikes.textContent = data.total_likes_received ?? 0;
    }
}


// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

async function loadDashboard() {

    try {

        const token = getAccessToken();

        if (!token) {
            throw new Error(
                "Access token not found. Please login again."
            );
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

            const errorText = await response.text();

            throw new Error(
                errorText || `HTTP ${response.status}`
            );
        }


        const data = await response.json();


        console.log(
            "Dashboard API response:",
            data
        );


        // Update cards
        updateStatistics(data);


        // Posts array
        const posts = Array.isArray(data.posts)
            ? data.posts
            : [];


        // Create charts
        createLikesChart(posts);
        createCommentsChart(posts);
        createViewsChart(posts);


        // Load notifications
        await loadNotifications();

    }

    catch (error) {

        console.error(
            "Dashboard error:",
            error
        );
    }
}


// ============================================================
// LIKES BY POST CHART
// ============================================================

function createLikesChart(posts) {

    const canvas = document.getElementById(
        "postsChart"
    );

    if (!canvas) {
        console.warn(
            "postsChart canvas not found."
        );
        return;
    }


    const labels = posts.map(
        post => post.title || `Post ${post.post_id}`
    );


    const likes = posts.map(
        post => post.likes ?? 0
    );


    if (likesChart) {
        likesChart.destroy();
    }


    likesChart = new Chart(
        canvas,
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Likes",

                        data: likes,

                        borderWidth: 1
                    }
                ]
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true
                    },

                    title: {
                        display: true,

                        text: "Likes by Post"
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        }
    );
}


// ============================================================
// COMMENTS BY POST CHART
// ============================================================

function createCommentsChart(posts) {

    const canvas = document.getElementById(
        "engagementChart"
    );

    if (!canvas) {
        console.warn(
            "engagementChart canvas not found."
        );
        return;
    }


    const labels = posts.map(
        post => post.title || `Post ${post.post_id}`
    );


    const comments = posts.map(
        post => post.comments ?? 0
    );


    if (commentsChart) {
        commentsChart.destroy();
    }


    commentsChart = new Chart(
        canvas,
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Comments",

                        data: comments,

                        borderWidth: 1
                    }
                ]
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true
                    },

                    title: {
                        display: true,

                        text: "Comments by Post"
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        }
    );
}


// ============================================================
// VIEWS BY POST CHART
// ============================================================

function createViewsChart(posts) {

    const canvas = document.getElementById(
        "userPostsChart"
    );

    if (!canvas) {
        console.warn(
            "userPostsChart canvas not found."
        );
        return;
    }


    const labels = posts.map(
        post => post.title || `Post ${post.post_id}`
    );


    const views = posts.map(
        post => post.views ?? 0
    );


    if (viewsChart) {
        viewsChart.destroy();
    }


    viewsChart = new Chart(
        canvas,
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Views",

                        data: views,

                        borderWidth: 2,

                        tension: 0.3,

                        fill: false
                    }
                ]
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true
                    },

                    title: {
                        display: true,

                        text: "Views by Post"
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        }
    );
}


// ============================================================
// NOTIFICATIONS
// ============================================================

async function loadNotifications() {

    try {

        const token = getAccessToken();

        if (!token) {
            return;
        }


        const response = await fetch(
            `${API_URL}/notifications`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            }
        );


        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                errorText || `HTTP ${response.status}`
            );
        }


        const data = await response.json();


        console.log(
            "Notifications API response:",
            data
        );


        renderNotifications(data);

    }

    catch (error) {

        console.error(
            "Notifications error:",
            error
        );
    }
}


// ============================================================
// RENDER NOTIFICATIONS
// ============================================================

function renderNotifications(data) {

    const notificationList =
        document.getElementById(
            "notificationList"
        );


    const notificationBadge =
        document.getElementById(
            "notificationBadge"
        );


    if (notificationBadge) {

        notificationBadge.textContent =
            data.unread_count ?? 0;
    }


    if (!notificationList) {
        return;
    }


    const notifications =
        Array.isArray(data.notifications)
            ? data.notifications
            : [];


    if (notifications.length === 0) {

        notificationList.innerHTML = `
            <div class="empty-notifications">
                🔔 No notifications yet.
            </div>
        `;

        return;
    }


    notificationList.innerHTML =
        notifications
            .map(notification => {

                const unreadClass =
                    notification.is_read
                        ? ""
                        : "unread";


                const date =
                    formatDate(
                        notification.created_at
                    );


                return `
                    <div
                        class="notification-item ${unreadClass}"
                        data-id="${notification.id}"
                    >

                        <div class="notification-message">
                            ${escapeHtml(
                                notification.message
                            )}
                        </div>

                        <div class="notification-type">
                            ${escapeHtml(
                                notification.notification_type || ""
                            )}
                        </div>

                        <div class="notification-date">
                            ${date}
                        </div>

                        ${
                            notification.is_read
                            ? ""
                            : `
                                <button
                                    class="mark-read-btn"
                                    onclick="markNotificationRead(${notification.id})"
                                >
                                    Mark as read
                                </button>
                            `
                        }

                    </div>
                `;
            })
            .join("");
}


// ============================================================
// MARK ONE NOTIFICATION AS READ
// ============================================================

async function markNotificationRead(
    notificationId
) {

    try {

        const token = getAccessToken();

        if (!token) {
            return;
        }


        const response = await fetch(
            `${API_URL}/notifications/${notificationId}/read`,
            {
                method: "PATCH",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            }
        );


        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                errorText || `HTTP ${response.status}`
            );
        }


        await loadNotifications();

    }

    catch (error) {

        console.error(
            "Mark notification read error:",
            error
        );
    }
}


// ============================================================
// MARK ALL NOTIFICATIONS AS READ
// ============================================================

async function markAllNotificationsRead() {

    try {

        const token = getAccessToken();

        if (!token) {
            return;
        }


        const response = await fetch(
            `${API_URL}/notifications/read-all`,
            {
                method: "PATCH",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            }
        );


        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                errorText || `HTTP ${response.status}`
            );
        }


        await loadNotifications();

    }

    catch (error) {

        console.error(
            "Mark all notifications error:",
            error
        );
    }
}


// ============================================================
// FORMAT DATE
// ============================================================

function formatDate(dateString) {

    if (!dateString) {
        return "";
    }


    try {

        const date = new Date(
            dateString
        );


        return date.toLocaleString();

    }

    catch (error) {

        return dateString;
    }
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// REFRESH BUTTON
// ============================================================

function setupRefreshButton() {

    const refreshButton =
        document.getElementById(
            "refreshButton"
        );


    if (!refreshButton) {
        return;
    }


    refreshButton.addEventListener(
        "click",
        async function () {

            refreshButton.disabled = true;

            refreshButton.textContent =
                "Refreshing...";


            await loadDashboard();


            refreshButton.disabled = false;

            refreshButton.textContent =
                "Refresh";
        }
    );
}


// ============================================================
// NOTIFICATION BUTTON
// ============================================================

function setupNotificationButton() {

    const notificationButton =
        document.getElementById(
            "notificationButton"
        );


    const notificationPanel =
        document.getElementById(
            "notificationPanel"
        );


    if (
        !notificationButton ||
        !notificationPanel
    ) {
        return;
    }


    notificationButton.addEventListener(
        "click",
        function () {

            notificationPanel.classList.toggle(
                "show"
            );
        }
    );
}


// ============================================================
// MARK ALL BUTTON
// ============================================================

function setupMarkAllButton() {

    const markAllButton =
        document.getElementById(
            "markAllRead"
        );


    if (!markAllButton) {
        return;
    }


    markAllButton.addEventListener(
        "click",
        markAllNotificationsRead
    );
}


// ============================================================
// INITIALIZE DASHBOARD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Dashboard initialized."
        );


        // Check Chart.js
        if (typeof Chart === "undefined") {

            console.error(
                "Chart.js is not loaded."
            );

        } else {

            console.log(
                "Chart.js version:",
                Chart.version
            );
        }


        setupRefreshButton();

        setupNotificationButton();

        setupMarkAllButton();


        // Load dashboard
        loadDashboard();


        // Refresh notifications every 30 seconds
        setInterval(
            loadNotifications,
            30000
        );
    }
);
