(() => {
  "use strict";

  const DEFAULT_REFERRER = "Vanda Silva";
  const params = new URLSearchParams(window.location.search);
  const initialReferrer = cleanName(params.get("indicado_por")) || DEFAULT_REFERRER;

  const form = document.getElementById("registration-form");
  const formCard = document.getElementById("form-card");
  const resultCard = document.getElementById("result-card");
  const errorBox = document.getElementById("form-error");
  const referrerInput = document.getElementById("referrer-name");
  referrerInput.value = initialReferrer;

  let registration = null;

  function cleanName(value) {
    return String(value || "").replace(/[<>\r\n]/g, " ").replace(/\s+/g, " ").trim().slice(0, 100);
  }

  function onlyDigits(value) {
    return String(value || "").replace(/\D/g, "");
  }

  function formatCPF(value) {
    const digits = onlyDigits(value).slice(0, 11);
    return digits.replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  }

  function formatPhone(value) {
    const digits = onlyDigits(value).slice(0, 11);
    if (digits.length <= 10) return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{4})(\d)/, "$1-$2");
    return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{5})(\d)/, "$1-$2");
  }

  function validCPF(value) {
    const cpf = onlyDigits(value);
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
    let sum = 0;
    for (let i = 0; i < 9; i++) sum += Number(cpf[i]) * (10 - i);
    let digit = (sum * 10) % 11;
    if (digit === 10) digit = 0;
    if (digit !== Number(cpf[9])) return false;
    sum = 0;
    for (let i = 0; i < 10; i++) sum += Number(cpf[i]) * (11 - i);
    digit = (sum * 10) % 11;
    if (digit === 10) digit = 0;
    return digit === Number(cpf[10]);
  }

  function dateBR(value) {
    if (!value) return "";
    const [year, month, day] = value.split("-");
    return `${day}/${month}/${year}`;
  }

  function currentBaseUrl() {
    return `${window.location.origin}${window.location.pathname}`;
  }

  function referralLink(name) {
    return `${currentBaseUrl()}?indicado_por=${encodeURIComponent(name)}`;
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function collect() {
    const data = Object.fromEntries(new FormData(form).entries());
    data.indicadoPor = cleanName(referrerInput.value);
    data.nome = cleanName(data.nome);
    data.titulo = onlyDigits(data.titulo);
    data.zona = onlyDigits(data.zona);
    data.secao = onlyDigits(data.secao);
    data.cpf = onlyDigits(data.cpf);
    data.celular = onlyDigits(data.celular);
    data.endereco = String(data.endereco || "").replace(/[<>\r\n]/g, " ").replace(/\s+/g, " ").trim();
    return data;
  }

  function validate(data) {
    if (!data.indicadoPor) return "Digite o nome de quem indicou você.";
    if (!data.nome || !data.titulo || !data.zona || !data.secao || !data.endereco || !data.nascimento || !data.cpf || !data.celular) return "Preencha todos os campos da ficha.";
    if (data.nome.split(" ").length < 2) return "Digite o nome completo.";
    if (!validCPF(data.cpf)) return "Confira o CPF. Ele parece estar incorreto.";
    if (data.celular.length < 10 || data.celular.length > 11) return "Digite um celular válido com DDD.";
    if (!document.getElementById("consentimento").checked) return "Marque a autorização para continuar.";
    return "";
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    const data = collect();
    const error = validate(data);
    if (error) return showError(error);
    registration = data;
    formCard.hidden = true;
    resultCard.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  document.getElementById("cpf").addEventListener("input", (event) => { event.target.value = formatCPF(event.target.value); });
  document.getElementById("celular").addEventListener("input", (event) => { event.target.value = formatPhone(event.target.value); });

  document.getElementById("share-referral").addEventListener("click", async () => {
    if (!registration) return;
    const link = referralLink(registration.nome);
    const text = `Olá! Preencha esta ficha de cadastro. Você será registrado como indicado por ${registration.nome}.`;
    if (navigator.share) {
      try { await navigator.share({ title: "Ficha de Cadastro", text, url: link }); return; } catch (error) { if (error.name === "AbortError") return; }
    }
    await navigator.clipboard.writeText(`${text}\n${link}`);
    alert("Link copiado. Agora cole e envie no WhatsApp.");
  });

  function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 3) {
    const words = String(text).split(" ");
    let line = "", lines = 0;
    for (const word of words) {
      const test = `${line}${word} `;
      if (ctx.measureText(test).width > maxWidth && line) {
        ctx.fillText(line.trim(), x, y + lines * lineHeight);
        line = `${word} `;
        if (++lines >= maxLines) return y + lines * lineHeight;
      } else line = test;
    }
    ctx.fillText(line.trim(), x, y + lines * lineHeight);
    return y + (lines + 1) * lineHeight;
  }

  function roundedRect(ctx, x, y, width, height, radius, fill, stroke) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
  }

  function drawField(ctx, label, value, x, y, width, height, maxLines = 2) {
    ctx.fillStyle = "#f8fafc";
    ctx.strokeStyle = "#c9d5e2";
    ctx.lineWidth = 2;
    roundedRect(ctx, x, y, width, height, 16, true, true);
    ctx.fillStyle = "#52667b";
    ctx.font = "bold 20px Arial";
    ctx.fillText(label.toUpperCase(), x + 22, y + 32);
    ctx.fillStyle = "#17212b";
    ctx.font = "30px Arial";
    wrapText(ctx, value, x + 22, y + 72, width - 44, 36, maxLines);
  }

  function drawImage(data) {
    const canvas = document.getElementById("card-canvas");
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#eaf1f7";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#ffffff";
    roundedRect(ctx, 36, 36, 1008, 1278, 28, true, false);

    ctx.fillStyle = "#123b68";
    roundedRect(ctx, 36, 36, 1008, 178, 28, true, false);
    ctx.fillRect(36, 150, 1008, 64);

    ctx.fillStyle = "#ffffff";
    roundedRect(ctx, 72, 75, 92, 92, 22, true, false);
    ctx.fillStyle = "#123b68";
    ctx.font = "bold 54px Arial";
    ctx.textAlign = "center";
    ctx.fillText("V", 118, 140);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 48px Arial";
    ctx.fillText("FICHA DE CADASTRO", 590, 115);
    ctx.font = "22px Arial";
    ctx.fillText("CADASTRO CENTRAL • VANDA SILVA", 590, 158);
    ctx.textAlign = "left";

    drawField(ctx, "Indicado por", data.indicadoPor, 72, 246, 936, 112);
    drawField(ctx, "Nome completo", data.nome, 72, 382, 936, 126);
    drawField(ctx, "Nº do título", data.titulo, 72, 532, 500, 112);
    drawField(ctx, "Zona", data.zona, 596, 532, 190, 112);
    drawField(ctx, "Seção", data.secao, 810, 532, 198, 112);
    drawField(ctx, "Endereço completo", data.endereco, 72, 668, 936, 166, 3);
    drawField(ctx, "Data de nascimento", dateBR(data.nascimento), 72, 858, 450, 112);
    drawField(ctx, "CPF", formatCPF(data.cpf), 546, 858, 462, 112);
    drawField(ctx, "Nº celular", formatPhone(data.celular), 72, 994, 936, 112);

    ctx.strokeStyle = "#d5dee8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(72, 1152);
    ctx.lineTo(1008, 1152);
    ctx.stroke();
    ctx.fillStyle = "#123b68";
    ctx.font = "bold 24px Arial";
    ctx.fillText("RECEBIMENTO CENTRAL", 72, 1200);
    ctx.fillStyle = "#52667b";
    ctx.font = "26px Arial";
    ctx.fillText("Vanda Silva • WhatsApp: (85) 92001-3309", 72, 1242);
    return canvas;
  }

  function imageFilename(data) {
    return `ficha-${data.nome.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`;
  }

  function canvasBlob(canvas) {
    return new Promise((resolve) => canvas.toBlob(resolve, "image/png", 1));
  }

  function downloadCanvas(canvas, data) {
    const link = document.createElement("a");
    link.download = imageFilename(data);
    link.href = canvas.toDataURL("image/png");
    link.click();
  }

  document.getElementById("send-whatsapp").addEventListener("click", async () => {
    if (!registration) return;
    const canvas = drawImage(registration);
    const blob = await canvasBlob(canvas);
    const file = new File([blob], imageFilename(registration), { type: "image/png" });

    if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({ title: "Ficha de Cadastro", files: [file] });
        return;
      } catch (error) {
        if (error.name === "AbortError") return;
      }
    }

    downloadCanvas(canvas, registration);
    alert("A ficha foi baixada como imagem. Abra o WhatsApp da Vanda e anexe essa imagem.");
  });

  document.getElementById("download-image").addEventListener("click", () => {
    if (!registration) return;
    const canvas = drawImage(registration);
    downloadCanvas(canvas, registration);
  });

  document.getElementById("edit-form").addEventListener("click", () => {
    resultCard.hidden = true;
    formCard.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();
