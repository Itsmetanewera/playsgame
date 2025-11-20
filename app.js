// web/app.js
const log = msg => {
  const el = document.getElementById("log");
  el.innerHTML = `${new Date().toLocaleTimeString()}: ${msg}<br>` + el.innerHTML;
};

const tg = window.Telegram?.WebApp;
if (!tg) {
  log("Warning: Telegram WebApp API not found. Open inside Telegram.");
}

let user = null;
try {
  // initDataUnsafe contains user info if available
  user = tg?.initDataUnsafe?.user || null;
  log("User: " + (user ? `${user.first_name} (${user.id})` : "unknown"));
} catch(e){
  console.error(e);
}

async function apiPost(path, body){
  const resp = await fetch(`/api/${path}`, {
    method: "POST",
    headers: { "Content-Type":"application/json" },
    body: JSON.stringify(body)
  });
  return resp.json();
}

async function refreshBalance(){
  if(!user) return;
  const r = await fetch(`/api/balance/${user.id}`);
  const j = await r.json();
  document.getElementById("bal").innerText = parseFloat(j.balance).toFixed(2);
}

document.getElementById("btn-deposit").addEventListener("click", async ()=>{
  const amount = document.getElementById("amount").value;
  if(!amount) return log("Введите сумму");
  const res = await apiPost("deposit", { user_id: user.id, amount });
  log("deposit: " + JSON.stringify(res));
});

document.getElementById("btn-withdraw").addEventListener("click", async ()=>{
  const amount = document.getElementById("amount").value;
  if(!amount) return log("Введите сумму");
  const res = await apiPost("withdraw", { user_id: user.id, amount });
  log("withdraw: " + JSON.stringify(res));
});

document.getElementById("btn-play").addEventListener("click", async ()=>{
  const bet = document.getElementById("bet").value;
  const n = parseInt(document.getElementById("nballs").value,10);
  if(!bet || !user) return log("Укажите ставку (и откройте в Telegram)");
  // Для простоты — играем локально в фронтенде, а бэкенд делает только депозит/вывод.
  const win_chance = 1/(n+1);
  const multiplier = n * 1.6;
  const roll = Math.random();
  if(roll < win_chance){
    const win = (parseFloat(bet) * multiplier).toFixed(2);
    log(`Вы выиграли ${win} (шанс ${win_chance.toFixed(3)}, бросок ${roll.toFixed(3)})`);
  } else {
    log(`Проиграли (шанс ${win_chance.toFixed(3)}, бросок ${roll.toFixed(3)})`);
  }
});

window.addEventListener("load", () => {
  refreshBalance();
  // Можно вызвать tg.ready() если надо
});
