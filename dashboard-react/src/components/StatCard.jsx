function StatCard({
    title,
    value
}) {

    return (

        <div className="stat-card">

            <h3>
                {title}
            </h3>

            <p>
                {value ?? 0}
            </p>

        </div>

    );

}


export default StatCard;