document.addEventListener("DOMContentLoaded", function () {
  // Connect to Socket.IO server
  var myLineChart;
  var canvas = document.getElementById("myLineChart");
  var ctxLine = canvas.getContext("2d");
  var socket = io.connect("http://localhost:5000");

  // Use the socket to listen for the 'update_line_chart' event
  socket.on("update_data", function (data) {
    console.log("Received data:", data);

    if (data.data) {
      // Fungsi untuk mengupdate nilai elemen
      function updateNilaiElement(id, index) {
        var element = document.getElementById(id);
        if (element) {
          element.innerText = data.data[index];
        } else {
          console.error("Element with ID", id, "not found.");
        }
      }

      // Memanggil fungsi update untuk setiap elemen
      updateNilaiElement("nilaiKetinggian", 0);
      updateNilaiElement("suhuKandang", 1);
      updateNilaiElement("kelembabanKandang", 2);
      updateNilaiElement("intensitasCahaya", 3);
    } else {
      console.error("Invalid or empty dataSensor array:", data.data);
    }

    if (myLineChart) {
      myLineChart.destroy();
    }

    myLineChart = new Chart(ctxLine, {
      type: "line",
      data: {
        labels: data.labels, // Ensure labels is an array
        datasets: [
          {
            label: "Ultrasonik",
            data: data.data.map((item) => item[0]), // Index 0 (Ultrasonik)
            fill: false,
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 2,
          },
          {
            label: "Suhu",
            data: data.data.map((item) => item[1]), // Index 1 (Suhu)
            fill: false,
            borderColor: "rgba(255, 0, 0, 1)",
            borderWidth: 2,
          },
          {
            label: "Kelembaban",
            data: data.data.map((item) => item[2]), // Index 2 (Kelembaban)
            fill: false,
            borderColor: "rgba(0, 255, 0, 1)",
            borderWidth: 2,
          },
          {
            label: "LDR",
            data: data.data.map((item) => item[3]), // Index 3 (LDR)
            fill: false,
            borderColor: "rgba(255, 255, 0, 1)",
            borderWidth: 2,
          },
        ],
      },
      options: {
        scales: {
          x: {
            type: "time",
            time: {
              unit: "month",
            },
          },
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
});
