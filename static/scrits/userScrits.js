const expenses = document.getElementById('expenses');
const ratio = document.getElementById('ratio');
const income = document.getElementById('income');

function expensesLineChart(labelsData, moneyData) {
    new Chart(expenses, {
      type: 'line',
      data: {
        labels: labelsData,
        datasets: [{
          label: 'Расходы',
          data: moneyData,
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
}


function ratioChart(proportionsOfMoney){
    new Chart(ratio, {
        type: 'doughnut',
        data: {
            labels: [
                'Расходы',
                'Доходы'
            ],
            datasets: [{
                label: 'My First Dataset',
                data: proportionsOfMoney,
                backgroundColor: [
                'rgb(247, 106, 106)',
                'rgb(255, 132, 0)'
                ],
                hoverOffset: 4
            }]
        }
        }
    );
}


function incomeLineChart(labelsData, moneyData){
    new Chart(income, {
        type: 'line',
        data: {
        labels: labelsData,
        datasets: [{
            label: 'Доходы',
            data: moneyData,
            borderWidth: 1
        }]
        },
        options: {
        scales: {
            y: {
            beginAtZero: true
            }
        }
        }
    });
}
