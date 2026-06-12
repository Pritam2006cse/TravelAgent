async function generatePlan() {

    const prompt =
        document.getElementById("prompt").value;

    const status =
        document.getElementById("status");

    const logs =
        document.getElementById("logs");

    const itinerary =
        document.getElementById("itinerary");

    status.innerHTML = "Running swarm...";
    logs.innerHTML = "";
    itinerary.innerHTML = "";

    try {

        const response =
            await fetch(
                "http://localhost:8000/run-swarm",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":
                        "application/json"
                    },
                    body:JSON.stringify({
                        user_prompt:prompt
                    })
                }
            );

        const data =
            await response.json();

        status.innerHTML =
            data.is_validated
            ? "<h3 class='success'>✅ Validated</h3>"
            : "<h3 class='error'>❌ Validation Failed</h3>";

        logs.innerHTML =
            "<div class='card'><h2>Agent Logs</h2></div>";

        data.agent_logs.forEach(log => {

            logs.innerHTML +=
            `<div class='card'>${log}</div>`;

        });

        itinerary.innerHTML =
            "<h2>Final Itinerary</h2>";

        data.current_itinerary.forEach(leg => {

            itinerary.innerHTML += `
            <div class="card">

                <h3>
                    ${leg.type.toUpperCase()}
                </h3>

                <p>
                    ${leg.operator}
                </p>

                <p>
                    ${
                        leg.type === "flight"
                        ? `Flight No: ${leg.identification_number}`
                        : `Train No: ${leg.identification_number}`
                    }
                </p>
                ${leg.flight_name ? `
                <p>
                    Flight:
                    ${leg.flight_name}
                </p>
                ` : ""}

                ${leg.train_name ? `
                <p>
                    Train:
                    ${leg.train_name}
                </p>
                ` : ""}
                <p>
                    ${leg.from_location}
                    →
                    ${leg.to_location}
                </p>

                <p>
                    Departure:
                    ${leg.departure_date}
                    ${leg.departure_time}
                </p>

                <p>
                    Arrival:
                    ${leg.arrival_date}
                    ${leg.arrival_time}
                </p>

                <p>
                    Status:
                    ${leg.status}
                </p>

            </div>
            `;
        });

    }
    catch(err){

        status.innerHTML =
            "<h3 class='error'>Backend Offline</h3>";

        console.error(err);
    }
}