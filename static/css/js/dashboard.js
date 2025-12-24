document.addEventListener("DOMContentLoaded", function () {
  if (typeof Chart === "undefined") {
    console.error("Chart.js belum ter-load");
    return;
  }

  const labelsMerk = window.labelsMerk || [];
  const jumlahMerk = window.jumlahMerk || [];

  console.log(labelsMerk, jumlahMerk); // DEBUG

  const canvas = document.getElementById("chartMerk");
  if (!canvas || labelsMerk.length === 0) return;

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: labelsMerk,
      datasets: [
        {
          label: "Jumlah Laptop per Merk",
          data: jumlahMerk,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
    },
  });
});
