import { useState } from "react";

import Notifications from "./Notifications";


function Header({ onRefresh }) {

    const [showNotifications, setShowNotifications] =
        useState(false);


    return (

        <header className="dashboard-header">

            <div>

                <h1>
                    Blog Analytics Dashboard
                </h1>

                <p>
                    Overview of your Mini Blog API
                </p>

            </div>


            <div className="header-actions">

                <button
                    className="notification-btn"
                    onClick={() =>
                        setShowNotifications(
                            !showNotifications
                        )
                    }
                >
                    🔔
                </button>


                <button
                    onClick={onRefresh}
                    className="refresh-btn"
                >
                    Refresh
                </button>

            </div>

        </header>

    );

}


export default Header;