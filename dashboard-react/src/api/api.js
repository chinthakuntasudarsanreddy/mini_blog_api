const API_URL =
    "http://127.0.0.1:8000";


function getAccessToken() {

    return localStorage.getItem(
        "access_token"
    );

}


async function request(
    endpoint,
    options = {}
) {

    const token =
        getAccessToken();


    const response =
        await fetch(
            `${API_URL}${endpoint}`,
            {
                ...options,

                headers: {
                    "Content-Type":
                        "application/json",

                    "Authorization":
                        `Bearer ${token}`,

                    ...(options.headers || {})
                }
            }
        );


    if (!response.ok) {

        const text =
            await response.text();

        throw new Error(
            text ||
            `HTTP ${response.status}`
        );

    }


    return response.json();

}


export async function getDashboardData() {

    return request(
        "/user/dashboard"
    );

}


export async function getNotifications() {

    return request(
        "/notifications"
    );

}


export async function markAllNotificationsRead() {

    return request(
        "/notifications/read-all",
        {
            method: "PUT"
        }
    );

}