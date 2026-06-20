const button = document.getElementById("weather-btn");

button.addEventListener("click", loadWeather);

async function loadWeather() {

    const response =
        await fetch("/weather/zurich");

    const data =
        await response.json();

    document.getElementById(
        "weather-output"
    ).innerText =
        JSON.stringify(data, null, 2);
}
