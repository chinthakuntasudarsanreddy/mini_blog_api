function Notifications({ notifications = [] }) {
  // Make sure notifications is always an array
  const notificationList = Array.isArray(notifications)
    ? notifications
    : Array.isArray(notifications?.notifications)
      ? notifications.notifications
      : Array.isArray(notifications?.data)
        ? notifications.data
        : [];

  return (
    <div className="notifications-card">
      <div className="card-header">
        <h3>Notifications</h3>
        <span>{notificationList.length}</span>
      </div>

      {notificationList.length === 0 ? (
        <p className="empty-message">
          No notifications yet.
        </p>
      ) : (
        <div className="notifications-list">
          {notificationList.map((notification, index) => (
            <div
              className="notification-item"
              key={notification.id || index}
            >
              <div className="notification-icon">
                🔔
              </div>

              <div className="notification-content">
                <strong>
                  {notification.title || "Notification"}
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Notifications;