document.getElementById('generateBtn').addEventListener('click', generateImage);

async function generateImage() {
  const promptInput = document.getElementById('prompt');
  const prompt = promptInput.value.trim();
  const result = document.getElementById('result');
  const btn = document.getElementById('generateBtn');

  if (!prompt) {
    alert('Bitte gib einen Text ein!');
    return;
  }

  btn.disabled = true;
  result.innerHTML = '<div class="loader"></div>';

  try {
    const response = await fetch("http://localhost:3000/generate-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await response.json();

    if (data.imageUrl) {
      result.innerHTML = `<img src="${data.imageUrl}" alt="Generiertes Bild" />`;
    } else {
      result.innerHTML = `<p style="color: red;">Fehler: ${data.error}</p>`;
    }
  } catch (error) {
    result.innerHTML = `<p style="color: red;">Fehler bei der Verbindung zum Server.</p>`;
  } finally {
    btn.disabled = false;
  }
}
document.getElementById('generateBtn').addEventListener('click', generateImage);

async function generateImage() {
  const promptInput = document.getElementById('prompt');
  const prompt = promptInput.value.trim();
  const result = document.getElementById('result');
  const btn = document.getElementById('generateBtn');

  if (!prompt) {
    alert('Bitte gib einen Text ein!');
    return;
  }

  btn.disabled = true;
  result.innerHTML = '<div class="loader"></div>';

  try {
    const response = await fetch("http://localhost:3000/generate-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await response.json();

    if (data.imageUrl) {
      result.innerHTML = `<img src="${data.imageUrl}" alt="Generiertes Bild" />`;
    } else {
      result.innerHTML = `<p style="color: red;">Fehler: ${data.error}</p>`;
    }
  } catch (error) {
    result.innerHTML = `<p style="color: red;">Fehler bei der Verbindung zum Server.</p>`;
  } finally {
    btn.disabled = false;
  }
}
