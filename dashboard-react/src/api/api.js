
const API_URL =
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


function getAccessToken() {
    return localStorage.getItem("access_token");
}


async function request(endpoint, options = {}) {

    const token = getAccessToken();

    if (!token) {
        throw new Error(
            "Authentication token is missing."
        );
    }


    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,

            headers: {
                "Content-Type": "application/json",

                "Authorization":
                    `Bearer ${token}`,

                ...(options.headers || {})
            }
        }
    );


    const responseText =
        await response.text();


    if (!response.ok) {

        console.error(
            `API Error ${response.status}:`,
            responseText
        );

        throw new Error(
            responseText ||
            `Backend returned HTTP ${response.status}`
        );

    }


    try {

        return JSON.parse(
            responseText
        );

    } catch {

        return responseText;

    }

}


/*
 * Dashboard
 */
export async function getDashboardData() {

    return request(
        "/user/dashboard"
    );

}


/*
 * Notifications
 */
export async function getNotifications() {

    return request(
        "/notifications"
    );

}


/*
 * Mark all notifications as read
 */
export async function markAllNotificationsRead() {

    return request(
        "/notifications/read-all",
        {
            method: "PUT"
        }
    );

}