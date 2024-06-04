let heads;
let tails;
let secret;
let coin = document.querySelector('.coin');
let flipBtn = document.getElementById('flip-button');
let resetBtn = document.getElementById('reset-button');

async function updateStats(){
    heads = await (await fetch('/heads/', { method: 'GET' })).text();
    tails = await (await fetch('/tails/', { method: 'GET' })).text();
}

function updateStatsOnPage(){
    document.getElementById('heads-count').textContent = `Face : ${heads}`;
    document.getElementById('tails-count').textContent = `Pile : ${tails}`;
}

async function updateSecret() {
    secret = await (await fetch('/secret/', { method: 'GET' })).text();

    // Check the condition and display the secret message if met
    if (parseInt(tails) === 1 && parseInt(heads) === 2) {
        document.getElementById('secret-message').textContent = `Mon secret est ${secret}`;
    } else {
        document.getElementById('secret-message').textContent = "";
    }
}

function disableButton() {
    flipBtn.disabled = true;
    setTimeout(()=>{
        flipBtn.disabled = false;
    }, 3000);
}

flipBtn.addEventListener("click", async ()=>{
    let i = Math.floor(Math.random() * 2);
    coin.style.animation = "none";
    if (i) {
        setTimeout(()=>{
            coin.style.animation = "spin-heads 3s forwards";
        }, 100);
        await (await fetch('/heads/', { method: 'POST' })).text();
    }else{
        setTimeout(()=>{
            coin.style.animation = "spin-tails 3s forwards";
        }, 100);
        await (await fetch('/tails/', { method: 'POST' })).text();
    }
    updateStats();
    setTimeout(updateStatsOnPage, 3000);
    setTimeout(updateSecret, 3000);
    disableButton();
});

resetBtn.addEventListener("click", async ()=>{
    coin.style.animation = "none";

    // Reset the counters in the database via API & on page
    await fetch('/reset/', { method: 'POST' });
    await updateStats();
    updateStatsOnPage();
    updateSecret();
});

(async () => {
    await updateStats();
    updateStatsOnPage();
    updateSecret();
})();
