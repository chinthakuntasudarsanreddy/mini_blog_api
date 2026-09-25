
import { useState } from "react";

function Notifications({ notifications = [] }) {

    const [isOpen, setIsOpen] = useState(false);

    // Always make sure notifications is an array
    const notificationList =
        Array.isArray(notifications)
            ? notifications
            : Array.isArray(notifications?.notifications)
                ? notifications.notifications
                : Array.isArray(notifications?.data)
                    ? notifications.data
                    : [];


    // Count only unread notifications
    const unreadCount = notificationList.filter(
        notification => !notification.is_read
    ).length;


    const getIcon = (type) => {

        switch (type) {

            case "like":
                return "❤️";

            case "comment":
                return "💬";

            case "subscription":
                return "⭐";

            default:
                return "🔔";
        }
    };


    const markAllAsRead = () => {

        // UI only for now
        // API can be connected later

        console.log("Mark all notifications as read");
    };


    return (

        <div className="notification-wrapper">


            {/* =========================
                BELL BUTTON
            ========================= */}

            <button
                className="notification-btn"
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Notifications"
            >

                🔔


                {/* Unread Badge */}

                {unreadCount > 0 && (

                    <span className="notification-badge">

                        {unreadCount > 99
                            ? "99+"
                            : unreadCount}

                    </span>

                )}

            </button>


            {/* =========================
                DROPDOWN
            ========================= */}

            {isOpen && (

                <div className="notifications-card">


                    {/* Header */}

                    <div className="notification-header">

                        <div>

                            <h3>
                                Notifications
                            </h3>

                            <p>
                                {unreadCount > 0
                                    ? `${unreadCount} unread notification${unreadCount > 1 ? "s" : ""}`
                                    : "You're all caught up"}
                            </p>

                        </div>


                        {unreadCount > 0 && (

                            <button
                                className="mark-read-btn"
                                onClick={markAllAsRead}
                            >
                                Mark all as read
                            </button>

                        )}

                    </div>


                    {/* Notifications */}

                    {notificationList.length === 0 ? (

                        <div className="empty-notifications">

                            <div className="empty-bell">
                                🔔
                            </div>

                            <h4>
                                No notifications
                            </h4>

                            <p>
                                You're all caught up!
                            </p>

                        </div>

                    ) : (

                        <div className="notifications-list">

                            {notificationList.map(
                                (notification, index) => {

                                    const unread =
                                        !notification.is_read;

                                    return (

                                        <div
                                            key={
                                                notification.id ||
                                                index
                                            }

                                            className={`notification-item ${
                                                unread
                                                    ? "unread"
                                                    : ""
                                            }`}
                                        >


                                            {/* Icon */}

                                            <div className="notification-icon">

                                                {getIcon(
                                                    notification.notification_type
                                                )}

                                            </div>


                                            {/* Content */}

                                            <div className="notification-content">

                                                <strong>

                                                    {notification.title ||
                                                        notification.notification_type ||
                                                        "Notification"}

                                                </strong>


                                                <p>

                                                    {notification.message ||
                                                        notification.text ||
                                                        "You have a new notification."}

                                                </p>


                                                {notification.created_at && (

                                                    <small>

                                                        {new Date(
                                                            notification.created_at
                                                        ).toLocaleString()}

                                                    </small>

                                                )}

                                            </div>


                                            {/* Unread dot */}

                                            {unread && (

                                                <span className="unread-dot">
                                                </span>

                                            )}

                                        </div>

                                    );
                                }
                            )}

                        </div>

                    )}

                </div>

            )}

        </div>
    );
}

export default Notifications;
